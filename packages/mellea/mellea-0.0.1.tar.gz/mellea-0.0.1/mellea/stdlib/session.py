"""Mellea Sessions."""

from __future__ import annotations

from typing import Any, Literal

from mellea.backends import Backend, BaseModelSubclass
from mellea.backends.aloras.huggingface.granite_aloras import add_granite_aloras
from mellea.backends.formatter import FormatterBackend
from mellea.backends.huggingface import LocalHFBackend
from mellea.backends.model_ids import (
    IBM_GRANITE_3_2_8B,
    IBM_GRANITE_3_3_8B,
    ModelIdentifier,
)
from mellea.backends.ollama import OllamaModelBackend
from mellea.backends.openai import OpenAIBackend
from mellea.backends.watsonx import WatsonxAIBackend
from mellea.helpers.fancy_logger import FancyLogger
from mellea.stdlib.base import (
    CBlock,
    Component,
    Context,
    ContextTurn,
    GenerateLog,
    LinearContext,
    ModelOutputThunk,
    SimpleContext,
)
from mellea.stdlib.chat import Message, ToolMessage
from mellea.stdlib.instruction import Instruction
from mellea.stdlib.mify import mify
from mellea.stdlib.mobject import MObjectProtocol
from mellea.stdlib.requirement import Requirement, check, req
from mellea.stdlib.sampling import SamplingResult, SamplingStrategy


def backend_name_to_class(name: str) -> Any:
    """Resolves backend names to Backend classes."""
    if name == "ollama":
        return OllamaModelBackend
    elif name == "hf" or name == "huggingface":
        return LocalHFBackend
    elif name == "openai":
        return OpenAIBackend
    elif name == "watsonx":
        return WatsonxAIBackend
    else:
        return None


def start_session(
    backend_name: Literal["ollama", "hf", "openai", "watsonx"] = "ollama",
    model_id: str | ModelIdentifier = IBM_GRANITE_3_3_8B,
    ctx: Context | None = SimpleContext(),
    *,
    model_options: dict | None = None,
    **backend_kwargs,
) -> MelleaSession:
    """Helper for starting a new mellea session.

    Args:
        backend_name (str): ollama | hf | openai
        model_id (ModelIdentifier): a `ModelIdentifier` from the mellea.backends.model_ids module
        ctx (Optional[Context]): If not provided, a `LinearContext` is used.
        model_options (Optional[dict]): Backend will be instantiated with these as its default, if provided.
        backend_kwargs: kwargs that will be passed to the backend for instantiation.
    """
    backend_class = backend_name_to_class(backend_name)
    if backend_class is None:
        raise Exception(
            f"Backend name {backend_name} unknown. Please see the docstring for `mellea.stdlib.session.start_session` for a list of options."
        )
    assert backend_class is not None
    backend = backend_class(model_id, model_options=model_options, **backend_kwargs)
    return MelleaSession(backend, ctx)


