"""Tools for retrieving text content."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Iterable
from functools import partial
from typing import Any, Literal, TypeAlias

import pandas as pd
import pubmed_downloader
from more_itertools import batched
from pubmed_downloader.client import SearchBackend
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

__all__ = [
    "PUBMED_DATAFRAME_COLUMNS",
    "INDRADatabaseHint",
    "clean_df",
    "get_article_dataframe_from_pubmeds",
    "get_article_dataframe_from_search",
]

logger = logging.getLogger(__name__)

PUBMED_DATAFRAME_COLUMNS = ["pubmed", "title", "abstract"]
RetrievalBackend: TypeAlias = Literal["indradb", "indra", "api"]
INDRADatabaseHint: TypeAlias = Any


def get_article_dataframe_from_search(
    search_term: str,
    *,
    search_backend: SearchBackend | None = None,
    retrieval_backend: RetrievalBackend | None,
    db: INDRADatabaseHint | None = None,
    batch_size: int | None = None,
    show_progress: bool = True,
    limit: int | None = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Query PubMed for article identifiers based on a given search and get a dataframe."""
    pubmed_ids = pubmed_downloader.search(search_term, backend=search_backend, **kwargs)
    if limit:
        pubmed_ids = pubmed_ids[:limit]
    return get_article_dataframe_from_pubmeds(
        pubmed_ids,
        backend=retrieval_backend,
        db=db,
        batch_size=batch_size,
        show_progress=show_progress,
    )


def get_article_dataframe_from_pubmeds(
    pubmed_ids: Iterable[str | int],
    *,
    backend: RetrievalBackend | None,
    db: INDRADatabaseHint | None = None,
    batch_size: int | None = None,
    show_progress: bool = True,
) -> pd.DataFrame:
    """Get a dataframe indexed by PubMed identifier (str) with title and abstract columns."""
    return pd.concat(
        _iter_dataframes_from_pubmeds(
            pubmed_ids=pubmed_ids,
            backend=backend,
            db=db,
            batch_size=batch_size,
            show_progress=show_progress,
        )
    )


def _get_batch(
    pubmed_ids: Iterable[str | int],
    *,
    backend: RetrievalBackend | None = None,
    db: INDRADatabaseHint | None = None,
) -> pd.DataFrame:
    clean_pubmed_ids = _clean_pubmeds(pubmed_ids)
    if backend == "indradb":
        try:
            return _full_text_df_from_indra_db(clean_pubmed_ids, db=db)
        except (ValueError, ImportError):
            logger.warning(
                "Could not to access INDRA DB, relying on PubMed API. "
                "Warning: this could be intractably slow depending on the "
                "query, and also is missing full text."
            )
            backend = "api"
    if backend is None or backend == "api":
        return _full_text_df_from_api(clean_pubmed_ids)
    elif backend == "indra":
        return _full_text_df_from_indra(clean_pubmed_ids)
    raise ValueError(f"unknown full-text lookup backend: {backend}")


def _iter_dataframes_from_pubmeds(
    pubmed_ids: Iterable[str | int],
    *,
    backend: RetrievalBackend | None = None,
    db: INDRADatabaseHint | None = None,
    batch_size: int | None = None,
    show_progress: bool = True,
) -> Iterable[pd.DataFrame]:
    """Query PubMed for article identifiers based on a given search and get a dataframe."""
    if batch_size is None:
        batch_size = 20_000

    pubmed_ids = _clean_pubmeds(pubmed_ids)
    if len(pubmed_ids) < batch_size:
        # only a single batch, iterator not needed
        show_progress = False
    outer_it = tqdm(
        batched(pubmed_ids, batch_size),
        total=1 + len(pubmed_ids) // batch_size,
        unit="batch",
        desc="Getting articles",
        disable=not show_progress,
    )
    for i, pubmed_batch in enumerate(outer_it, start=1):
        t = time.time()
        df = _get_batch(pubmed_batch, backend=backend, db=db)
        n_retrieved = len(df.index)
        outer_it.write(
            f"[batch {i}] Got {n_retrieved:,} articles "
            f"({n_retrieved / len(pubmed_batch):.1%}) in {time.time() - t:.2f} seconds"
        )
        yield df


