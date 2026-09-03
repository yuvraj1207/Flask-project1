import urllib.request
import urllib.parse
import json


class ExternalAPIService:
    @staticmethod
    def fetch_supplementary_books(topic_keyword):

        if not topic_keyword:
            return []

        query = urllib.parse.quote(topic_keyword)
        url = f"https://openlibrary.org/search.json?q={query}&limit=5"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LMS/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                books = []
                for doc in data.get("docs", []):
                    books.append({
                        "title": doc.get("title", "Unknown"),
                        "author": ", ".join(doc.get("author_name", ["Unknown"])),
                        "year": doc.get("first_publish_year"),
                        "isbn": (doc.get("isbn", [None]) or [None])[0],
                    })
                return books
        except Exception:
            return []