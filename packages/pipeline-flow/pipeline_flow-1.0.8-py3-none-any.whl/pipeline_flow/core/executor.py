# Standard Imports
from __future__ import annotations

import asyncio
import logging
from abc import ABCMeta, abstractmethod
from functools import reduce
from typing import TYPE_CHECKING, Any

from pipeline_flow.common.exceptions import (
    ExtractError,
    LoadError,
    TransformError,
    TransformLoadError,
)

# Third Party Imports
# Local Imports
from pipeline_flow.common.utils import async_time_it, sync_time_it
from pipeline_flow.core.models.pipeline import Pipeline, PipelineType

# Type Imports

if TYPE_CHECKING:
    from pipeline_flow.common.type_def import ETLData, ExtractedData, TransformedData
    from pipeline_flow.core.models.phases import (
        ExtractPhase,
        LoadPhase,
        TransformLoadPhase,
        TransformPhase,
    )
    from pipeline_flow.plugins import IPlugin


@sync_time_it
def plugin_sync_executor(plugin: IPlugin, *pipeline_args: Any, **pipeline_kwargs: Any) -> ETLData:  # noqa: ANN401
    logging.info("Executing plugin `%s`", plugin.id)
    result = plugin(*pipeline_args, **pipeline_kwargs)
    logging.info("Finished executing plugin `%s`", plugin.id)
    return result


@async_time_it
async def plugin_async_executor(plugin: IPlugin, *pipeline_args: Any, **pipeline_kwargs: Any) -> ETLData:  # noqa: ANN401
    logging.info("Executing plugin `%s`", plugin.id)
    result = await plugin(*pipeline_args, **pipeline_kwargs)
    logging.info("Finished executing plugin `%s`", plugin.id)
    return result


async def task_group_executor(
    plugins: list[IPlugin],
    *pipeline_args: Any,  # noqa: ANN401
    **pipeline_kwargs: Any,  # noqa: ANN401
) -> dict[str, ETLData]:
    async with asyncio.TaskGroup() as group:
        tasks = {
            plugin.id: group.create_task(plugin_async_executor(plugin, *pipeline_args, **pipeline_kwargs))
            for plugin in plugins
        }

    return {plugin_id: task.result() for plugin_id, task in tasks.items()}


@async_time_it
async def run_extractor(extracts: ExtractPhase) -> ExtractedData:
    results = {}

    try:
        if extracts.pre:
            await task_group_executor(extracts.pre)

        results = await task_group_executor(extracts.steps)

        # If there's only one step, we can return its result directly.
        # Or if there's a merge step, we can return the merged result.
        df_result = (
            results.get(extracts.steps[0].id)
            if len(extracts.steps) == 1
            else plugin_sync_executor(extracts.merge, extracted_data=results)
        )

        if extracts.post:
            if len(extracts.post) == 1:
                # If there's only one post-processing step, we can run it directly.
                df_result = await plugin_async_executor(extracts.post[0], data=df_result)
            else:
                raise NotImplementedError("Multiple post-processing steps are not supported yet. ")  # noqa: TRY301 - Temporarily disabled for simplicity

    except Exception as e:
        error_message = "Extraction Phase Error"
        raise ExtractError(error_message, e) from e

    else:
        return df_result


@sync_time_it
def run_transformer(data: ExtractedData, transformations: TransformPhase) -> TransformedData:
    if not transformations.steps:
        logging.info("No transformations to run")
        return data

    try:
        transformed_data = reduce(lambda data, plugin: plugin_sync_executor(plugin, data), transformations.steps, data)
    except Exception as e:
        msg = "Transformation Phase Error"
        raise TransformError(msg, e) from e

    return transformed_data


@async_time_it
async def run_loader(data: ExtractedData | TransformedData, destinations: LoadPhase) -> None:
    if destinations.pre:
        await task_group_executor(destinations.pre)

    try:
        await task_group_executor(destinations.steps, data=data)

        if destinations.post:
            await task_group_executor(destinations.post, data=data)
    except Exception as e:
        error_message = "Load Phase Error"
        raise LoadError(error_message, e) from e


@sync_time_it
def run_transformer_after_load(transformations: TransformLoadPhase) -> None:
    try:
        for plugin in transformations.steps:
            plugin_sync_executor(plugin)

    except Exception as e:
        error_message = "Transform Load Phase Error"
        raise TransformLoadError(error_message, e) from e


class PipelineStrategy(metaclass=ABCMeta):
    @abstractmethod
    async def execute(self, pipeline: Pipeline) -> bool:
        raise NotImplementedError("This has to be implemented by the subclasses.")


class ETLStrategy(PipelineStrategy):
    async def execute(self, pipeline: Pipeline) -> bool:
        extracted_data = await run_extractor(pipeline.extract)

        # Transform (CPU-bound work, so offload to executor)
        transformed_data = await asyncio.get_running_loop().run_in_executor(
            None, run_transformer, extracted_data, pipeline.transform
        )

        await run_loader(transformed_data, pipeline.load)

        return True


class ELTStrategy(PipelineStrategy):
    async def execute(self, pipeline: Pipeline) -> bool:
        extracted_data = await run_extractor(pipeline.extract)

        await run_loader(extracted_data, pipeline.load)

        run_transformer_after_load(pipeline.load_transform)

        return True


class ETLTStrategy(PipelineStrategy):
    async def execute(self, pipeline: Pipeline) -> bool:
        extracted_data = await run_extractor(pipeline.extract)

        transformed_data = await asyncio.get_running_loop().run_in_executor(
            None, run_transformer, extracted_data, pipeline.transform
        )

        await run_loader(transformed_data, pipeline.load)

        run_transformer_after_load(pipeline.load_transform)

        return True


PIPELINE_STRATEGY_MAP = {
    PipelineType.ETL: ETLStrategy,
    PipelineType.ELT: ELTStrategy,
    PipelineType.ETLT: ETLTStrategy,
}