def _clean_pubmeds(pubmeds: Iterable[str | int]) -> list[str]:
    return sorted(map(str, pubmeds), key=int)


def _full_text_df_from_indra(pubmed_ids: list[str]) -> pd.DataFrame:
    return _full_text_helper(pubmed_ids, _get_titles_indra, _get_abstracts_indra)


def _full_text_df_from_api(pubmed_ids: list[str]) -> pd.DataFrame:
    return _full_text_helper(
        pubmed_ids,
        partial(pubmed_downloader.get_titles, error_strategy="none"),
        partial(pubmed_downloader.get_abstracts, error_strategy="none"),
    )


#: A function that takes a list of pubmed ids and returns a list of corresponding things
PubmedAttributeGetter: TypeAlias = Callable[[list[str]], list[str | None] | list[str]]


def _full_text_helper(
    pubmed_ids: list[str], get_titles: PubmedAttributeGetter, get_abstracts: PubmedAttributeGetter
) -> pd.DataFrame:
    titles = get_titles(pubmed_ids)
    abstracts = get_abstracts(pubmed_ids)
    df = pd.DataFrame(
        zip(pubmed_ids, titles, abstracts, strict=False),
        columns=PUBMED_DATAFRAME_COLUMNS,
    )
    df = df.set_index("pubmed")
    df = clean_df(df)
    return df


def _get_titles_indra(x: list[str]) -> list[str]:
    from indra.literature import pubmed_client

    with logging_redirect_tqdm():
        rv = [
            pubmed_client.get_title(pubmed_id)
            for pubmed_id in tqdm(
                x,
                leave=False,
                unit_scale=True,
                unit="article",
                desc="Getting PubMed titles",
            )
        ]
    return rv


def _get_abstracts_indra(x: list[str]) -> list[str]:
    from indra.literature import pubmed_client

    with logging_redirect_tqdm():
        rv = [
            pubmed_client.get_abstract(pubmed_id, prepend_title=False)
            for pubmed_id in tqdm(
                x,
                leave=False,
                unit_scale=True,
                unit="article",
                desc="Getting PubMed titles",
            )
        ]
    return rv


def _full_text_df_from_indra_db(
    pubmed_ids: list[str], db: INDRADatabaseHint | None = None
) -> pd.DataFrame:
    """Get titles and abstracts from the INDRA database."""
    db = _ensure_db(db)
    df = pd.DataFrame(
        {
            "title": _get_text(pubmed_ids, text_type="title", db=db),
            "abstract": _get_text(pubmed_ids, text_type="abstract", db=db),
        }
    )
    df.index.name = "pubmed"
    df = clean_df(df)
    return df


def _get_text(pubmed_ids: list[str], text_type: str, db: INDRADatabaseHint) -> dict[str, str]:
    from indra_db.util.helpers import unpack as unpack_indra_db

    return {
        row.pmid: unpack_indra_db(row.content).replace("\t", " ").replace("\n", "\t")
        for row in (
            db.session.query(db.TextRef.pmid, db.TextContent.text_type, db.TextContent.content)
            .filter(db.TextRef.pmid_in(pubmed_ids))
            .join(db.TextContent)
            .filter(db.TextContent.text_type == text_type)
            .all()
        )
    }


def _ensure_db(db: INDRADatabaseHint | None = None) -> INDRADatabaseHint:
    from indra_db import get_db

    if db is None:
        db = get_db("primary")
    if db is None:
        raise ValueError("Could not connect to INDRA DB")
    return db


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the literature dataframe.

    :param df: A dataframe

    :returns: A cleaned dataframe

    Does the following:

    1. Removes missing titles/abstracts
    2. Removes questionable whitespace.

    """
    df = df[df.title.notna()].copy()
    df["title"] = df["title"].map(lambda s: s.replace("\n", " ").replace("\t", " "))
    df = df[df.abstract.notna()]
    df["abstract"] = df["abstract"].map(lambda s: s.replace("\n", " ").replace("\t", " "))
    return df
