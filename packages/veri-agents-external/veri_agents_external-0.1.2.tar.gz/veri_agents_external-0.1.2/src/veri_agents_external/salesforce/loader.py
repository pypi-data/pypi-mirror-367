import logging
import os
from datetime import datetime
from typing import Iterator, cast

from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from veri_agents_knowledgebase.knowledgebase import DataSource, DocumentLoader

from .api import SalesforceConnection, get_knowledge_articles

log = logging.getLogger(__name__)


class SalesforceDataSource(DataSource):
    client_id: str
    """ The client ID for Salesforce API access. """

    client_secret: str
    """ The client secret for Salesforce API access. """


class SalesforceSupportDocumentLoader(DocumentLoader):
    def __init__(
        self, data_source: SalesforceDataSource, load_all_products: bool = False
    ):
        super().__init__(data_source)
        self.load_all_products = load_all_products

        self.product_name_map = {
            "aiWare - aiWare": "aiWare",
            "aiWare - Automate Studio": "Automate",
            "Contact App": "Contact",
            "GLC - Redaction Managed Service (RMS)": "Redact",
            "Relativity (integration)": "Relativity",
        }
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=200
        )

    def _parse_html(self, text: str | None) -> str:
        if not text:
            return ""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()

    def _split(self, text: str, metadata: dict):
        doc = Document(page_content=text, metadata=metadata)
        new_docs = self.splitter.split_documents([doc])
        return new_docs

    def _add(
        self,
        parent_doc: Document,
        docs: list[Document],
        text: str,
        fieldname: str | None,
        metadata: dict,
    ):
        if text:
            if fieldname:
                parent_doc.page_content += f"{fieldname}: {text}\n"
            else:
                parent_doc.page_content += f"{text}\n"
            new_docs = self._split(text, metadata)
            docs.extend(new_docs)

    def load_documents(
        self, **kwargs
    ) -> Iterator[tuple[Document, list[Document] | None]]:
        products_to_include = []

        if "products" in kwargs:
            products_to_include = kwargs["products"]

        data_source = cast(SalesforceDataSource, self.data_source)
        sf = SalesforceConnection(
            token_url=str(data_source.location),
            client_id=data_source.client_id,
            client_secret=data_source.client_secret,
        )

        if not sf.is_connected():
            raise ValueError(
                "Salesforce connection failed. Please check your credentials."
            )

        articles = get_knowledge_articles(sf, limit=50000)

        log.info("Found %d knowledge articles in Salesforce.", len(articles))

        if not articles:
            raise ValueError("No knowledge articles found in Salesforce.")

        for article in articles:
            summary = self._parse_html(article.summary)
            content = self._parse_html(article.body)
            problem = self._parse_html(article.problem)
            cause = self._parse_html(article.cause)
            solution = self._parse_html(article.solution)
            question = self._parse_html(article.question)
            answer = self._parse_html(article.answer)
            description = self._parse_html(article.description)
            instructions = self._parse_html(article.instructions)
            release_notes = self._parse_html(article.release_notes)
            title = article.title or "Untitled"
            link = article.public_article_link or "none"
            product = article.marketing_product or ""

            # TODO: images? docling?

            # TODO: can we use a metadata filter that can handle this
            product_list = product.split(";")
            for product in product_list:
                if not product:
                    continue
                product = self.product_name_map.get(product, product)
                if (
                    not self.load_all_products
                    and products_to_include
                    and product not in products_to_include
                ):
                    continue

                docs: list[Document] = []
                metadata = {
                    "source": f"{article.knowledge_article_id}_{product}",
                    "title": title,
                    "product": product,
                    "link": link,
                    "last_updated": datetime.now().isoformat(),
                }
                # Title as a separate document because we want to use ParentRetriever
                parent_doc = Document(page_content="", metadata=metadata)
                self._add(parent_doc, docs, title, "Title", metadata)
                self._add(parent_doc, docs, summary, "Summary", metadata)
                self._add(parent_doc, docs, problem, "Problem", metadata)
                self._add(parent_doc, docs, cause, "Cause", metadata)
                self._add(parent_doc, docs, solution, "Solution", metadata)
                self._add(parent_doc, docs, question, "Question", metadata)
                self._add(parent_doc, docs, answer, "Answer", metadata)
                self._add(parent_doc, docs, description, "Description", metadata)
                self._add(parent_doc, docs, instructions, "Instruction", metadata)
                self._add(parent_doc, docs, release_notes, "Release Notes", metadata)
                self._add(parent_doc, docs, content, None, metadata)
                yield parent_doc, docs


def main():
    CLIENT_ID = os.getenv("SALESFORCE_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SALESFORCE_CLIENT_SECRET")
    TOKEN_URL = os.getenv("SALESFORCE_TOKEN_URL")
    if not CLIENT_ID or not CLIENT_SECRET or not TOKEN_URL:
        raise ValueError(
            "Please set the SALESFORCE_CLIENT_ID and SALESFORCE_CLIENT_SECRET environment variables."
        )

    # Example usage
    ds = SalesforceDataSource(
        name="salesforce_knowledge",
        location=TOKEN_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    loader = SalesforceSupportDocumentLoader(ds)
    # loader.load_documents(products=["aiWare", "Automate", "Contact", "Redact"])
    for doc, _ in loader.load_documents(
        products=["aiWare", "Automate", "Contact", "Redact"]
    ):
        print(f"Document ID: {doc.metadata['source']}")
        print(f"Title: {doc.metadata['title']}")
        print(f"Product: {doc.metadata['product']}")
        print(f"Content: {doc.page_content[:100]}...")  # Print first 100 characters
        print()


if __name__ == "__main__":
    main()
