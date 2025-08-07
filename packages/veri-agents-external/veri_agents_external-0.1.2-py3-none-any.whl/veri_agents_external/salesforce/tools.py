import requests
import logging
from typing import Optional, Tuple, Type, cast

from langchain_core.tools import BaseTool, ToolException, InjectedToolArg
from typing_extensions import Annotated
from pydantic import BaseModel, Field
from datetime import datetime

from .api import (
    SalesforceConnection,
    get_cases,
    get_case_by_number,
    # get_knowledge_articles,
    get_article_by_id,
)

log = logging.getLogger(__name__)


def filter_none_values(data) -> dict | list:
    if isinstance(data, dict):
        return {k: filter_none_values(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [filter_none_values(item) for item in data]
    return data


class SalesforceToolInput(BaseModel):
    """Input for the Salesforce tool."""

    query: str = Field(
        description="Salesforce SQL query to execute. Use SOQL (Salesforce Object Query Language) syntax."
    )


class SalesforceTool(BaseTool):
    """Generic Salesforce API tool.

    Typically used as base class for more specialized Salesforce tools.
    """

    salesforce_client_id: str
    """ The client ID for Salesforce API access. """

    salesforce_client_secret: str
    """ The client secret for Salesforce API access. """

    salesforce_token_url: str
    """ The token URL for Salesforce API access. This is typically the OAuth token endpoint. """

    name: str = "salesforce_tool"
    description: str = "Performs Salesforce queries. Use this tool if you have no other, more specialized Salesforce tool."
    #args_schema = SalesforceToolInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    allow_mutation: bool = False

    def _connect(self) -> SalesforceConnection:
        sf = SalesforceConnection(
            token_url=self.salesforce_token_url,
            client_id=self.salesforce_client_id,
            client_secret=self.salesforce_client_secret,
        )

        if not sf.is_connected():
            raise ToolException(
                "Salesforce connection failed. Please check your credentials."
            )

        return sf
        # articles = get_knowledge_articles(sf, limit=50000)

    # def _run(
    #     self,
    #     gql_query: str,
    #     # aiware_api_key: Annotated[Optional[str], InjectedToolArg]
    # ) -> Tuple[str, dict]:
    #     """Run the aiWARE GraphQL query."""
    #     aiware_api_key = None
    #     result = self._run_query(gql_query, aiware_api_key)
    #     return str(result), {"items": result, "type": "json", "source": "aiware"}


class SalesforceGetRecentCasesInput(BaseModel):
    """Input for the Salesforce Get Recent Tickets tool."""

    days_ago: int = Field(
        default=90,
        description="Number of days ago to look for cases. For example, if you want to get cases from the last 7 days, set this to 7. Default is 90 days.",
    )
    limit: int = Field(
        default=10, description="Maximum number of cases to return. Default is 10."
    )


class SalesforceGetRecentCases(SalesforceTool):
    """Tool to get recent Salesforce cases."""

    name: str = "salesforce_recent_cases"
    description: str = "Get recent Salesforce cases. Use this tool to get cases from the last N days. The result is a list of cases with contents."
    args_schema = SalesforceGetRecentCasesInput

    def _run(self, days_ago: int = 90, limit: int = 10) -> Tuple[str, dict]:
        sf = self._connect()
        result = get_cases(sf, days_ago=days_ago, limit=limit)
        # convert list of tickets to json
        results_json = [result.model_dump() for result in result]
        return str(results_json), {
            "items": results_json,
            "type": "json",
            "source": "salesforce",
        }


class SalesforceGetCaseByNumberInput(BaseModel):
    case_number: str = Field(
        description="Case number of the ticket to retrieve. This is the Salesforce case number of the requested case."
    )


class SalesforceGetCaseByNumber(SalesforceTool):
    """Tool to get a Salesforce ticket by case number."""

    name: str = "salesforce_case_by_number"
    description: str = "Get a Salesforce case by number. Use this tool to get the contents of a specific case."
    args_schema = SalesforceGetCaseByNumberInput

    def _run(self, case_number: str) -> Tuple[str, dict]:
        sf = self._connect()
        result = get_case_by_number(sf, case_number)
        if not result:
            raise ToolException(f"Case with ID {case_number} not found.")
        return str(result.model_dump()), {
            "item": result.model_dump(),
            "type": "json",
            "source": "salesforce",
        }


class SalesforceGetArticleByIdInput(BaseModel):
    article_id: str = Field(
        description="ID of the article to retrieve. This is the Salesforce ID of the article."
    )


class SalesforceGetArticleById(SalesforceTool):
    """Tool to get a Salesforce article by ID."""

    name: str = "salesforce_article_by_id"
    description: str = "Get a Salesforce article by ID. Use this tool to get the contents of a specific article."
    args_schema = SalesforceGetArticleByIdInput

    def _run(self, article_id: str) -> Tuple[str, dict]:
        sf = self._connect()
        result = get_article_by_id(sf, article_id)
        if not result:
            raise ToolException(f"Article with ID {article_id} not found.")
        return str(result.model_dump()), {
            "item": result.model_dump(),
            "type": "json",
            "source": "salesforce",
        }
