import os
import sys
from typing import Dict, Any, Optional, List
from pathlib import Path
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_error, log_info, log_debug
    from helpers import get_settings, Settings
except ImportError as ie:
    print(f"ImportError in {__file__}: {ie}")
    raise


def from_doc_to_chunks(file_path: Optional[str] = None, app_settings: Settings = get_settings()) -> pd.DataFrame:
    """
    Loads and chunks documents from a file path or a folder defined in settings.

    Returns:
        pd.DataFrame: DataFrame containing page content, page numbers, sources, and authors.
    """
    total_chunks = 0

    if file_path:
        files_to_process = [file_path]
    else:
        try:
            files_to_process = [
                os.path.join(app_settings.LOC_DOC, f)
                for f in os.listdir(app_settings.LOC_DOC)
                if Path(f).suffix.lower().lstrip(".") in app_settings.FILE_ALLOWED_TYPES
            ]
        except Exception as e:
            log_error(f"Failed to list files in directory: {e}")
            return pd.DataFrame()

    if not files_to_process:
        log_error("No valid files found to process.")
        return pd.DataFrame()

    all_chunks = []

    for file in files_to_process:
        try:
            extension = Path(file).suffix.lower().lstrip(".")
            loader = None

            if extension == "pdf":
                loader = PyPDFLoader(file)
            elif extension == "txt":
                loader = TextLoader(file, encoding="utf-8")
            else:
                log_debug(f"Unsupported file type: {extension}")
                continue

            documents = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=app_settings.FILE_DEFAULT_CHUNK_SIZE,
                chunk_overlap=app_settings.CHUNK_OVERLAP
            )
            chunks = splitter.split_documents(documents)
            all_chunks.extend(chunks)

            total_chunks += len(chunks)
            log_info(f"Processed {len(chunks)} chunks from {file}")

        except Exception as e:
            log_error(f"Error processing file {file}: {e}")
            continue

    # Extract metadata and content
    texts, pages, sources, authors = [], [], [], []

    for doc in all_chunks:
        texts.append(doc.page_content)
        meta = doc.metadata
        pages.append(meta.get("page", -1))
        sources.append(meta.get("source", ""))
        authors.append(meta.get("author", ""))

    data = {
        "text": texts,
        "pages": pages,
        "sources": sources,
        "authors": authors,
    }

    df = pd.DataFrame(data)
    log_info(f"Total number of chunks processed: {total_chunks}")
    return df


if __name__ == "__main__":
    df = from_doc_to_chunks()
    print(df.head())  # For debug