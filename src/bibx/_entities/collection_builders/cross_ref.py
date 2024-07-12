import requests

from bibx._entities.collection import Article, Collection
from bibx._entities.collection_builders.base import CollectionBuilder


class CrossRefCollectionBuilder(CollectionBuilder):
    def __init__(self, query: str, count: int = 100):
        self._query = query
        self._count = count

    def with_count(self, count: int):
        self._count = count
        return self

    def build(self) -> Collection:
        url = f"https://api.crossref.org/works?query={self._query.lower().replace(' ', '+')}&filter=has-orcid:true,type:journal-article,has-references:true,from-pub-date:2003-01-01&rows={self._count}"
        response = requests.get(url)
        data = response.json()
        items = data.get("message", {}).get("items", [])

        articles = []
        for item in items:
            author_list = item.get("author", [])
            authors = [
                f"{author.get('given', '')} {author.get('family', '')}"
                for author in author_list
            ]
            publication_year = item.get("published").get("date-parts", [[2000]])[0][0]
            title = item.get("title", None)[0]
            journal = item.get("container-title", None)[0]
            volume = item.get("volume", None)
            issue = item.get("issue", None)
            page = item.get("page", None)
            doi = item.get("DOI", None)
            times_cited = item.get("is-referenced-by-count", 0)
            reference = item.get("reference", [])
            references = []
            for ref in reference:
                if ref.get("unstructured", None) is not None:
                    unique_reference = Article(title=ref.get("unstructured", None))
                else:
                    unique_reference = Article(
                        authors=[ref.get("author", [])],
                        year=ref.get("year", None),
                        title=ref.get("article-title", None),
                        journal=ref.get("journal-title", None),
                        volume=ref.get("volume", None),
                        issue=ref.get("issue", None),
                        page=ref.get("page", None),
                        doi=ref.get("DOI", None),
                    )
                references.append(unique_reference)

            article = Article(
                authors=authors,
                year=publication_year,
                title=title,
                journal=journal,
                volume=volume,
                issue=issue,
                page=page,
                doi=doi,
                times_cited=times_cited,
                references=references,
            )
            articles.append(article)

        return Collection(articles)
