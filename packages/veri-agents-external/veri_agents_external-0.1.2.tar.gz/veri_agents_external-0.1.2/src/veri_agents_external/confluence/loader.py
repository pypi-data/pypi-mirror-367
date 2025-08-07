import logging
from datetime import datetime
from typing import Iterator

from langchain_core.documents import Document
from langchain_community.document_loaders import ConfluenceLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from veri_agents_knowledgebase.knowledgebase import DataSource, DocumentLoader

logger = logging.getLogger(__name__)

class ConfluenceDataSource(DataSource):
    username: str
    """ The username for Confluence API access. """
    
    api_key: str
    """ The API key for Confluence API access. """

    space_key: str
    """ The key of the Confluence space to load documents from. """


class ConfluenceDocumentLoader(DocumentLoader):
    def __init__(
        self,
        data_source: ConfluenceDataSource,
        include_attachments: bool = False,
    ):
        super().__init__(data_source)
        self.loader = ConfluenceLoader(
            url=str(data_source.location),
            username=data_source.username,
            api_key=data_source.api_key,
            keep_markdown_format=True,
            include_attachments=include_attachments,
            space_key=data_source.space_key,
            limit=50,
            max_pages=10000,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=200
        )

    def _split(self, text: str, metadata: dict) -> list[Document]:
        """Split text into smaller chunks using the text splitter."""
        doc = Document(page_content=text, metadata=metadata)
        new_docs = self.splitter.split_documents([doc])
        return new_docs

    def _add_content(
        self,
        parent_doc: Document,
        child_docs: list[Document],
        text: str,
        metadata: dict,
    ):
        """Add content to parent document and create child documents."""
        if text.strip():
            parent_doc.page_content += f"{text}\n"
            new_docs = self._split(text, metadata)
            child_docs.extend(new_docs)

    def load_documents(
        self, **kwargs
    ) -> Iterator[tuple[Document, list[Document] | None]]:
        """Load documents from Confluence and split them into parent and child documents."""
        # Load documents using the lazy_load method
        for doc in self.loader.lazy_load(**kwargs):
            # Create metadata with updated timestamp
            metadata = doc.metadata.copy()
            metadata["last_updated"] = datetime.now().isoformat()
            
            # Create parent document
            parent_doc = Document(page_content="", metadata=metadata)
            child_docs: list[Document] = []
            
            # Add the full content to both parent and child documents
            self._add_content(parent_doc, child_docs, doc.page_content, metadata)
            
            yield parent_doc, child_docs
