from textwrap import indent
from typing import Literal, Self

from pydantic import BaseModel, Field
from rich.text import Text

import agents.code_logician.rich_utils as rich_utils

from .imandrax import VerifyRes


class RawVerifyReq(BaseModel):
    """
    A formal specification of a property / logical statement, clause, predicate,
    or condition to verify about functions in the source code.

    Each verification pairs a natural language description with a corresponding logical
    statement that will be later used in tasks related to property-based testing and
    formal verification.
    The description is human-readable, while the logical statement is more precise,
    mathematically formal.
    """

    src_func_names: list[str] = Field(
        title="Src func names",
        description="names of the functions (including class methods) involved "
        "in the verification",
    )
    iml_func_names: list[str] = Field(
        title="IML func names",
        description="names of the corresponding functions in IML",
    )
    description: str = Field(
        title="Description",
        description="Human-readable description of the property to verify. Should "
        "clearly explain what aspect of the function's behavior is being checked. "
        "Example: 'The function always returns a value greater than or equal to 10' or "
        "'The output array is always sorted in ascending order'",
    )
    logical_statement: str = Field(
        title="Logical statement",
        description="Logical statement expressing the property in a precise way. "
        "Can use plain English with logical terms like 'for all', 'there exists', "
        "'and', 'or', etc. Example: 'for all inputs x, f(x) is greater than or equal "
        "to 10' or 'for all indices i from 0 to n-2, array[i] is less than or equal "
        "to array[i+1]'",
    )

    def __rich__(self) -> Text:
        field_titles_and_values = rich_utils.extract_field_titles_and_values(self)
        items_t = Text()
        for f_title, f_value in field_titles_and_values.items():
            items_t.append(
                Text.assemble(
                    " " * 2,
                    f_title,
                    f": {f_value}\n",
                )
            )
        title_t = Text("RawVerifyReq", style="bold")
        t = Text()
        t.append(title_t)
        t.append("\n")
        t.append(items_t)
        return t

    def __repr__(self):
        return self.__rich__().plain


class VerifyReqData(BaseModel):
    """Verify"""

    predicate: str = Field(
        title="Predicate",
        description="IML code representing some logical statement using lambda"
        "functions. Eg. `fun x -> x >= 10`, `fun x -> f x <> 98`. Backticks should"
        "be omitted.",
    )
    kind: Literal["verify", "instance"] = Field(
        title="Kind",
        description="""Kind of reasoning request. 
        - `verify` checks that the given predicate is always true (universal)
        - `instance` finds an example where the predicate is true (existential)
        """,
    )

    def to_iml(self) -> str:
        return f"${self.kind} ({self.predicate})"

    def to_negation(self) -> Self:
        """Negate the predicate"""

        predicate = self.predicate
        arrow_idx = predicate.index("->")
        dom = predicate[:arrow_idx]
        cod = predicate[arrow_idx + 2 :]
        neg_cod = f"not ({cod.strip()})"
        neg_predicate = f"{dom}-> {neg_cod}"
        if self.kind == "verify":
            kind = "instance"
        else:
            kind = "verify"
        return self.__class__(predicate=neg_predicate, kind=kind)

    def __rich__(self) -> Text:
        iml = self.to_iml().lstrip("$").strip()
        iml = indent(iml, "  ")
        t = Text()
        t.append(Text("VerifyReqData", style="bold"))
        t.append("\n")
        t.append(Text(iml, style="dim"))
        return t

    def __repr__(self):
        return self.__rich__().plain


class VG(BaseModel):
    """
    A verification goal
    """

    raw: RawVerifyReq
    data: VerifyReqData | None = Field(None)
    res: VerifyRes | None = Field(None)

    @staticmethod
    def render_verify_res(res: VerifyRes) -> Text:
        content = rich_utils.join_texts(
            rich_utils.devtools_pformat(res).split("\n")[1:-1]
        )
        t = Text()
        t.append(Text("VerifyRes:\n", style="bold"))
        t.append(content)
        return t

    def render_content(self) -> list[Text | str]:
        ts = []

        if self.raw:
            ts.append(rich_utils.left_pad(self.raw.__rich__(), 2))
        else:
            ts.append(indent("None", "  "))

        if self.data:
            ts.append(rich_utils.left_pad(self.data.__rich__(), 2))
        else:
            ts.append(indent("None", "  "))

        if self.res:
            ts.append(rich_utils.left_pad(self.render_verify_res(self.res), 2))
        else:
            ts.append(indent("None", "  "))
        return ts

    def render_title(self) -> Text:
        return Text("VG", style="bold")

    def __rich__(self) -> Text:
        title_t = self.render_title()
        content_ts = self.render_content()
        content_t = rich_utils.join_texts(content_ts)

        t = Text()
        t.append(title_t)
        t.append("\n")
        t.append(rich_utils.left_pad(content_t, 2))
        return t

    def __repr__(self):
        return self.__rich__().plain
