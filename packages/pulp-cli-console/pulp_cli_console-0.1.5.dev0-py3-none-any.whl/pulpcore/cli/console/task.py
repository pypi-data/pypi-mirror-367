from typing import Optional

import click
from pulp_glue.common.context import PulpContext
from pulp_glue.console.context import AdminTaskContext

from pulpcore.cli.common.generic import (
    PulpCLIContext,
    pass_pulp_context,
)


def attach_tasks_commands(console_group: click.Group) -> None:
    @console_group.group()
    @pass_pulp_context
    @click.pass_context
    def task(ctx: click.Context, pulp_ctx: PulpContext, /) -> None:
        """Manage admin tasks."""
        ctx.obj = AdminTaskContext(pulp_ctx)

    @task.command()
    @click.option("--limit", type=int, help="Limit the number of tasks shown")
    @click.option("--offset", type=int, help="Skip a number of tasks")
    @click.option("--name", help="Filter by task name")
    @click.option("--name-contains", "name__contains", help="Filter tasks containing this name")
    @click.option(
        "--logging-cid-contains", "logging_cid__contains", help="Filter by logging correlation ID"
    )
    @click.option("--state", help="Filter by task state")
    @click.option("--state-in", "state__in", help="Filter by multiple states (comma-separated)")
    @click.option("--task-group", help="Filter by task group")
    @click.option("--parent-task", help="Filter by parent task")
    @click.option("--worker", help="Filter by worker")
    @click.option("--created-resources", help="Filter by created resources")
    @click.option(
        "--started-at-gte", "started_at__gte", help="Filter by start time (greater than or equal)"
    )
    @click.option(
        "--started-at-lte", "started_at__lte", help="Filter by start time (less than or equal)"
    )
    @click.option(
        "--finished-at-gte",
        "finished_at__gte",
        help="Filter by finish time (greater than or equal)",
    )
    @click.option(
        "--finished-at-lte", "finished_at__lte", help="Filter by finish time (less than or equal)"
    )
    @click.option(
        "--reserved-resource",
        "reserved_resources",
        help="Href of a resource reserved by the task",
    )
    @click.option(
        "--reserved-resource-in",
        "reserved_resources__in",
        help="Href of a resource reserved by the task (comma-separated)",
    )
    @click.option(
        "--exclusive-resource",
        "exclusive_resources",
        help="Href of a resource reserved exclusively by the task",
    )
    @click.option(
        "--exclusive-resource-in",
        "exclusive_resources__in",
        help="Href of a resource reserved exclusively by the task (comma-separated)",
    )
    @click.option(
        "--shared-resource",
        "shared_resources",
        help="Href of a resource shared by the task",
    )
    @click.option(
        "--shared-resource-in",
        "shared_resources__in",
        help="Href of a resource shared by the task (comma-separated)",
    )
    @click.pass_context
    @pass_pulp_context
    def list(
        pulp_ctx: PulpCLIContext,
        ctx: click.Context,
        /,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        name: Optional[str] = None,
        name__contains: Optional[str] = None,
        logging_cid__contains: Optional[str] = None,
        state: Optional[str] = None,
        state__in: Optional[str] = None,
        task_group: Optional[str] = None,
        parent_task: Optional[str] = None,
        worker: Optional[str] = None,
        created_resources: Optional[str] = None,
        started_at__gte: Optional[str] = None,
        started_at__lte: Optional[str] = None,
        finished_at__gte: Optional[str] = None,
        finished_at__lte: Optional[str] = None,
        reserved_resources: Optional[str] = None,
        reserved_resources__in: Optional[str] = None,
        exclusive_resources: Optional[str] = None,
        exclusive_resources__in: Optional[str] = None,
        shared_resources: Optional[str] = None,
        shared_resources__in: Optional[str] = None,
    ) -> None:
        task_ctx = ctx.obj
        result = task_ctx.list(
            limit=limit,
            offset=offset,
            name=name,
            name__contains=name__contains,
            logging_cid__contains=logging_cid__contains,
            state=state,
            state__in=state__in,
            task_group=task_group,
            parent_task=parent_task,
            worker=worker,
            created_resources=created_resources,
            started_at__gte=started_at__gte,
            started_at__lte=started_at__lte,
            finished_at__gte=finished_at__gte,
            finished_at__lte=finished_at__lte,
            reserved_resources=reserved_resources,
            reserved_resources__in=reserved_resources__in,
            exclusive_resources=exclusive_resources,
            exclusive_resources__in=exclusive_resources__in,
            shared_resources=shared_resources,
            shared_resources__in=shared_resources__in,
        )
        pulp_ctx.output_result(result)
