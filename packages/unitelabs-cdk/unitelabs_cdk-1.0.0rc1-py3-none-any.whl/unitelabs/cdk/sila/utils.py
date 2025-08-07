import asyncio
import collections.abc
import inspect
import re
import time
import typing

import packaging.version


def humanize(value: typing.Optional[str] = None, sep: str = "_") -> str:
    """Convert `value` to a human-readable string."""

    return " ".join(x.capitalize() for x in (value or "").split(sep))


def parse_docs(docs: typing.Optional[str] = None) -> dict:
    """Parse documentation strings."""
    docs = docs or ""
    directives = re.split(r"^\.\. *([^:]+):: *", docs, flags=re.MULTILINE)
    result = {"default": inspect.cleandoc(directives.pop(0)).replace("\n", " ")}

    for i in range(0, len(directives), 2):
        key = directives[i]

        params = re.split(r"^ *:([^:]+): *", directives[i + 1], flags=re.MULTILINE)
        item = {"default": inspect.cleandoc(params.pop(0)).replace("\n", " ")}

        par = {params[i]: params[i + 1] for i in range(0, len(params), 2)}
        for param_k, param_v in par.items():
            item[param_k] = inspect.cleandoc(param_v).replace("\n", " ")

        result[key] = result.get(key, [])
        result[key].append(item)

    return result


def parse_version(version: str) -> str:
    """Parse a PEP 440-compatible version into a valid SiLA 2 version."""

    try:
        v = packaging.version.parse(version)
        parts = [str(v.major), str(v.minor)]
        if v.micro != 0:
            parts.append(str(v.micro))
        sila_version = ".".join(parts)

        suffix_parts = []
        if v.pre:
            suffix_parts.append(f"{v.pre[0]}{v.pre[1]}")
        if v.post:
            suffix_parts.append(f"post{v.post}")
        if v.dev:
            suffix_parts.append(f"dev{v.dev}")
        if v.local:
            suffix_parts.append(v.local.replace(".", "_"))

        if suffix_parts:
            sila_version += "_" + "_".join(suffix_parts)

        return sila_version
    except packaging.version.InvalidVersion:
        msg = f"Invalid version format: '{version}'."
        raise ValueError(msg) from None


def to_display_name(value: str) -> str:
    """Convert `value` to a display name."""
    value = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", value)
    value = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", value)
    return value.replace("-", " ")


def set_interval(function: collections.abc.Callable, delay: float = 1) -> asyncio.Task:
    """Repeatedly call a function or execute a codesnippet, with a fixed time delay between each call."""
    delay_ns = delay * 10**9
    timer = time.perf_counter_ns()

    async def interval(timer: float) -> None:
        while True:
            response = function()
            if inspect.isawaitable(response):
                await response

            timer += delay_ns
            await asyncio.sleep((timer - time.perf_counter_ns()) / 10**9)

    return asyncio.create_task(interval(timer))


def clear_interval(interval: asyncio.Task) -> None:
    """Cancel a timed, repeating action which was previously established by a call to set_interval()."""
    interval.cancel()


__all__ = ["clear_interval", "humanize", "parse_docs", "set_interval", "to_display_name"]
