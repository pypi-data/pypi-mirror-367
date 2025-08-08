"""Requirements are a special type of Component used as input to the "validate" step in Instruct/Validate/Repair design patterns."""

import re
from collections.abc import Callable
from typing import Any

from mellea.backends import (
    Backend,
    BaseModelSubclass,
    CBlock,
    Component,
    Context,
    ModelOutputThunk,
)
from mellea.backends.aloras import Alora
from mellea.helpers.fancy_logger import FancyLogger
from mellea.stdlib.base import GenerateLog, ModelOutputThunk, TemplateRepresentation


def default_output_to_bool(x: CBlock | str) -> bool:
    """Checks if a given output should be marked converted to `True`.

    Checks if the output is exactly equal to "yes" or "y" (case-insensitive). If not, it will also
    check if any of the words in the output are "yes" (case-insensitive).
    """
    output = str(x)

    if output.upper() == "YES" or output.upper() == "Y":
        return True

    word_splits = re.split(r"\W+", output)
    if "YES" in [word.upper() for word in word_splits]:
        return True

    return False


class Requirement(Component):
    """Requirements are a special type of Component used as input to the Validate step in Instruct/Validate/Repair patterns."""

    def __init__(
        self,
        description: str | None = None,
        validation_fn: Callable[[Context], Any] | None = None,
        *,
        output_to_bool: Callable[[CBlock | str], bool] | None = default_output_to_bool,
        check_only: bool = False,
    ):
        """A Requirement, interpreted over a Context.

          By default, requirements are validated by the model using LLM-as-a-Judge (or a `constraint` LoRA when available). However, you can also provide a `validate` function with arbitrary behavior.

        Args:
            description: A natural-language description of the requirement. This will sometimes be included in `Instruction` prompts; if you do not want the requirement to be included in the prompt to avoid [Purple Elephant Effects](https://${PROJECT_URL}/llm-requirement-engineering-and-purple-elephants/) use check_only=True.
            validation_fn: If provided, this function will be executed instead of using LLM-as-a-Judge. The `bool()` for the function's output defines whether the requirement passes.
            output_to_bool: An `output_to_bool` may be provided so that the library can translate the LLM-as-a-judge or ALora output into a boolean value. If none is provided, we will look for 'yes' (case-insensitive) in the LLMaJ output.
            check_only: If set, then `Instruction` will not include this requirement in its prompt.
        """
        self.description = description
        self.output_to_bool = output_to_bool
        self.validation_fn = validation_fn
        self.check_only = check_only

    def validate(
        self,
        backend: Backend,
        ctx: Context,
        *,
        format: type[BaseModelSubclass] | None = None,
        model_options: dict | None = None,
        generate_logs: list[GenerateLog] | None = None,
    ) -> tuple[Any, bool]:
        """Chooses the appropriate validation strategy and applies that strategy."""
        if self.validation_fn is not None:
            # Python validation strategy
            result = self.validation_fn(ctx)
            return result, bool(result)
        else:
            # LLMaJ validation strategy. This includes ALora because the backend generate call will appropriately dispatch.
            assert self.output_to_bool is not None
            last_output = ctx.last_output()
            assert isinstance(last_output, ModelOutputThunk), (
                " Context has no appropriate last output"
            )
            self._output = last_output.value  # type: ignore
            llm_as_a_judge_result = backend.generate_from_context(
                self,
                ctx,
                format=format,
                model_options=model_options,
                generate_logs=generate_logs,
            )
            # This is crucial, because requirements can get reused;
            # this also means requirements are not thread-safe.
            self._output = None
            return llm_as_a_judge_result, self.output_to_bool(llm_as_a_judge_result)

    def parts(self):
        """Returns all of the constituent parts of a Requirement."""
        raise Exception(
            "Disallowing use of `parts` until we figure out exactly what it's supposed to be for"
        )

    def format_for_llm(self) -> TemplateRepresentation | str:
        """Some object protocol magic happens here with management of the output."""
        assert self._output is not None, (
            "Object protocol error: should never try to templatize a Requirement except inside of a validate call for that same requirement."
        )
        return TemplateRepresentation(
            obj=self,
            args={"description": self.description, "output": self._output},
            tools=None,
            template_order=["*", "Requirement"],
        )


class LLMaJRequirement(Requirement):
    """A requirement that always uses LLM-as-a-Judge. Any available constraint ALoRA will be ignored."""

    use_aloras: bool = False


class ALoraRequirement(Requirement):
    """A requirement that always uses an (possibly specified) ALora. If an exception is thrown during the ALora execution path, `mellea` will fall back to LLMaJ. But that is the only case where LLMaJ will be used."""

    def __init__(self, description: str, alora: Alora | None = None):
        """A requirement that is validated by an ALora.

        Args:
            description: See `Requirement.__init__`
            alora: if None, the ALora with name "constraint" will be used.
        """
        super().__init__(description, validation_fn=None)
        self.use_aloras: bool = True
        self.alora = alora


def reqify(r: str | Requirement) -> Requirement:
    """Maps strings to Requirements.

    This is a utility method for functions that allow you to pass in Requirements as either explicit Requirement objects or strings that you intend to be interpreted as requirements.
    """
    if type(r) is str:
        return Requirement(r)
    elif isinstance(r, Requirement):
        return r
    else:
        raise Exception(f"reqify takes a str or requirement, not {r}")


def req(*args, **kwargs) -> Requirement:
    """Shorthand for Requirement.__init__."""
    return Requirement(*args, **kwargs)


def check(*args, **kwargs) -> Requirement:
    """Shorthand for Requirement.__init__(..., check_only=True)."""
    return Requirement(*args, **kwargs, check_only=True)


def simple_validate(fn: Callable[[str], bool]) -> Callable[[Context], bool]:
    """Syntactic sugar for writing validation functions that only operate over the last output from the model (interpreted as a string).

    This is useful when your validation logic only depends upon the most recent model output. For example:

    `Requirement("Answer 'yes' or 'no'", simple_validate(lambda x: x == 'yes' or x == 'no')`

    Validation functions operate over `Context`. Often you do not care about the entire context, and just want to consider the most recent output from the model.

    Important notes:
     - this operates over the more recent _model output_, not the most recent message.
     - Model outputs are sometimes parsed into more complex types (eg by a `Formatter.parse` call or an OutputProcessor). This validation logic will interpret the most recent output as a string, regardless of whether it has a more complex parsed representation.
    """

    def validate(ctx: Context) -> bool:
        o = ctx.last_output()
        if o is None or o.value is None:
            FancyLogger.get_logger().warn(
                "Last output of context was None. That might be a problem. We return validation as False to be able to continue..."
            )
            return False
        return fn(o.value)

    return validate
