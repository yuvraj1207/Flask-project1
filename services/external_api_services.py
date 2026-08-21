import urllib.request
import urllib.parse
import json

class ExternalAPIService:
    @staticmethod
    def fetch_supplementary_books(topic_keyword):

        if not topic_keyword:
            return []

        query = urllib.parse.quote(topic_keyword)
        url = "https://openlibrary.org/search.json?&limit=5"