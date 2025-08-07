"""Interact with NCBI rest."""

import logging
import os
import platform
import shlex
import stat
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal, TypeAlias, TypedDict

import pystow
import requests
import ssslm
from lxml import etree
from more_itertools import batched
from pydantic import BaseModel
from ratelimit import rate_limited
from typing_extensions import NotRequired, Unpack

from pubmed_downloader.api import Article, _extract_article

__all__ = [
    "PubMedSearchKwargs",
    "SearchBackend",
    "count_search_results",
    "get_abstracts",
    "get_titles",
    "search",
    "search_with_api",
    "search_with_edirect",
]

logger = logging.getLogger(__name__)

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

URL = "https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/edirect.tar.gz"
URL_APPLE_SILICON = "https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/xtract.Silicon.gz"
URL_LINUX = "https://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/xtract.Linux.gz"
MODULE = pystow.module("ncbi")

#: https://www.ncbi.nlm.nih.gov/books/NBK25497/ rate limit getting to the API
get = rate_limited(calls=3, period=1)(requests.get)


class PubMedSearchKwargs(TypedDict):
    """Keyword arguments for the PubMed search API.

    .. seealso:: https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch
    """

    use_text_word: NotRequired[bool]
    """
    Automatically add the ``[tw]`` type to the query to only search
    the title, abstract, and text fields. Useful to avoid spurious results.

    .. seealso:: https://www.nlm.nih.gov/bsd/disted/pubmedtutorial/020_760.html
    """
    retstart: NotRequired[int]
    retmax: NotRequired[int]
    reldate: NotRequired[int]
    maxdate: NotRequired[str]


class SearchResult(BaseModel):
    """Results from the PubMed search API."""

    count: int
    maximum: int
    start: int
    identifiers: list[str]
    query: str
    query_translation: str


#: The serch backend
SearchBackend: TypeAlias = Literal["edirect", "api"]


def search(query: str, backend: SearchBackend | None = None, **kwargs: Any) -> list[str]:
    """Search PubMed."""
    if backend == "edirect":
        return search_with_edirect(query)
    elif backend == "api" or backend is None:
        return search_with_api(query, **kwargs)
    else:
        raise ValueError


def search_with_edirect(query: str) -> list[str]:
    """Get PubMed identifiers for a query."""
    injection = f"PATH={get_edirect_directory().as_posix()}:${{PATH}}"
    cmd = (
        f"{injection} esearch -db pubmed -query {shlex.quote(query)} "
        f"| {injection} efetch -format uid"
    )
    res = subprocess.getoutput(cmd)  # noqa:S605
    if "esearch: command not found" in res:
        raise RuntimeError("esearch is not properly on the filepath")
    if "efetch: command not found" in res:
        raise RuntimeError("efetch is not properly on the filepath")
    # If there are more than 10k IDs, the CLI outputs a . for each
    # iteration, these have to be filtered out
    pubmeds = [pubmed for pubmed in res.split("\n") if pubmed and "." not in pubmed]
    return pubmeds


def get_edirect_directory() -> Path:
    """Get path to eSearch tool."""
    path = MODULE.ensure_untar(url=URL)

    if platform.system() == "Darwin" and platform.machine() == "arm64":
        # if you're on an apple system, you need to download this,
        # and later enable it from the security preferences
        _ensure_xtract_command(URL_APPLE_SILICON)
    elif platform.system() == "Linux":
        _ensure_xtract_command(URL_LINUX)

    return path.joinpath("edirect")


def _ensure_xtract_command(url: str) -> Path:
    path = MODULE.ensure_gunzip("edirect", "edirect", url=url)

    # make sure that the file is executable
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def search_with_api(
    query: str,
    **kwargs: Unpack[PubMedSearchKwargs],
) -> list[str]:
    """Search Pubmed for paper IDs given a search term.

    :param query:
        A term for which the PubMed search should be performed.
    :param kwargs:
        Additional keyword arguments to pass to the PubMed search as
        parameters. See https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch

    Here's an example XML response:

    .. code-block:: xml

        <?xml version="1.0" encoding="UTF-8" ?>
        <!DOCTYPE eSearchResult PUBLIC "-//NLM//DTD esearch 20060628//EN" "https://eutils.ncbi.nlm.nih.gov/eutils/dtd/20060628/esearch.dtd">
        <eSearchResult>
            <Count>422</Count>
            <RetMax>2</RetMax>
            <RetStart>0</RetStart>
            <IdList>
                <Id>40758384</Id>
                <Id>40535547</Id>
            </IdList>
            <TranslationSet/>
            <QueryTranslation>"Disease Ontology"[Text Word]</QueryTranslation>
        </eSearchResult>

    """
    result = _request_api(query, **kwargs)
    if len(result.identifiers) < result.count:
        logger.warning(
            "Not all PubMeds were returned for search `%s`. Limited by `retmax` of %d",
            query,
            result.maximum,
        )
    return result.identifiers


def count_search_results(query: str, **kwargs: Unpack[PubMedSearchKwargs]) -> int:
    """Count results."""
    return _request_api(query, **kwargs).count


def _request_api(query: str, **kwargs: Unpack[PubMedSearchKwargs]) -> SearchResult:
    if kwargs.pop("use_text_word", True):
        query += "[tw]"

    retmax = kwargs.pop("retmax", 10_000)
    if retmax <= 0:
        raise ValueError
    if retmax > 10_000:
        retmax = 10_000

    retstart = kwargs.pop("retstart", 0)
    if retstart < 0:
        raise ValueError

    params: dict[str, Any] = {
        "term": query,
        "retmax": retmax,
        "retstart": retstart,
        "db": "pubmed",
    }
    params.update(kwargs)
    res = get(PUBMED_SEARCH_URL, params=params, timeout=30)
    res.raise_for_status()
    tree = etree.fromstring(res.content)
    return SearchResult(
        count=int(tree.find("Count").text),
        maximum=int(tree.find("RetMax").text),
        start=int(tree.find("RetStart").text),
        query=query,
        query_translation=tree.find("QueryTranslation").text,
        identifiers=[element.text for element in tree.findall("IdList/Id")],
    )


def get_titles(pubmed_ids: list[str]) -> list[str]:
    """Get titles."""
    return [article.title for article in _fetch_iter(pubmed_ids)]


def get_abstracts(pubmed_ids: list[str]) -> list[str]:
    """Get abstracts."""
    return [
        " ".join(abstract.text for abstract in article.abstract)
        for article in _fetch_iter(pubmed_ids)
    ]


def _fetch_iter(
    pubmed_ids: list[str],
    *,
    ror_grounder: ssslm.Grounder | None = None,
    mesh_grounder: ssslm.Grounder | None = None,
    timeout: int | None = None,
) -> Iterable[Article]:
    for subset in batched(pubmed_ids, 10_000):
        params = {"db": "pubmed", "id": ",".join(subset), "retmode": "xml"}
        response = get(PUBMED_FETCH_URL, params=params, timeout=timeout or 300)
        tree = etree.fromstring(response.text)
        for article_element in tree.findall("PubmedArticle"):
            article = _extract_article(
                article_element, ror_grounder=ror_grounder, mesh_grounder=mesh_grounder
            )
            if article is None:
                raise ValueError
            yield article


if __name__ == "__main__":
    pass
