import json
from flask import Flask, request, Response
from pyselsearch import GoogleSearch

app = Flask(__name__)


def search_google(query, retry_limit=1):
    attempt = 0
    data = []

    while attempt < retry_limit and not data:
        scraper = (
            GoogleSearch(headless=False)
            if attempt == 0
            else GoogleSearch(headless=False, proxy="prime:pass@proxies.hawker.news:12852")
        )
        data = scraper.search(query)
        attempt += 1

    return data


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    retry = request.args.get("retry", default=1, type=int)

    if not query:
        return Response(
            json.dumps({"error": "Missing 'query' parameter"}, ensure_ascii=False),
            status=400,
            mimetype="application/json"
        )

    data = search_google(query, retry)
    return Response(
        json.dumps(data, ensure_ascii=False),
        mimetype="application/json"
    )


if __name__ == "__main__":
    app.run(debug=False, port=5001)
