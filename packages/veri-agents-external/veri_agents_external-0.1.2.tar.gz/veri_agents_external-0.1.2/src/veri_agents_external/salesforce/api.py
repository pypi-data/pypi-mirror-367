from datetime import datetime
import os
import logging
from typing import List, Optional

import requests
from pydantic import BaseModel, Field
from simple_salesforce.api import Salesforce

log = logging.getLogger(__name__)


class KnowledgeArticle(BaseModel):
    """
    Pydantic model to represent a Salesforce Knowledge Article.
    Uses Field aliases to map from Salesforce API names to Python-friendly names.
    """

    knowledge_article_id: str = Field(..., alias="KnowledgeArticleId")
    title: Optional[str] = Field(None, alias="Title")
    summary: Optional[str] = Field(None, alias="Summary")
    body: Optional[str] = Field(None, alias="Body__c")
    problem: Optional[str] = Field(None, alias="Problem__c")
    cause: Optional[str] = Field(None, alias="Cause__c")
    solution: Optional[str] = Field(None, alias="Solution__c")
    public_article_link: Optional[str] = Field(None, alias="Public_Article_Link__c")
    product: Optional[str] = Field(None, alias="Product__c")
    marketing_product: Optional[str] = Field(None, alias="Marketing_Product__c")
    question: Optional[str] = Field(None, alias="Question__c")
    answer: Optional[str] = Field(None, alias="Answer__c")
    description: Optional[str] = Field(None, alias="Description__c")
    instructions: Optional[str] = Field(None, alias="Instructions__c")
    release_notes: Optional[str] = Field(None, alias="Release_Notes__c")


class Case(BaseModel):
    """
    Pydantic model to represent a Salesforce Case (Ticket).
    """

    id: str = Field(..., alias="Id")
    case_number: Optional[str] = Field(None, alias="CaseNumber")
    subject: Optional[str] = Field(None, alias="Subject")
    status: Optional[str] = Field(None, alias="Status")
    priority: Optional[str] = Field(None, alias="Priority")
    origin: Optional[str] = Field(None, alias="Origin")
    type: Optional[str] = Field(None, alias="Type")
    description: Optional[str] = Field(None, alias="Description")
    created_date: str = Field(..., alias="CreatedDate")
    closed_date: Optional[str] = Field(None, alias="ClosedDate")
    is_closed: bool = Field(..., alias="IsClosed")
    is_escalated: bool = Field(..., alias="IsEscalated")
    contact_email: Optional[str] = Field(None, alias="ContactEmail")
    products: Optional[str] = Field(None, alias="Products__c")


class SuggestedArticle(BaseModel):
    Id: str
    Title: Optional[str]


class CaseArticleRecommendation(BaseModel):
    Id: str
    RecommendationAction: Optional[str]
    RecommendationType: Optional[str]
    SuggestedArticleId: Optional[str]
    SuggestedArticle: Optional[SuggestedArticle]
    CreatedDate: datetime


class CaseArticleRecommendationResponse(BaseModel):
    totalSize: int
    done: bool
    records: List[CaseArticleRecommendation]


