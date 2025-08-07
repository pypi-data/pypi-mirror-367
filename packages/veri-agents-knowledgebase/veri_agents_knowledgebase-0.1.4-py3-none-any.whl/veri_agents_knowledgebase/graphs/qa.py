import logging
from datetime import datetime
from typing import Sequence, Callable

from langchain_core.language_models import (
    LanguageModelLike,
)
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode, create_react_agent
from langchain_core.tools import BaseTool

from veri_agents_knowledgebase import Knowledgebase

log = logging.getLogger(__name__)


def create_qa_agent(
    llm: LanguageModelLike,
    knowledgebases: Sequence[Knowledgebase],
    system_prompt: str,
    tools: Sequence[BaseTool | Callable] | None = None,
    **react_kwargs,
) -> CompiledGraph:
    tools = list(tools) if tools else []
    for i, knowledgebase in enumerate(knowledgebases):
        tools.extend(
            knowledgebase.get_tools(
                retrieve_tools=True,
                list_tools=True,
                write_tools=False,
            ))
    tool_node = ToolNode(tools)

    system_prompt = system_prompt
    system_prompt += f"""Today's date is: {datetime.now().strftime("%Y-%m-%d")}."""

    return create_react_agent(
        model=llm, tools=tool_node, prompt=system_prompt, **react_kwargs
    )
