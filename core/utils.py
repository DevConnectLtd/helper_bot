from __future__ import annotations

import logging
import os
import sys
import typing

import attrs
import dotenv

__all__: tuple[str, ...] = ("EnvironmentVariables", "load_and_verify_envs")


class Missing:
    ...


MISSING = Missing()

T = typing.TypeVar("T")

MissingOr = typing.Union[Missing, T]


@attrs.define(kw_only=True)
class EnvironmentVariables:
    BOT_TOKEN: str
    PGSQL_URL: str


dotenv.load_dotenv()


def load_and_verify_envs() -> EnvironmentVariables:
    required: set[str] = set([a.name for a in EnvironmentVariables.__attrs_attrs__])  # type: ignore
    if not ((validated := (required)).intersection(os.environ)) == required:
        logging.error(
            "\n".join(
                (
                    "ENV ERROR!",
                    "Missing required environmental variables.",
                    "-----------------------------------------",
                    "Missing:",
                    "--------",
                    "%s",
                )
            ),
            required.difference(validated),
        )
        print(
            validated,
            required,
        )
        sys.exit()
    else:
        return EnvironmentVariables(**{k: v for k, v in os.environ.items() if k in required})
