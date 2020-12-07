# Support Pydantic Models as ParamTypes
# https://github.com/tiangolo/typer/issues/111

from typing import Any

import click
import typer

_get_click_type = typer.main.get_click_type


def supersede_get_click_type(
    *, annotation: Any, parameter_info: typer.main.ParameterInfo
) -> click.ParamType:
    if hasattr(annotation, "parse_raw"):

        class CustomParamType(click.ParamType):
            def convert(self, value, param, ctx):
                return annotation.parse_raw(value)

        return CustomParamType()
    else:
        return _get_click_type(annotation=annotation, parameter_info=parameter_info)


typer.main.get_click_type = supersede_get_click_type