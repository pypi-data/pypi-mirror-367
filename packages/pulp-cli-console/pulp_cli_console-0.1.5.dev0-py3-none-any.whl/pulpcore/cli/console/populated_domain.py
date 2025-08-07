import typing as t

import click
from pulp_glue.common.context import PulpContext
from pulpcore.cli.common.generic import pass_pulp_context


@click.group()
def populated_domain() -> None:
    """Populated domain management commands."""
    pass


@populated_domain.command()
@click.option("--name", required=True, help="Name of the domain to create")
@pass_pulp_context
def create(
    pulp_ctx: PulpContext,
    name: str,
) -> None:
    """Create a new domain using the self-service endpoint."""

    data = {
        "name": name,
        "storage_settings": {},
        "storage_class": "storages.backends.s3boto3.S3Boto3Storage",
    }

    try:
        response = pulp_ctx.call(operation_id="api_pulp_create_domain_post", body=data)

        click.echo(f"Domain '{name}' created successfully!")
        click.echo(f"Domain ID: {response.get('pulp_id', 'N/A')}")

    except Exception as e:
        click.echo(f"Error creating domain: {str(e)}", err=True)
        raise click.ClickException(f"Failed to create domain '{name}': {str(e)}")


def attach_domain_commands(main_group: click.Group) -> None:
    """Attach populated domain commands to the main console group."""
    main_group.add_command(populated_domain)