class MelleaSession:
    """Mellea sessions are a THIN wrapper around `m` convenience functions with NO special semantics.

    Using a Mellea session is not required, but it does represent the "happy path" of Mellea programming. Some nice things about ussing a `MelleaSession`:
    1. In most cases you want to keep a Context together with the Backend from which it came.
    2. You can directly run an instruction or a send a chat, instead of first creating the `Instruction` or `Chat` object and then later calling backend.generate on the object.
    3. The context is "threaded-through" for you, which allows you to issue a sequence of commands instead of first calling backend.generate on something and then appending it to your context.

    These are all relatively simple code hygiene and state management benefits, but they add up over time.
    If you are doing complicating programming (e.g., non-trivial inference scaling) then you might be better off forgoing `MelleaSession`s and managing your Context and Backend directly.

    Note: we put the `instruct`, `validate`, and other convenience functions here instead of in `Context` or `Backend` to avoid import resolution issues.
    """

    def __init__(self, backend: Backend, ctx: Context | None = None):
        """Initializes a new Mellea session with the provided backend and context.

        Args:
            backend (Backend): This is always required.
            ctx (Context): The way in which the model's context will be managed. By default, each interaction with the model is a stand-alone interaction, so we use SimpleContext as the default.
            model_options (Optional[dict]): model options, which will upsert into the model/backend's defaults.
        """
        self.backend = backend
        self.ctx = ctx if ctx is not None else SimpleContext()
        self._backend_stack: list[tuple[Backend, dict | None]] = []
        self._session_logger = FancyLogger.get_logger()

    def _push_model_state(self, new_backend: Backend, new_model_opts: dict):
        """The backend and model options used within a `Context` can be temporarily changed. This method changes the model's backend and model_opts, while saving the current settings in the `self._backend_stack`.

        Question: should this logic be moved into context? I really want to keep `Session` as simple as possible... see true motivation in the docstring for the class.
        """
        self._backend_stack.append((self.backend, self.model_options))
        self.backend = new_backend
        self.opts = new_model_opts

    def _pop_model_state(self) -> bool:
        """Pops the model state.

        The backend and model options used within a `Context` can be temporarily changed by pushing and popping from the model state.
        This function restores the model's previous backend and model_opts from the `self._backend_stack`.

        Question: should this logic be moved into context? I really want to keep `Session` as simple as possible... see true motivation in the docstring for the class.
        """
        try:
            b, b_model_opts = self._backend_stack.pop()
            self.backend = b
            self.model_options = b_model_opts
            return True
        except Exception:
            return False

    def reset(self):
        """Reset the context state."""
        self.ctx.reset()

    def summarize(self) -> ModelOutputThunk:
        """Summarizes the current context."""
        raise NotImplementedError()

    def instruct(
        self,
        description: str,
        *,
        requirements: list[Requirement | str] | None = None,
        icl_examples: list[str | CBlock] | None = None,
        grounding_context: dict[str, str | CBlock | Component] | None = None,
        user_variables: dict[str, str] | None = None,
        prefix: str | CBlock | None = None,
        output_prefix: str | CBlock | None = None,
        strategy: SamplingStrategy | None = None,
        return_sampling_results: bool = False,
        format: type[BaseModelSubclass] | None = None,
        model_options: dict | None = None,
        tool_calls: bool = False,
    ) -> ModelOutputThunk | SamplingResult:
        """Generates from an instruction.

        Args:
            description: The description of the instruction.
            requirements: A list of requirements that the instruction can be validated against.
            icl_examples: A list of in-context-learning examples that the instruction can be validated against.
            grounding_context: A list of grounding contexts that the instruction can use. They can bind as variables using a (key: str, value: str | ContentBlock) tuple.
            user_variables: A dict of user-defined variables used to fill in Jinja placeholders in other parameters. This requires that all other provided parameters are provided as strings.
            prefix: A prefix string or ContentBlock to use when generating the instruction.
            output_prefix: A string or ContentBlock that defines a prefix for the output generation. Usually you do not need this.
            strategy: A SamplingStrategy that describes the strategy for validating and repairing/retrying for the instruct-validate-repair pattern. None means that no particular sampling strategy is used.
            return_sampling_results: attach the (successful and failed) sampling attempts to the results.
            format: If set, the BaseModel to use for constrained decoding.
            model_options: Additional model options, which will upsert into the model/backend's defaults.
            tool_calls: If true, tool calling is enabled.
        """
        requirements = [] if requirements is None else requirements
        icl_examples = [] if icl_examples is None else icl_examples
        grounding_context = dict() if grounding_context is None else grounding_context
        # all instruction options are forwarded to create a new Instruction object
        i = Instruction(
            description=description,
            requirements=requirements,
            icl_examples=icl_examples,
            grounding_context=grounding_context,
            user_variables=user_variables,
            prefix=prefix,
            output_prefix=output_prefix,
        )

        res = None
        generate_logs: list[GenerateLog] = []
        if strategy is None:
            result = self.backend.generate_from_context(
                i,
                ctx=self.ctx,
                format=format,
                model_options=model_options,
                generate_logs=generate_logs,
                tool_calls=tool_calls,
            )

            # make sure that one Log is marked as the one related to result
            assert len(generate_logs) == 1, "Simple call can only add one generate_log"
            generate_logs[0].is_final_result = True
        else:
            if strategy.validate is None:
                strategy.validate = lambda reqs, output: self.validate(  # type: ignore
                    reqs,
                    output=output,  # type: ignore
                )  # type: ignore
            if strategy.generate is None:
                strategy.generate = (
                    lambda instruction, g_logs: self.backend.generate_from_context(
                        instruction,
                        ctx=self.ctx,
                        format=format,
                        model_options=model_options,
                        generate_logs=g_logs,
                        tool_calls=tool_calls,
                    )
                )

            # sample
            res = strategy.sample(i, generate_logs=generate_logs)

            # make sure that one Log is marked as the one related to res.result
            if res.success:
                # if successful, the last log is the one related
                generate_logs[-1].is_final_result = True
            else:
                # find the one where log.result and res.result match
                selected_log = [
                    log for log in generate_logs if log.result == res.result
                ]
                assert len(selected_log) == 1, (
                    "There should only be exactly one log corresponding to the single result. "
                )
                selected_log[0].is_final_result = True

            result = res.result

        self.ctx.insert_turn(ContextTurn(i, result), generate_logs=generate_logs)

        if return_sampling_results:
            assert res is not None, "Asking for sampling results without sampling."
            return res
        else:
            return result

    def chat(
        self,
        content: str,
        role: Message.Role = "user",
        *,
        user_variables: dict[str, str] | None = None,
        format: type[BaseModelSubclass] | None = None,
        model_options: dict | None = None,
        tool_calls: bool = False,
    ) -> Message:
        """Sends a simple chat message and returns the response. Adds both messages to the Context."""
        if user_variables is not None:
            content_resolved = Instruction.apply_user_dict_from_jinja(
                user_variables, content
            )
        else:
            content_resolved = content
        user_message = Message(role=role, content=content_resolved)
        generate_logs: list[GenerateLog] = []
        output_thunk = self.backend.generate_from_context(
            action=user_message,
            ctx=self.ctx,
            format=format,
            model_options=model_options,
            generate_logs=generate_logs,
            tool_calls=tool_calls,
        )
        # make sure that the last and only Log is marked as the one related to result
        assert len(generate_logs) == 1, "Simple call can only add one generate_log"
        generate_logs[0].is_final_result = True

        parsed_assistant_message = output_thunk.parsed_repr
        assert type(parsed_assistant_message) is Message
        self.ctx.insert(user_message)
        self.ctx.insert(output_thunk, generate_logs=generate_logs)
        return parsed_assistant_message

    def act(self, c: Component, tool_calls: bool = False) -> Any:
        """Runs a generic action, and adds both the action and the result to the context."""
        generate_logs: list[GenerateLog] = []
        result: ModelOutputThunk = self.backend.generate_from_context(
            c, self.ctx, generate_logs=generate_logs, tool_calls=tool_calls
        )
        self.ctx.insert_turn(turn=ContextTurn(c, result), generate_logs=generate_logs)
        return result

    def validate(
        self,
        reqs: Requirement | list[Requirement],
        *,
        output: CBlock | None = None,
        return_full_validation_results: bool = False,
        format: type[BaseModelSubclass] | None = None,
        model_options: dict | None = None,
        generate_logs: list[GenerateLog] | None = None,
    ) -> list[bool] | list[tuple[Any, bool]]:
        """Validates a set of requirements over the output (if provided) or the current context (if the output is not provided)."""
        # Turn a solitary requirement in to a list of requirements, and then reqify if needed.
        reqs = [reqs] if not isinstance(reqs, list) else reqs
        reqs = [Requirement(req) if type(req) is str else req for req in reqs]
        if output is None:
            validation_target_ctx = self.ctx
        else:
            validation_target_ctx = SimpleContext()
            validation_target_ctx.insert(output)
        rvs = []
        for requirement in reqs:
            req_v, req_satisfied = requirement.validate(
                self.backend,
                validation_target_ctx,
                format=format,
                model_options=model_options,
                generate_logs=generate_logs,
            )
            rvs.append((req_v, req_satisfied))
        if return_full_validation_results:
            return rvs
        else:
            return [b for (_, b) in rvs]

    def req(self, *args, **kwargs):
        """Shorthand for Requirement.__init__(...)."""
        return req(*args, **kwargs)

    def check(self, *args, **kwargs):
        """Shorthand for Requirement.__init__(..., check_only=True)."""
        return check(*args, **kwargs)

    def load_default_aloras(self):
        """Loads the default Aloras for this model, if they exist and if the backend supports."""
        if self.backend.model_id == IBM_GRANITE_3_2_8B and isinstance(
            self.backend, LocalHFBackend
        ):
            add_granite_aloras(self.backend)
            return
        self._session_logger.warning(
            "This model/backend combination does not support any aloras."
        )

    def genslot(
        self,
        gen_slot: Component,
        model_options: dict | None = None,
        format: type[BaseModelSubclass] | None = None,
        tool_calls: bool = False,
    ) -> ModelOutputThunk:
        """Call generative Slot on a GenerativeSlot Component.

        Args:
            gen_slot (GenerativeSlot Component): A generative slot

        Returns:
            ModelOutputThunk: Output thunk
        """
        result: ModelOutputThunk = self.backend.generate_from_context(
            action=gen_slot,
            ctx=self.ctx,
            model_options=model_options,
            format=format,
            tool_calls=tool_calls,
        )
        return result

    def query(
        self,
        obj: Any,
        query: str,
        *,
        format: type[BaseModelSubclass] | None = None,
        model_options: dict | None = None,
        tool_calls: bool = False,
    ) -> ModelOutputThunk:
        """Query method for retrieving information from an object.

        Args:
            obj : The object to be queried. It should be an instance of MObject or can be converted to one if necessary.
            query:  The string representing the query to be executed against the object.
            format:  format for output parsing.
            model_options: Model options to pass to the backend.
            tool_calls: If true, the model may make tool calls. Defaults to False.

        Returns:
            ModelOutputThunk: The result of the query as processed by the backend.
        """
        if not isinstance(obj, MObjectProtocol):
            obj = mify(obj)

        assert isinstance(obj, MObjectProtocol)
        q = obj.get_query_object(query)

        generate_logs: list[GenerateLog] = []
        answer = self.backend.generate_from_context(
            q,
            self.ctx,
            format=format,
            model_options=model_options,
            generate_logs=generate_logs,
            tool_calls=tool_calls,
        )
        # make sure that the last and only Log is marked as the one related to result
        assert len(generate_logs) == 1, "Simple call can only add one generate_log"
        generate_logs[0].is_final_result = True

        if isinstance(self.ctx, SimpleContext):
            self.ctx.insert_turn(ContextTurn(q, answer), generate_logs=generate_logs)
        elif isinstance(self.ctx, LinearContext) and len(self.ctx._ctx) == 0:
            FancyLogger.get_logger().info(
                "Adding the Object Query and its answer as first turn to a Linear Context (Chat History). "
                "You can now run more .chat() or .instruct() with the object as reference."
            )
            self.ctx.insert_turn(ContextTurn(q, answer), generate_logs=generate_logs)
        else:
            FancyLogger.get_logger().info(
                "The Linear Context has not been modified by this query."
            )

        return answer

    def transform(
        self,
        obj: Any,
        transformation: str,
        *,
        format: type[BaseModelSubclass] | None = None,
        model_options: dict | None = None,
    ) -> ModelOutputThunk | Any:
        """Transform method for creating a new object with the transformation applied.

        Args:
            obj : The object to be queried. It should be an instance of MObject or can be converted to one if necessary.
            transformation:  The string representing the query to be executed against the object.

        Returns:
            ModelOutputThunk|Any: The result of the transformation as processed by the backend. If no tools were called,
            the return type will be always be ModelOutputThunk. If a tool was called, the return type will be the return type
            of the function called, usually the type of the object passed in.
        """
        if not isinstance(obj, MObjectProtocol):
            obj = mify(obj)

        assert isinstance(obj, MObjectProtocol)
        t = obj.get_transform_object(transformation)

        generate_logs: list[GenerateLog] = []

        # Check that your model / backend supports tool calling.
        # This might throw an error when tools are provided but can't be handled by one or the other.
        transformed = self.backend.generate_from_context(
            t,
            self.ctx,
            format=format,
            model_options=model_options,
            generate_logs=generate_logs,
            tool_calls=True,
        )

        assert len(generate_logs) == 1, "Simple call can only add one generate_log"
        generate_logs[0].is_final_result = True

        # Insert the new turn into the context. Tool calls are handled afterwards.
        insert = False
        if isinstance(self.ctx, SimpleContext):
            insert = True
            self.ctx.insert_turn(
                ContextTurn(t, transformed), generate_logs=generate_logs
            )
        elif isinstance(self.ctx, LinearContext) and len(self.ctx._ctx) == 0:
            insert = True
            FancyLogger.get_logger().info(
                "Adding the Object Transform and its result as first turn to a Linear Context (Chat History). "
                "You can now run more .chat() or .instruct() with the object as reference."
            )
            self.ctx.insert_turn(
                ContextTurn(t, transformed), generate_logs=generate_logs
            )
        else:
            FancyLogger.get_logger().info(
                "The Linear Context has not been modified by this query."
            )

        tools = self._call_tools(transformed)

        # Transform only supports calling one tool call since it cannot currently synthesize multiple outputs.
        # Attempt to choose the best one to call.
        chosen_tool: ToolMessage | None = None
        if len(tools) == 1:
            # Only one function was called. Choose that one.
            chosen_tool = tools[0]

        elif len(tools) > 1:
            for output in tools:
                if type(output._tool_output) is type(obj):
                    chosen_tool = output
                    break

            if chosen_tool is None:
                chosen_tool = tools[0]

            FancyLogger.get_logger().warning(
                f"multiple tool calls returned in transform of {obj} with description '{transformation}'; picked `{chosen_tool.name}`"  # type: ignore
            )

        if chosen_tool:
            # Tell the user the function they should've called if no generated values were added.
            if len(chosen_tool._tool.args.keys()) == 0:
                FancyLogger.get_logger().warning(
                    f"the transform of {obj} with transformation description '{transformation}' resulted in a tool call with no generated arguments; consider calling the function `{chosen_tool._tool.name}` directly"
                )
            if insert:
                self.ctx.insert(chosen_tool)
                FancyLogger.get_logger().warning(
                    "added a tool message from transform to the context as well."
                )
            return chosen_tool._tool_output

        return transformed

    def _call_tools(self, result: ModelOutputThunk) -> list[ToolMessage]:
        """Call all the tools requested in a result's tool calls object.

        Returns:
            list[ToolMessage]: A list of tool messages that can be empty.
        """
        # There might be multiple tool calls returned.
        outputs: list[ToolMessage] = []
        tool_calls = result.tool_calls
        if tool_calls:
            # Call the tools and decide what to do.
            for name, tool in tool_calls.items():
                try:
                    output = tool.call_func()
                except Exception as e:
                    output = e

                content = str(output)
                if isinstance(self.backend, FormatterBackend):
                    content = self.backend.formatter.print(output)  # type: ignore

                outputs.append(
                    ToolMessage(
                        role="tool",
                        content=content,
                        tool_output=output,
                        name=name,
                        args=tool.args,
                        tool=tool,
                    )
                )
        return outputs

    # ###############################
    #  Convenience functions
    # ###############################

    def last_prompt(self) -> str | list[dict] | None:
        """Returns the last prompt that has been called from the session context.

        Returns:
            A string if the last prompt was a raw call to the model OR a list of messages (as role-msg-dicts). Is None if none could be found.
        """
        _, log = self.ctx.last_output_and_logs()

        prompt = None
        if isinstance(log, GenerateLog):
            prompt = log.prompt
        elif isinstance(log, list):
            last_el = log[-1]
            if isinstance(last_el, GenerateLog):
                prompt = last_el.prompt
        return prompt
