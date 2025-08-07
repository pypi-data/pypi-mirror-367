import json
import typing as t

import click
from pulp_glue.common.openapi import OpenAPI


def mount(main: click.Group, **kwargs: t.Any) -> None:
    if hasattr(OpenAPI, "_parse_response"):
        original_parse_response = OpenAPI._parse_response
        parse_response_attr = "_parse_response"
    else:
        original_parse_response = OpenAPI.parse_response  # type: ignore[attr-defined]
        parse_response_attr = "parse_response"

    # Define our custom implementation that handles 202 responses (Original one throws an error)
    def custom_parse_response(
        self: OpenAPI, method_spec: t.Dict[str, t.Any], response: t.Any
    ) -> t.Any:
        # Handle 202 responses directly
        if response.status_code == 202:
            content_type = response.headers.get("content-type")
            if content_type is not None and content_type.startswith("application/json"):
                return json.loads(response.body)
            return {"status": "accepted"}

        # For all other responses, use the original implementation
        return original_parse_response(self, method_spec, response)

    setattr(OpenAPI, parse_response_attr, custom_parse_response)

    # Continue with normal mounting
    from pulpcore.cli.console.task import attach_tasks_commands
    from pulpcore.cli.console.vulnerability import attach_vulnerability_commands
    from pulpcore.cli.console.populated_domain import attach_domain_commands

    @main.group()
    def console() -> None:
        """Pulp Console commands."""
        pass

    attach_vulnerability_commands(console)  # type: ignore
    attach_tasks_commands(console)  # type: ignore
    attach_domain_commands(console)  # type: ignore
