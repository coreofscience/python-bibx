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
            references = item.get("reference", [])

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
