from typing import Callable, Any, Set, Dict, List
from fastmcp.tools import Tool
from mcp.types import ToolAnnotations


def toolify(
    *,
    name: str | None = None,
    description: str | None = None,
    tags: Set[str] | None = None,
    enabled: bool = True,
    exclude_args: List[str] | None = None,
    annotations: ToolAnnotations | dict | None = None,
    meta: Dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Tool]:
    """
    Decorator to wrap a function in a fastmcp Tool.
    """
    def decorator(fn: Callable[..., Any]) -> Tool:
        return Tool.from_function(
            fn=fn,
            name=name,
            description=description,
            enabled=enabled,
            exclude_args=exclude_args,
            annotations=annotations,
            tags=tags,
            meta=meta
        )
    return decorator
