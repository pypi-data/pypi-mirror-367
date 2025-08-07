"""Tools for working with literature."""

from .annotate import (
    AnnotatedArticle,
    annotate_abstracts_from_pubmeds,
    annotate_abstracts_from_search,
)
from .retrieve import (
    get_article_dataframe_from_pubmeds,
    get_article_dataframe_from_search,
)

__all__ = [
    "AnnotatedArticle",
    "annotate_abstracts_from_pubmeds",
    "annotate_abstracts_from_search",
    "get_article_dataframe_from_pubmeds",
    "get_article_dataframe_from_search",
]