class SalesforceConnection:
    """
    Handles the connection and authentication with the Salesforce API.
    """

    def __init__(self, client_id: str, client_secret: str, token_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.sf = self._connect()

    def is_connected(self) -> bool:
        """
        Checks if the Salesforce connection is established.
        Returns:
            bool: True if connected, False otherwise.
        """
        return self.sf is not None

    def _connect(self):
        """
        Establishes the connection to Salesforce using client credentials.
        """
        log.info("Attempting to connect to Salesforce...")
        try:
            payload = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
            response = requests.post(self.token_url, data=payload, timeout=10)
            response.raise_for_status()
            response_data = response.json()
            access_token = response_data.get("access_token")
            instance_url = response_data.get("instance_url").rstrip(
                "/"
            )  # Clean trailing slash if present

            if not access_token or not instance_url:
                raise ValueError(
                    "Access token or instance URL not found in the response."
                )

            log.info("Successfully obtained access token and instance URL.")
            return Salesforce(instance_url=instance_url, session_id=access_token)

        except requests.exceptions.RequestException as e:
            log.error(f"Error getting access token: {e}")
            return None
        except (ValueError, KeyError) as e:
            log.error(f"Error parsing authentication response: {e}")
            return None


def get_knowledge_articles(sf_connection, limit: int = 200000) -> List[KnowledgeArticle]:
    """
    Retrieves and validates knowledge articles from Salesforce.

    Returns:
        List[KnowledgeArticle]: A list of validated Pydantic models.
    """
    if not sf_connection.sf:
        log.error(
            "Cannot fetch knowledge articles: Salesforce connection is not available."
        )
        return []

    query = f"""
        SELECT
            KnowledgeArticleId, Title, Summary, Body__c, Problem__c, Cause__c, Solution__c,
            Public_Article_Link__c, Product__c, Marketing_Product__c, Question__c, Answer__c, Description__c,
            Instructions__c, Release_Notes__c
        FROM Knowledge__kav
        WHERE IsDeleted = false AND PublishStatus = 'Online' AND IsLatestVersion = true AND IsMasterLanguage = true
        LIMIT {limit}
    """
    try:
        log.info("\nQuerying for Knowledge Articles...")
        result = sf_connection.sf.query_all_iter(query)
        validated_articles = [KnowledgeArticle.model_validate(article) for article in result]
        return validated_articles
    except Exception as e:
        log.error(f"An error occurred while getting knowledge articles: {e}")
        return []


def get_cases(
    sf_connection: SalesforceConnection, days_ago: int = 30, limit: int = 100
) -> List[Case]:
    """
    Retrieves and validates cases (Tickets) from Salesforce.

    Returns:
        List[Case]: A list of validated Pydantic models.
    """
    if not sf_connection.sf:
        log.error("Cannot fetch tickets: Salesforce connection is not available.")
        return []

    query = f"""
        SELECT
            Id, CaseNumber, Subject, Status, Priority, Origin, Type, Description,
            CreatedDate, ClosedDate, IsClosed, IsEscalated, ContactEmail, Products__c
        FROM Case
        WHERE CreatedDate = LAST_N_DAYS:{days_ago}
        ORDER BY CreatedDate DESC
        LIMIT {limit}
    """
    try:
        log.info(f"\nQuerying for {limit} cases from the last {days_ago} days...")
        result = sf_connection.sf.query(query)
        case_data = result.get("records", [])
        log.info(f"Found {len(case_data)} cases. Validating...")
        validated_cases = [Case.model_validate(case) for case in case_data]
        return validated_cases
    except Exception as e:
        log.error(f"An error occurred while getting cases: {e}")
        return []


def get_case_by_id(
    sf_connection: SalesforceConnection, case_id: str
) -> Optional[Case]:
    """
    Retrieves and validates a single ticket (Case) from Salesforce by its ID.

    Args:
        sf_connection (Salesforce): An active simple_salesforce.Salesforce instance.
        ticket_id (str): The ID of the ticket to retrieve.

    Returns:
        Optional[Case]: A validated Pydantic model of the ticket, or None if not found.
    """
    if not sf_connection.sf:
        log.error("Cannot fetch ticket: Salesforce connection is not available.")
        return None

    # Sanitize case_id to prevent SOQL injection
    sanitized_case_id = case_id.replace("'", "\\'")

    query = f"""
        SELECT
            Id, CaseNumber, Subject, Status, Priority, Origin, Type, Description,
            CreatedDate, ClosedDate, IsClosed, IsEscalated, ContactEmail, Products__c
        FROM Case
        WHERE Id = '{sanitized_case_id}'
        LIMIT 1
    """
    try:
        log.info(f"\nQuerying for Case with ID: {case_id}...")
        result = sf_connection.sf.query(query)
        records = result.get("records", [])
        if not records:
            log.info(f"No ticket found with ID: {case_id}")
            return None

        ticket_data = records[0]
        log.info("Found ticket. Validating...")
        validated_ticket = Case.model_validate(ticket_data)
        return validated_ticket
    except Exception as e:
        log.error(f"An error occurred while getting case by ID: {e}")
        return None


def get_case_by_number(
    sf_connection: SalesforceConnection, case_number: str
) -> Optional[Case]:
    """
    Retrieves and validates a single ticket (Case) from Salesforce by its case number.

    Args:
        sf_connection (Salesforce): An active simple_salesforce.Salesforce instance.
        case_number (str): The case number of the ticket to retrieve.

    Returns:
        Optional[Case]: A validated Pydantic model of the ticket, or None if not found.
    """
    if not sf_connection.sf:
        log.error("Cannot fetch ticket: Salesforce connection is not available.")
        return None

    # Sanitize case_number to prevent SOQL injection
    sanitized_case_number = case_number.replace("'", "\\'")

    query = f"""
        SELECT
            Id, CaseNumber, Subject, Status, Priority, Origin, Type, Description,
            CreatedDate, ClosedDate, IsClosed, IsEscalated, ContactEmail, Products__c
        FROM Case
        WHERE CaseNumber = '{sanitized_case_number}'
        LIMIT 1
    """
    try:
        log.info(f"\nQuerying for Case with Case Number: {case_number}...")
        result = sf_connection.sf.query(query)
        records = result.get("records", [])
        if not records:
            log.info(f"No ticket found with Case Number: {case_number}")
            return None

        ticket_data = records[0]
        log.info("Found ticket. Validating...")
        validated_ticket = Case.model_validate(ticket_data)
        return validated_ticket
    except Exception as e:
        log.error(f"An error occurred while getting case by number: {e}")
        return None


def get_article_by_id(
    sf_connection: SalesforceConnection, article_id: str
) -> Optional[KnowledgeArticle]:
    """
    Retrieves and validates a single knowledge article from Salesforce by its ID.

    Args:
        sf_connection (Salesforce): An active simple_salesforce.Salesforce instance.
        article_id (str): The ID of the knowledge article to retrieve.

    Returns:
        Optional[KnowledgeArticle]: A validated Pydantic model of the article, or None if not found.
    """
    if not sf_connection.sf:
        log.error("Cannot fetch article: Salesforce connection is not available.")
        return None

    # Sanitize article_id to prevent SOQL injection
    sanitized_article_id = article_id.replace("'", "\\'")

    query = f"""
        SELECT
            KnowledgeArticleId, Title, Summary, Body__c, Problem__c, Cause__c, Solution__c,
            Public_Article_Link__c, Product__c, Question__c, Answer__c, Description__c,
            Instructions__c, Release_Notes__c
        FROM Knowledge__kav
        WHERE KnowledgeArticleId = '{sanitized_article_id}'
        LIMIT 1
    """
    try:
        log.info(f"\nQuerying for Article with ID: {article_id}...")
        result = sf_connection.sf.query(query)
        records = result.get("records", [])
        if not records:
            log.error(f"No article found with ID: {article_id}")
            return None

        article_data = records[0]
        log.info("Found article. Validating...")
        validated_article = KnowledgeArticle.model_validate(article_data)
        return validated_article
    except Exception as e:
        log.error(f"An error occurred while getting article by ID: {e}")
        return None


def get_article_recommendation(
    sf_connection: SalesforceConnection, ticket_id: str
) -> Optional[list[CaseArticleRecommendation]]:
    if not sf_connection.sf:
        log.error("Cannot fetch article: Salesforce connection is not available.")
        return None

    soql_query = f"""
    SELECT Id,
        RecommendationAction,
        RecommendationType,
        SuggestedArticleId,
        SuggestedArticle.Title,
        CreatedDate
    FROM CaseArticleRecommendation
    WHERE CaseId = '{ticket_id}'
    """

    try:
        results = sf_connection.sf.query_all(soql_query)
        parsed = CaseArticleRecommendationResponse(**results)
        return parsed.records
    except Exception as e:
        log.error(f"An error occurred while querying for article recommendations: {e}")
        return None


def describe_salesforce_object(sf_connection: SalesforceConnection, object_name: str) -> Optional[dict]:
    """
    Describes a Salesforce object and returns its field information.
    
    Args:
        sf_connection: An active SalesforceConnection instance
        object_name: The API name of the Salesforce object (e.g., 'Knowledge__kav', 'Case')
    
    Returns:
        Dictionary containing object description or None if error
    """
    if not sf_connection.sf:
        log.error(f"Cannot describe {object_name}: Salesforce connection is not available.")
        return None
    
    try:
        # Use getattr to access the object dynamically and call describe()
        obj = getattr(sf_connection.sf, object_name)
        description = obj.describe()
        return description
    except Exception as e:
        log.error(f"An error occurred while describing {object_name}: {e}")
        return None


def print_object_fields(sf_connection: SalesforceConnection, object_name: str):
    """
    Prints all fields of a Salesforce object in a readable format.
    
    Args:
        sf_connection: An active SalesforceConnection instance
        object_name: The API name of the Salesforce object
    """
    print(f"\n=== {object_name} Object Fields ===")
    description = describe_salesforce_object(sf_connection, object_name)
    
    if not description:
        print(f"Failed to retrieve description for {object_name}")
        return
    
    fields = description.get('fields', [])
    print(f"Object Label: {description.get('label', 'N/A')}")
    print(f"Total Fields: {len(fields)}")
    print("\nFields:")
    print("-" * 80)
    
    for field in sorted(fields, key=lambda x: x['name']):
        field_name = field.get('name', 'N/A')
        field_label = field.get('label', 'N/A')
        field_type = field.get('type', 'N/A')
        is_custom = field.get('custom', False)
        is_required = not field.get('nillable', True)
        
        custom_indicator = " [CUSTOM]" if is_custom else ""
        required_indicator = " [REQUIRED]" if is_required else ""
        
        print(f"  {field_name:<30} | {field_type:<15} | {field_label}{custom_indicator}{required_indicator}")
    
    print("-" * 80)


if __name__ == "__main__":
    CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET")
    TOKEN_URL = os.getenv("SALESFORCE_TOKEN_URL")
    if not CLIENT_ID or not CLIENT_SECRET or not TOKEN_URL:
        raise ValueError(
            "Please set the SALESFORCE_CLIENT_ID and SALESFORCE_CLIENT_SECRET environment variables."
        )

    sf_conn = SalesforceConnection(CLIENT_ID, CLIENT_SECRET, TOKEN_URL)

    products = set()
    unknown_products = []

    if sf_conn.sf:
        # Print all fields for Knowledge__kav and Case objects
        print_object_fields(sf_conn, "Knowledge__kav")
        print_object_fields(sf_conn, "Case")
        
        articles = get_knowledge_articles(sf_conn)
        if articles:
            print("\n--- Recently Found Knowledge Articles ---")
            for i, article in enumerate(articles):
                if i <= 3:
                    print(f"Title: {article.title}")
                    print(f"Summary: {article.summary}")
                    print(f"Body: {article.body[:100] if article.body else 'N/A'}...")
                    print(f"Problem: {article.problem}")
                    print(f"Cause: {article.cause}")
                    print(f"Solution: {article.solution}")
                    print(f"Public Article Link: {article.public_article_link}")
                    print(f"Product: {article.product}")
                    print(f"Marketing product: {article.marketing_product}")
                    print(f"Question: {article.question}")
                    print(f"Answer: {article.answer}")
                    print(f"Description: {article.description}")
                    print(f"Instructions: {article.instructions}")
                    print(f"Release Notes: {article.release_notes}")
                    print("-" * 20)

                if article.marketing_product:
                    for p in article.marketing_product.split(";"):
                        if p:
                            products.add(p.strip())
                else:
                    unknown_products.append(article.title)

        print(f"Found {len(articles)} knowledge articles."  )
        tickets = get_cases(sf_conn, days_ago=90, limit=3)
        if tickets:
            print("\n--- Recently Created Cases ---")
            for ticket in tickets:
                # Accessing data via model attributes
                print(f"  Case Number: {ticket.case_number}")
                print(f"    Subject: {ticket.subject}")
                print(f"    Status: {ticket.status}")
                print(f"    Products: {ticket.products}")
                if ticket.description:
                    print(f"    Description: {ticket.description[:100]}")
                print("-" * 20)

            # --- Example: Retrieve a specific ticket by its ID ---
            first_ticket_id = tickets[0].id
            specific_ticket = get_case_by_id(sf_conn, first_ticket_id)
            if specific_ticket:
                print("\n--- Details for Specific Cases ---")
                print(f"  Case Number: {specific_ticket.case_number}")
                if specific_ticket.description:
                    print(f"    Description: {specific_ticket.description[:100]}")
                # print(specific_ticket)
                print("-" * 20)

            print(f"Found {len(tickets)} tickets in the last 90 days.")

            # ---- Example: Retrieve knowledge article recommendations for this specific ticket
            #article_recommendation = get_article_recommendation(
            #    sf_conn, first_ticket_id
            #)
            #if article_recommendation:
            #    print("\n--- Article Recommendation for Specific Cases ---")
            #    print(article_recommendation)
            #    print("-" * 20)

    print(f"Products: {', '.join(products)}")
    print(f"Unknown product for {len(unknown_products)} articles")
    print(f"Unknown products: {', '.join(unknown_products[:30])}")
