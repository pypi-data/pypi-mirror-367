import copy
from typing import Any

from pydantic import BaseModel, Field
from rich.table import Table
from rich.text import Text

from agents.code_logician import rich_utils

from .imandrax import DecomposeRes


class RawDecomposeReq(BaseModel):
    """
    A function to decompose in source code and its corresponding function in IML.
    """

    description: str = Field(
        description="Human-readable description of the function to decompose"
    )
    src_func_name: str = Field(
        description="name of function to decompose in source code"
    )
    iml_func_name: str = Field(description="name of function to decompose in IML")


class DecomposeReqData(BaseModel):
    name: str
    assuming: list[str] | None = Field(None)
    basis: list[str] | None = Field(None)
    rule_specs: list[str] | None = Field(None)
    prune: bool | None = Field(True)
    ctx_simp: bool | None = Field(True)
    lift_bool: Any | None = Field(None)
    timeout: float | None = Field(None)
    str_: bool | None = Field(True)

    def render_content(self) -> Text:
        data = self.model_dump()
        data = {k: v for k, v in data.items() if v is not None}
        skip_keys = ["str_", "name"]
        data = {k: v for k, v in data.items() if k not in skip_keys}

        content_t = rich_utils.devtools_pformat(data, indent=0)
        content_ts = content_t.split("\n")[1:-1]

        t = rich_utils.join_texts(content_ts)
        return t

    def __rich__(self) -> Text:
        t = Text()
        t.append(Text("DecomposeReqData:", style="bold"))
        t.append("\n")
        t.append(rich_utils.left_pad(self.render_content(), 2))
        return t


class RegionDecomp(BaseModel):
    """
    A region decomposition
    """

    raw: RawDecomposeReq
    data: DecomposeReqData | None = Field(None)
    res: DecomposeRes | None = Field(None)

    test_cases: dict[str, list[dict]] | None = Field(
        None,
        examples=[
            {
                "iml": [
                    {"args": {"x": "1"}, "expected_output": "(-2)"},
                    {"args": {"x": "2"}, "expected_output": "4"},
                ],
                "src": [
                    {
                        "args": {"x": "1"},
                        "expected_output": "-2",
                        "docstr": (
                            "Constraints:\n    - `x <= 1`\nInvariant:\n    - `x - 3`\n"
                        ),
                    },
                    {
                        "args": {"x": "2"},
                        "expected_output": "4",
                        "docstr": (
                            "Constraints:\n    - `x >= 2`\nInvariant:\n    - `x + 2`\n"
                        ),
                    },
                ],
            }
        ],
    )

    @staticmethod
    def render_test_cases(test_cases: dict[str, list[dict]]) -> Table:
        test_cases = copy.deepcopy(test_cases)
        if "src" in test_cases:
            data = test_cases["src"]
        else:
            data = test_cases["iml"]

        if "docstr" in data[0]:
            for item in data:
                item.pop("docstr")

        table = Table(title="Test Cases")
        col_names = list(data[0].keys())

        def title_case(s: str) -> str:
            s = s.replace("_", " ")
            return s.title()

        col_names = [title_case(name) for name in col_names]
        col_names = ["", *col_names]
        for col_name in col_names:
            table.add_column(col_name)

        for i, item in enumerate(data, 1):
            table.add_row(str(i), *list(map(str, list(item.values()))))

        return table

    def render_content(self) -> list[Text | str]:
        ts = []
        ts.append(Text("RawDecomposeReq:", style="bold"))
        ts.append(f"  Src func name: {self.raw.src_func_name}")
        ts.append(f"  IML func name: {self.raw.iml_func_name}")
        ts.append(f"  Description: {self.raw.description}")

        ts.append(self.data.__rich__())

        ts.append(Text("DecomposeRes:", style="bold"))
        ts.append(
            f"  {str(len(self.res.__repr__())) + ' bytes' if self.res else 'None'}"
        )

        ts.append(Text("Test cases:", style="bold"))
        ts.append(f"  {len(self.test_cases['iml']) if self.test_cases else 'None'}")
        return ts

    def __rich__(self) -> Text:
        title_t = Text("RegionDecomp", style="bold")

        content_ts = self.render_content()
        content_t = rich_utils.join_texts(content_ts)

        t = Text()
        t.append(title_t)
        t.append("\n")
        t.append(rich_utils.left_pad(content_t, 2))
        return t

    def __repr__(self):
        return self.__rich__().plain
