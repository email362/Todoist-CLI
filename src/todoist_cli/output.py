import json
from collections.abc import Iterable, Sequence
from typing import Any

from rich import box
from rich.console import Console
from rich.table import Table

Column = tuple[str, str]


def render_output(
    data: Any,
    *,
    output_format: str,
    no_color: bool = False,
    columns: Sequence[Column] | None = None,
    success_message: str = "Done.",
) -> None:
    console = Console(no_color=no_color)

    if output_format == "json":
        console.print(json.dumps(data, ensure_ascii=False))
        return

    if output_format == "ndjson":
        for item in _items_for_ndjson(data):
            console.print(json.dumps(item, ensure_ascii=False, separators=(",", ":")))
        return

    if data is None:
        console.print(success_message)
    elif isinstance(data, list):
        _render_list_table(console, data, columns)
    elif isinstance(data, dict):
        _render_detail_table(console, data, columns)
    else:
        console.print(str(data))


def _items_for_ndjson(data: Any) -> Iterable[Any]:
    if isinstance(data, list):
        return data
    return [data]


def _render_list_table(
    console: Console,
    rows: list[Any],
    columns: Sequence[Column] | None,
) -> None:
    if not rows:
        console.print("No results.")
        return

    table_columns = columns or _columns_from_rows(rows)
    table = Table(box=box.SIMPLE, show_edge=False)
    for heading, _key in table_columns:
        table.add_column(heading)

    for row in rows:
        values = [
            _format_value(_value_for_key(row, key)) for _heading, key in table_columns
        ]
        table.add_row(*values)

    console.print(table)


def _render_detail_table(
    console: Console,
    data: dict[str, Any],
    columns: Sequence[Column] | None,
) -> None:
    entries = columns or [(key.replace("_", " ").title(), key) for key in data]
    table = Table(box=box.SIMPLE, show_header=False, show_edge=False)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for heading, key in entries:
        value = _value_for_key(data, key)
        if value is not None:
            table.add_row(heading, _format_value(value))

    console.print(table)


def _columns_from_rows(rows: list[Any]) -> list[Column]:
    first_dict = next((row for row in rows if isinstance(row, dict)), None)
    if not isinstance(first_dict, dict):
        return [("Value", "")]
    return [(key.replace("_", " ").title(), key) for key in first_dict]


def _value_for_key(row: Any, key: str) -> Any:
    if key == "":
        return row
    if isinstance(row, dict):
        return row.get(key)
    return None


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(_format_value(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)
