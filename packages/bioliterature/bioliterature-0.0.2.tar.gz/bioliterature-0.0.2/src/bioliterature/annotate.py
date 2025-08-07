"""Tools for getting literature."""

from __future__ import annotations

import logging
import typing as t
from collections import Counter

import pubmed_downloader
import ssslm
from curies import NamableReference
from pubmed_downloader.client import SearchBackend
from pydantic import BaseModel
from tqdm.auto import tqdm

from .retrieve import RetrievalBackend, _iter_dataframes_from_pubmeds

__all__ = [
    "AnnotatedArticle",
    "annotate_abstracts_from_pubmeds",
    "annotate_abstracts_from_search",
]


logger = logging.getLogger(__name__)


class AnnotatedArticle(BaseModel):
    """A data model representing an annotated article from PubMed."""

    pubmed: str
    title: str
    abstract: str
    annotations: list[ssslm.Annotation]

    def count_references(self) -> t.Counter[NamableReference]:
        """Count the references annotated in this article."""
        return Counter(a.reference for a in self.annotations)


def annotate_abstracts_from_search(
    pubmed_query: str,
    grounder: ssslm.GrounderHint,
    *,
    limit: int | None = None,
    show_progress: bool = True,
    search_backend: SearchBackend | None = None,
    retrieval_backend: RetrievalBackend | None = None,
    **kwargs: t.Any,
) -> list[AnnotatedArticle]:
    """Get articles based on the query and do NER annotation using the given Gilda grounder."""
    if limit:
        kwargs["retmax"] = limit
    pubmed_ids = pubmed_downloader.search(pubmed_query, backend=search_backend, **kwargs)
    return annotate_abstracts_from_pubmeds(
        pubmed_ids,
        grounder=grounder,
        backend=retrieval_backend,
        show_progress=show_progress,
    )


def annotate_abstracts_from_pubmeds(
    pubmed_ids: t.Collection[str | int],
    grounder: ssslm.GrounderHint,
    *,
    backend: RetrievalBackend | None = None,
    batch_size: int | None = None,
    show_progress: bool = True,
) -> list[AnnotatedArticle]:
    """Annotate the given articles using the given Gilda grounder."""
    grounder = ssslm.make_grounder(grounder)
    df_iterator = _iter_dataframes_from_pubmeds(
        pubmed_ids=pubmed_ids,
        batch_size=batch_size,
        backend=backend,
        show_progress=show_progress,
    )
    rv: list[AnnotatedArticle] = [
        AnnotatedArticle(
            pubmed=pubmed,
            title=title,
            abstract=abstract,
            annotations=grounder.annotate(abstract),
        )
        for i, df in enumerate(df_iterator, start=1)
        for pubmed, title, abstract in tqdm(
            df.itertuples(),
            desc=f"Annotating batch {i}",
            unit_scale=True,
            unit="article",
            total=len(df.index),
            leave=False,
            disable=not show_progress,
        )
    ]
    return rv
