"""Question answering over a graph."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from arango import AQLQueryExecuteError, AQLQueryExplainError
from langchain.chains.base import Chain
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage
from langchain_core.prompts import BasePromptTemplate
from langchain_core.runnables import Runnable
from pydantic import Field

from langchain_arangodb.chains.graph_qa.prompts import (
    AQL_FIX_PROMPT,
    AQL_GENERATION_PROMPT,
    AQL_QA_PROMPT,
)
from langchain_arangodb.graphs.graph_store import GraphStore

AQL_WRITE_OPERATIONS: List[str] = [
    "INSERT",
    "UPDATE",
    "REPLACE",
    "REMOVE",
    "UPSERT",
]


class ArangoGraphQAChain(Chain):
    """Chain for question-answering against a graph by generating AQL statements.

    *Security note*: Make sure that the database connection uses credentials
        that are narrowly-scoped to only include necessary permissions.
        Failure to do so may result in data corruption or loss, since the calling
        code may attempt commands that would result in deletion, mutation
        of data if appropriately prompted or reading sensitive data if such
        data is present in the database.
        The best way to guard against such negative outcomes is to (as appropriate)
        limit the permissions granted to the credentials used with this tool.

        See https://python.langchain.com/docs/security for more information.
    """

    graph: GraphStore = Field(exclude=True)
    aql_generation_chain: Runnable[Dict[str, Any], Any]
    aql_fix_chain: Runnable[Dict[str, Any], Any]
    qa_chain: Runnable[Dict[str, Any], Any]
    input_key: str = "query"  #: :meta private:
    output_key: str = "result"  #: :meta private:

    top_k: int = 10
    """Number of results to return from the query"""
    aql_examples: str = ""
    """Specifies the set of AQL Query Examples that promote few-shot-learning"""
    return_aql_query: bool = False
    """ Specify whether to return the AQL Query in the output dictionary"""
    return_aql_result: bool = False
    """Specify whether to return the AQL JSON Result in the output dictionary"""
    max_aql_generation_attempts: int = 3
    """Specify the maximum amount of AQL Generation attempts that should be made"""
    execute_aql_query: bool = True
    """If False, the AQL Query is only explained & returned, not executed"""
    allow_dangerous_requests: bool = False
    """Forced user opt-in to acknowledge that the chain can make dangerous requests."""
    output_list_limit: int = 32
    """Maximum list length to include in the response prompt. Truncated if longer."""
    output_string_limit: int = 256
    """Maximum string length to include in the response prompt. Truncated if longer."""
    force_read_only_query: bool = False
    """If True, the query is checked for write operations and raises an
    error if a write operation is detected."""

    """
    *Security note*: Make sure that the database connection uses credentials
        that are narrowly-scoped to only include necessary permissions.
        Failure to do so may result in data corruption or loss, since the calling
        code may attempt commands that would result in deletion, mutation
        of data if appropriately prompted or reading sensitive data if such
        data is present in the database.
        The best way to guard against such negative outcomes is to (as appropriate)
        limit the permissions granted to the credentials used with this tool.

        See https://python.langchain.com/docs/security for more information.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the chain."""
        super().__init__(**kwargs)
        if self.allow_dangerous_requests is not True:
            raise ValueError(
                "In order to use this chain, you must acknowledge that it can make "
                "dangerous requests by setting `allow_dangerous_requests` to `True`."
                "You must narrowly scope the permissions of the database connection "
                "to only include necessary permissions. Failure to do so may result "
                "in data corruption or loss or reading sensitive data if such data is "
                "present in the database."
                "Only use this chain if you understand the risks and have taken the "
                "necessary precautions. "
                "See https://python.langchain.com/docs/security for more information."
            )

    @property
    def input_keys(self) -> List[str]:
        """Get the input keys for the chain."""
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Get the output keys for the chain."""
        return [self.output_key]

    @property
    def _chain_type(self) -> str:
        """Get the chain type."""
        return "graph_aql_chain"

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        *,
        qa_prompt: Optional[BasePromptTemplate] = None,
        aql_generation_prompt: Optional[BasePromptTemplate] = None,
        aql_fix_prompt: Optional[BasePromptTemplate] = None,
        **kwargs: Any,
    ) -> ArangoGraphQAChain:
        """Initialize from LLM.

        :param llm: The language model to use.
        :type llm: BaseLanguageModel
        :param qa_prompt: The prompt to use for the QA chain.
        :type qa_prompt: BasePromptTemplate
        :param aql_generation_prompt: The prompt to use for the AQL generation chain.
        :type aql_generation_prompt: BasePromptTemplate
        :param aql_fix_prompt: The prompt to use for the AQL fix chain.
        :type aql_fix_prompt: BasePromptTemplate
        :param kwargs: Additional keyword arguments.
        :type kwargs: Any
        :return: The initialized ArangoGraphQAChain.
        :rtype: ArangoGraphQAChain
        :raises ValueError: If the LLM is not provided.
        """
        if qa_prompt is None:
            qa_prompt = AQL_QA_PROMPT
        if aql_generation_prompt is None:
            aql_generation_prompt = AQL_GENERATION_PROMPT
        if aql_fix_prompt is None:
            aql_fix_prompt = AQL_FIX_PROMPT

        qa_chain = qa_prompt | llm
        aql_generation_chain = aql_generation_prompt | llm
        aql_fix_chain = aql_fix_prompt | llm

        return cls(
            qa_chain=qa_chain,
            aql_generation_chain=aql_generation_chain,
            aql_fix_chain=aql_fix_chain,
            **kwargs,
        )

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        """
        Generate an AQL statement from user input, use it retrieve a response
        from an ArangoDB Database instance, and respond to the user input
        in natural language.

        Users can modify the following ArangoGraphQAChain Class Variables:

        :param top_k: The maximum number of AQL Query Results to return
        :type top_k: int

        :param aql_examples: A set of AQL Query Examples that are passed to
            the AQL Generation Prompt Template to promote few-shot-learning.
            Defaults to an empty string.
        :type aql_examples: str

        :param return_aql_query: Whether to return the AQL Query in the
            output dictionary. Defaults to False.
        :type return_aql_query: bool

        :param return_aql_result: Whether to return the AQL Query in the
            output dictionary. Defaults to False
        :type return_aql_result: bool

        :param max_aql_generation_attempts: The maximum amount of AQL
            Generation attempts to be made prior to raising the last
            AQL Query Execution Error. Defaults to 3.
        :type max_aql_generation_attempts: int

        :param execute_aql_query: If False, the AQL Query is only
            explained & returned, not executed. Defaults to True.
        :type execute_aql_query: bool

        :param output_list_limit: The maximum list length to display
            in the output. If the list is longer, it will be truncated.
            Defaults to 32.
        :type output_list_limit: int

        :param output_string_limit: The maximum string length to display
            in the output. If the string is longer, it will be truncated.
            Defaults to 256.
        :type output_string_limit: int
        """
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()
        user_input = inputs[self.input_key]

        ######################
        # Generate AQL Query #
        ######################

        aql_generation_output = self.aql_generation_chain.invoke(
            {
                "adb_schema": self.graph.schema_yaml,
                "aql_examples": self.aql_examples,
                "user_input": user_input,
            },
            callbacks=callbacks,
        )

        aql_query = ""
        aql_error = ""
        aql_result = None
        aql_generation_attempt = 1

        aql_execution_func = (
            self.graph.query if self.execute_aql_query else self.graph.explain
        )

        while (
            aql_result is None
            and aql_generation_attempt < self.max_aql_generation_attempts + 1
        ):
            if isinstance(aql_generation_output, str):
                aql_generation_output_content = aql_generation_output
            elif isinstance(aql_generation_output, AIMessage):
                aql_generation_output_content = str(aql_generation_output.content)
            else:
                m = f"Invalid AQL Generation Output: {aql_generation_output} (type: {type(aql_generation_output)})"  # noqa: E501
                raise ValueError(m)

            #####################
            # Extract AQL Query #
            #####################

            pattern = r"```(?i:aql)?(.*?)```"
            matches: List[str] = re.findall(
                pattern, aql_generation_output_content, re.DOTALL
            )

            if not matches:
                _run_manager.on_text(
                    "Invalid Response: ", end="\n", verbose=self.verbose
                )

                _run_manager.on_text(
                    aql_generation_output_content,
                    color="red",
                    end="\n",
                    verbose=self.verbose,
                )

                m = f"Unable to extract AQL Query from response: {aql_generation_output_content}"  # noqa: E501
                raise ValueError(m)

            aql_query = matches[0].strip()

            if self.force_read_only_query:
                is_read_only, write_operation = self._is_read_only_query(aql_query)

                if not is_read_only:
                    error_msg = f"""
                        Security violation: Write operations are not allowed.
                        Detected write operation in query: {write_operation}
                    """
                    raise ValueError(error_msg)

            _run_manager.on_text(
                f"AQL Query ({aql_generation_attempt}):", verbose=self.verbose
            )
            _run_manager.on_text(
                aql_query, color="green", end="\n", verbose=self.verbose
            )

            #############################
            # Execute/Explain AQL Query #
            #############################

            try:
                params = {
                    "top_k": self.top_k,
                    "list_limit": self.output_list_limit,
                    "string_limit": self.output_string_limit,
                }

                aql_result = aql_execution_func(aql_query, params)
            except (AQLQueryExecuteError, AQLQueryExplainError) as e:
                aql_error = str(e.error_message)

                _run_manager.on_text(
                    "AQL Query Execution Error: ", end="\n", verbose=self.verbose
                )
                _run_manager.on_text(
                    aql_error, color="yellow", end="\n\n", verbose=self.verbose
                )

                ########################
                # Retry AQL Generation #
                ########################

                aql_generation_output = self.aql_fix_chain.invoke(
                    {
                        "adb_schema": self.graph.schema_yaml,
                        "aql_query": aql_query,
                        "aql_error": aql_error,
                    },
                    callbacks=callbacks,
                )

            aql_generation_attempt += 1

        if aql_result is None:
            m = f"""
                Maximum amount of AQL Query Generation attempts reached.
                Unable to execute the AQL Query due to the following error:
                {aql_error}
            """
            raise ValueError(m)

        text = "AQL Result:" if self.execute_aql_query else "AQL Explain:"
        _run_manager.on_text(text, end="\n", verbose=self.verbose)
        _run_manager.on_text(
            str(aql_result), color="green", end="\n", verbose=self.verbose
        )

        if not self.execute_aql_query:
            result = {self.output_key: aql_query, "aql_result": aql_result}

            return result

        ########################
        # Interpret AQL Result #
        ########################

        result = self.qa_chain.invoke(  # type: ignore
            {
                "adb_schema": self.graph.schema_yaml,
                "user_input": user_input,
                "aql_query": aql_query,
                "aql_result": aql_result,
            },
            callbacks=callbacks,
        )

        results: Dict[str, Any] = {self.output_key: result}

        if self.return_aql_query:
            results["aql_query"] = aql_generation_output

        if self.return_aql_result:
            results["aql_result"] = aql_result

        return results

    def _is_read_only_query(self, aql_query: str) -> Tuple[bool, Optional[str]]:
        """Check if the AQL query is read-only.

        :param aql_query: The AQL query to check.
        :type aql_query: str

        :return: True if the query is read-only, False otherwise.
        :rtype: Tuple[bool, Optional[str]]
        """
        normalized_query = aql_query.upper()

        for op in AQL_WRITE_OPERATIONS:
            if op in normalized_query:
                return False, op

        return True, None
