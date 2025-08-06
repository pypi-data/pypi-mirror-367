from typing import Any, Sequence, Union
import traceback
from tenacity import (
    retry_if_exception,
    stop_after_attempt,
    Retrying,
    RetryCallState,
)
import dlt
from dlt.common import logger
from dlt.pipeline import Pipeline
from dlt.common.pipeline import LoadInfo
from dlt.pipeline.typing import TPipelineStep
from dlt.pipeline.helpers import retry_load
from .trace_resource import (
    trace_resource,
    write_trace_to_pipeline_storage,
    delete_trace_files,
    TRACES_DIR,
    has_traces,
    get_default_trace_schema_with_name,
)
from .utils import create_retry_policy_description
from .exceptions import RunnerException


DEFAULT_RETRY_NO_RETRY = Retrying(stop=stop_after_attempt(1), reraise=True)


class PipelineRunner:
    def __init__(
        self,
        pipeline: Pipeline,
        run_from_clean_folder: bool = False,
        store_trace_info: Union[bool, Pipeline] = False,
        retry_policy: Retrying = DEFAULT_RETRY_NO_RETRY,
        retry_pipeline_steps: Sequence[TPipelineStep] = ("load",),
    ):
        """
        A runner for a single pipeline with retry capabilities and automatic trace storage.
        Read more on: https://dlthub.com/docs/plus/features/runner

        Args:
            pipeline (Pipeline): The pipeline to be run.
            run_from_clean_folder (bool, optional): If True, wipes the local state of the pipeline
                and syncs to the destination to get latest schema and state. Applies to both data
                and trace pipelines.
            store_trace_info (Union[bool, Pipeline], optional): Controls trace storage behavior.
                If True, creates a default trace pipeline. If a Pipeline instance, uses that for
                trace storage.
            retry_policy (Retrying, optional): The retry policy to use for running the pipeline.
            retry_pipeline_steps (Sequence[TPipelineStep], optional): The steps of the pipeline to
                retry on failure.

        Example:
            >>> pipeline = dlt.pipeline("my_pipeline", destination="duckdb")
            >>> load_info = dlt_plus.runner(
            ...     pipeline=pipeline,
            ...     store_trace_info=True,
            ...     retry_policy=Retrying(
            ...         stop=stop_after_attempt(3),
            ...         wait=wait_exponential(multiplier=2, min=1, max=5),
            ...         reraise=True,
            ...     ),
            ...     retry_pipeline_steps=["load"],
            ... ).run(my_source())


        """
        self.pipeline = pipeline
        logger.info(
            self._format(
                f"PipelineRunner initialized for pipeline: `{pipeline.pipeline_name}`",
                pipeline_name=pipeline.pipeline_name,
            )
        )
        self.trace_pipeline = None
        if isinstance(store_trace_info, Pipeline):
            logger.info(
                self._format(
                    f"Storing trace info enabled: Using provided trace pipeline: "
                    f"{store_trace_info.pipeline_name}"
                )
            )
            self.trace_pipeline = store_trace_info
        elif store_trace_info:
            # derive a default trace pipeline from the main pipeline
            self.trace_pipeline = dlt.pipeline(
                pipeline_name="_trace_" + pipeline.pipeline_name,
                destination=pipeline.destination,
                dataset_name="_trace_" + pipeline.dataset_name,
            )
            logger.info(
                self._format(
                    f"Storing trace info enabled: Using default trace pipeline: "
                    f"`{self.trace_pipeline.pipeline_name}`"
                )
            )
        # for code readability we also define a bool here
        self.store_trace_info = bool(store_trace_info)
        self.run_from_clean_folder = run_from_clean_folder
        self.retry_policy = retry_policy
        self.retry_policy_description = create_retry_policy_description(retry_policy)
        self.retry_pipeline_steps = retry_pipeline_steps

    def run(
        self,
        data: Any = None,
        **kwargs: Any,
    ) -> LoadInfo:
        """
        Run the pipeline with the provided data.

        This method executes a complete pipeline run with several phases:
        1. Pre-load phase: Either wipes local folders (if run_from_clean_folder is True) or
           finalizes any pending loads or traces from previous runs
        2. Execution phase: Runs the pipeline with the provided data
        3. Post-load phase: Saves trace information if storing traces is enabled

        Args:
            data (Any, optional): Data to be processed by the pipeline. Can be any data type
                supported by the pipeline, such as sources, resources, or plain lists,
                generators, etc. Defaults to None.
            **kwargs (Any): Additional keyword arguments to pass to the pipeline's run method.
                Common arguments include table_name, schema_name, write_disposition, etc.

        Returns:
            LoadInfo: Information about the load operation, including load IDs and statistics.

        Behavior:
            - Performs pre-load cleanup or finalization based on configuration.
            - Executes the pipeline with retry capability using the configured retry policy.
            - Stores trace information if enabled.
            - Returns comprehensive load information.

        Example:
            >>> load_info = dlt_plus.runner(pipeline).run(source_data, table_name="my_table")
            >>> print(load_info)
        """
        # ----- pre-load -----
        if self.run_from_clean_folder:
            logger.info(self._format("Running from clean folder. Dropping all local state"))
            self.pipeline.drop()
        else:
            # if there are pending loads or traces, finalize them
            if self.pipeline.has_pending_data or has_traces(self.pipeline):
                target = "Pending data" if self.pipeline.has_pending_data else "Pending traces"
                logger.info(self._format(f"{target} found. Finalizing ..."))
                self.finalize()

        # ----- actual run -----
        # with retry policy
        load_info = self._run(self.pipeline, data, store_trace_info=self.store_trace_info, **kwargs)

        # ----- post-load -----
        if load_info and self.store_trace_info:
            self._run_trace_pipeline(with_retry=True, reraise_exception=True)

        logger.info(
            self._format(
                "Pipeline runner completely done.",
                pipeline_name=self.pipeline.pipeline_name,
            )
        )

        return load_info

    def finalize(self) -> LoadInfo:
        """
        Finalize any pending data operations in the pipeline, with the runner's retry policy.

        This method attempts to load any remaining data from the local working directory
        to the destination. It follows the pipeline's natural flow:
        1. Activates the pipeline
        2. If there are extracted load packages, it normalizes them
        3. If there are normalized load packages, it loads them to the destination

        If the runner is configured to store trace information, it will also store any new or any
        pending existing trace information to the trace pipeline.

        Returns:
            LoadInfo: Information about the load operation if data was loaded, or None if no data
                was pending.

        Raises:
            RunnerException: If run_from_clean_folder is True, as it would conflict with
                finalization by removing data before it can be finalized.


        Example:
            >>> # After an interrupted run, finalize any pending data
            >>> load_info = dlt_plus.runner(pipeline).finalize()
            >>> print(load_info)
        """
        if self.run_from_clean_folder:
            raise RunnerException(
                "Conflicting arguments: run_from_clean_folder would remove any data before "
                "anything can be finalized"
            )
        # finalize with retry
        load_info = self._run(
            self.pipeline,
            None,
            store_trace_info=self.store_trace_info,
            log_description="finalize pipeline",
        )

        # post-finalize:
        if self.store_trace_info and (load_info or has_traces(self.pipeline)):
            target = "finalized data" if load_info else "existing traces"
            logger.info(self._format(f"Loading traces for {target}"))
            self._run_trace_pipeline(reraise_exception=True, with_retry=True)
        return load_info

    def _run(
        self,
        pipeline: Pipeline,
        data: Any = None,
        store_trace_info: bool = False,
        log_description: str = "run",
        **kwargs: Any,
    ) -> LoadInfo:
        """
        Internal method to run a pipeline with retry capability.

        This method handles the actual pipeline execution with the configured retry policy.
        It will attempt to run the pipeline according to the retry policy specified during
        initialization, applying retries only to the pipeline steps specified in
        retry_pipeline_steps.
        """

        def log_and_load_trace_after_failed_attempt(retry_state: RetryCallState) -> None:
            attempt_number = retry_state.attempt_number
            was_last_attempt = retry_state.retry_object.stop(retry_state)
            logger.warning(
                self._format(
                    f"Attempt {attempt_number} to {log_description}"
                    f" failed with exception: {retry_state.outcome.exception()}",
                    pipeline_name=pipeline.pipeline_name,
                )
            )
            if not was_last_attempt:
                exc = retry_state.outcome.exception()
                tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
                logger.info(
                    self._format(
                        f"Stacktrace of the exception:\n{''.join(tb_lines)}",
                        pipeline_name=pipeline.pipeline_name,
                    )
                )

            if store_trace_info:
                logger.info(
                    self._format(
                        f"Storing trace on failed attempt `{attempt_number}` to pipeline storage: "
                        f"`{pipeline._pipeline_storage.storage_path}/{TRACES_DIR}`",
                        pipeline_name=pipeline.pipeline_name,
                    )
                )
                write_trace_to_pipeline_storage(pipeline, name_suffix=f"attempt_{attempt_number}")
                self._run_trace_pipeline(with_retry=False, reraise_exception=False)

            if not was_last_attempt:
                logger.info(self._format("Retrying...", pipeline_name=pipeline.pipeline_name))
            else:
                # log whether or not to reraise the exception
                will_reraise = self.retry_policy.reraise
                logger.info(
                    self._format(
                        f"Max attempts reached."
                        f" Exception {'will' if will_reraise else 'will not'} be reraised.",
                        pipeline_name=pipeline.pipeline_name,
                    )
                )

        retry_with_logging = self.retry_policy.copy(
            retry=retry_if_exception(retry_load(retry_on_pipeline_steps=self.retry_pipeline_steps)),
            after=log_and_load_trace_after_failed_attempt,
        )

        retry_decorator = retry_with_logging.wraps

        @retry_decorator
        def run_with_retry(**kwargs: Any) -> LoadInfo:
            info = pipeline.run(data=data, **kwargs)
            # if here, I assume success
            if info and store_trace_info:
                write_trace_to_pipeline_storage(pipeline)
            return info

        logger.info(
            self._format(
                f"Attempting {log_description} with retry policy: {self.retry_policy_description}",
                pipeline_name=pipeline.pipeline_name,
            )
        )

        load_info = run_with_retry(**kwargs)

        logger.info(
            self._format(
                f"{log_description} completed successfully", pipeline_name=pipeline.pipeline_name
            )
        )
        return load_info

    def _run_trace_pipeline(self, reraise_exception: bool = False, with_retry: bool = True) -> None:
        """
        Internal method to load the most recent pipeline trace to the trace pipeline with retry
        policy applied.

        This method takes all trace-JSON files from the pipeline's working directory,
        and stores them in the destination using the runner's trace pipeline.
        If this succeeds, all trace files are deleted from the pipeline storage.
        """
        traces_found = has_traces(self.pipeline)
        if not traces_found:
            logger.info(self._format("No stored traces found"))
            return
        logger.info(self._format(f"Found `{traces_found}` stored traces"))
        logger.info(
            self._format(
                "Attempt loading stored traces to destination "
                f"`{self.trace_pipeline.destination.destination_name}` "
                f"with trace pipeline `{self.trace_pipeline.pipeline_name}`"
                f"{' with' if with_retry else 'without'} retrying",
            )
        )
        self.trace_pipeline.drop()

        new_schema_name = f"{self.pipeline.pipeline_name}_trace"
        trace_contract = get_default_trace_schema_with_name(name=new_schema_name)

        try:
            if with_retry:
                self._run(
                    pipeline=self.trace_pipeline,
                    data=trace_resource(self.pipeline, table_name=new_schema_name),
                    store_trace_info=False,
                    log_description="load traces",
                    schema=trace_contract,
                )
            else:
                self.trace_pipeline.run(
                    data=trace_resource(self.pipeline, table_name=new_schema_name),
                    schema=trace_contract,
                )
                logger.info(
                    self._format(
                        "Traces loaded successfully",
                        pipeline_name=self.trace_pipeline.pipeline_name,
                    )
                )

            delete_trace_files(self.pipeline)
            logger.info(self._format("Traces deleted from pipeline storage"))
        except Exception as exc:
            logger.error(
                self._format(
                    f"Loading traces failed. Traces remain in pipeline storage for inspection: "
                    f"`{self.pipeline._pipeline_storage.storage_path}/{TRACES_DIR}`. "
                    f"Error: {exc}",
                    pipeline_name=self.trace_pipeline.pipeline_name,
                )
            )
            if reraise_exception:
                logger.error(
                    self._format(
                        "Raising exception after failed trace load",
                        pipeline_name=self.trace_pipeline.pipeline_name,
                    )
                )
                raise exc
            else:
                logger.info(
                    self._format(
                        "Not reraising exception to enable further processing",
                        pipeline_name=self.trace_pipeline.pipeline_name,
                    )
                )

    def _format(self, message: str, pipeline_name: str = None) -> str:
        """Add relevant context to the log message."""
        if pipeline_name is None:
            pipeline_name = self.pipeline.pipeline_name
        return f"{pipeline_name}|{message}"
