#!/usr/bin/env python3
"""Fetch literature from PubMed via NCBI E-utilities for a given variant/gene.

Produces reports/{rsid}_literature.json with pubmed_articles and search metadata.
Google Scholar is not available via free API, so only PubMed is searched.
"""


import glob as _glob
import os as _os
import sys as _sys

# Auto-detect venv when present (following nano-banana pattern)
_SCRIPT_DIR = _os.path.dirname(_os.path.abspath(__file__))
_SKILL_DIR = _os.path.dirname(_SCRIPT_DIR)
_VENV_SITE = _os.path.join(_SKILL_DIR, ".venv", "lib")
if _os.path.isdir(_VENV_SITE):
    _matches = _glob.glob(_os.path.join(_VENV_SITE, "python*", "site-packages"))
    if _matches:
        _sys.path.insert(0, _matches[0])

import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
NCBI_API_KEY = None  # Set via env var NCBI_API_KEY for higher rate limits


def esearch(query: str, retmax: int = 20) -> list[str]:
    """Search PubMed and return list of PMIDs."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": retmax,
        "sort": "relevance",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    resp = requests.get(f"{EUTILS_BASE}/esearch.fcgi", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def efetch_articles(pmids: list[str]) -> list[dict]:
    """Fetch article details for a list of PMIDs using efetch XML."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "xml",
        "retmode": "xml",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    resp = requests.get(f"{EUTILS_BASE}/efetch.fcgi", params=params, timeout=60)
    resp.raise_for_status()

    articles = []
    root = ET.fromstring(resp.text)
    for article_elem in root.findall(".//PubmedArticle"):
        article = _parse_pubmed_article(article_elem)
        if article:
            articles.append(article)

    return articles


def _parse_pubmed_article(elem) -> dict | None:
    """Parse a PubmedArticle XML element into a dict."""
    medline = elem.find(".//MedlineCitation")
    if medline is None:
        return None

    pmid_elem = medline.find("PMID")
    pmid = pmid_elem.text if pmid_elem is not None else ""

    article = medline.find("Article")
    if article is None:
        return None

    # Title
    title_elem = article.find("ArticleTitle")
    title = _get_text(title_elem)

    # Journal
    journal_elem = article.find(".//Journal/Title")
    journal = journal_elem.text if journal_elem is not None else ""

    # Year
    year = ""
    pub_date = article.find(".//Journal/JournalIssue/PubDate")
    if pub_date is not None:
        year_elem = pub_date.find("Year")
        if year_elem is not None:
            year = year_elem.text
        else:
            medline_date = pub_date.find("MedlineDate")
            if medline_date is not None and medline_date.text:
                year = medline_date.text[:4]

    # Authors
    authors = []
    author_list = article.find("AuthorList")
    if author_list is not None:
        for author_elem in author_list.findall("Author"):
            last = author_elem.find("LastName")
            initials = author_elem.find("Initials")
            if last is not None:
                name = last.text
                if initials is not None:
                    name += f" {initials.text}"
                authors.append(name)
    authors_str = authors[0] + " et al." if len(authors) > 1 else (authors[0] if authors else "")

    # Abstract
    abstract_elem = article.find(".//Abstract/AbstractText")
    abstract = _get_text(abstract_elem)
    abstract_snippet = abstract[:300] + "..." if len(abstract) > 300 else abstract

    return {
        "pmid": pmid,
        "title": title,
        "authors": authors_str,
        "journal": journal,
        "year": year,
        "abstract_snippet": abstract_snippet,
    }


def _get_text(elem) -> str:
    """Get all text content from an XML element, including mixed content."""
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


def fetch_literature(rsid: str, gene_symbol: str) -> dict:
    """Search PubMed for literature on the given variant/gene."""
    import os
    global NCBI_API_KEY
    NCBI_API_KEY = os.environ.get("NCBI_API_KEY")

    result = {
        "rsid": rsid,
        "gene_symbol": gene_symbol,
        "pubmed_articles": [],
        "scholar_articles": [],
        "search_queries_used": [],
        "errors": [],
    }

    all_pmids = []
    queries = [
        f"{gene_symbol} AND {rsid}",
        f"{gene_symbol} AND (drug target OR therapeutic)",
        f"{gene_symbol} AND (biomarker OR pharmacogenomics)",
    ]

    for query in queries:
        result["search_queries_used"].append(query)
        try:
            pmids = esearch(query, retmax=10)
            for pmid in pmids:
                if pmid not in all_pmids:
                    all_pmids.append(pmid)
            time.sleep(0.34)  # Respect NCBI rate limit (3/sec without key)
        except requests.RequestException as e:
            result["errors"].append(f"PubMed search failed for '{query}': {str(e)}")

    # Fetch article details
    if all_pmids:
        try:
            articles = efetch_articles(all_pmids[:30])
            result["pubmed_articles"] = articles
        except requests.RequestException as e:
            result["errors"].append(f"PubMed efetch failed: {str(e)}")

    # Note about Google Scholar
    result["errors"].append(
        "Google Scholar search not available via free API; only PubMed results included"
    )

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_literature.py <rsID> [reports_dir]", file=sys.stderr)
        sys.exit(1)

    rsid = sys.argv[1].lower().strip()
    script_dir = Path(__file__).parent
    reports_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd() / "reports"

    # Read variant info
    variant_file = reports_dir / f"{rsid}_variant.json"
    try:
        with open(variant_file) as f:
            variant_info = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(json.dumps({"error": f"Could not read variant info: {e}"}))
        sys.exit(1)

    gene_symbol = variant_info.get("gene_symbol", "")
    if not gene_symbol:
        print(json.dumps({"error": "No gene_symbol in variant info"}))
        sys.exit(1)

    result = fetch_literature(rsid, gene_symbol)

    # Write output
    output_file = reports_dir / f"{rsid}_literature.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Literature results written to {output_file}")


if __name__ == "__main__":
    main()
