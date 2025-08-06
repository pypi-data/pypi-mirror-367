import json
import os
import time
from flask import Flask, request, Response
from pyselsearch import GoogleSearch

app = Flask(__name__)
COOLDOWN_FILE = "cooldown.txt"
COOLDOWN_SECONDS = 5 * 60  # 5 minutes


def is_in_cooldown():
    if not os.path.exists(COOLDOWN_FILE):
        return False

    with open(COOLDOWN_FILE, "r") as f:
        try:
            last_failed_time = float(f.read().strip())
        except ValueError:
            return False

    return (time.time() - last_failed_time) < COOLDOWN_SECONDS


def mark_cooldown():
    with open(COOLDOWN_FILE, "w") as f:
        f.write(str(time.time()))


def search_google(query, retry_limit, sleep):
    attempt = 0
    data = []

    while attempt < retry_limit and not data:
        use_proxy = attempt > 0 or is_in_cooldown()
        scraper = GoogleSearch(
            headless=False,
            window_size="0, 0",
            window_position="0, 0",
            proxy="prime:6a0JL4uChppl@proxies.hawker.news:12852" if use_proxy else None
        )
        data = scraper.search(query, sleep_time=sleep)
        if attempt == 0 and not data:
            mark_cooldown()
        attempt += 1

    return data


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query")
    retry = request.args.get("retry", default=4, type=int)
    sleep = request.args.get("retry", default=2, type=int)

    if not query:
        return Response(
            json.dumps({"error": "Missing 'query' parameter"}, ensure_ascii=False),
            status=400,
            mimetype="application/json"
        )

    data = search_google(query, retry, sleep)
    return Response(
        json.dumps({"query": query, "data": data}, ensure_ascii=False),
        mimetype="application/json"
    )


if __name__ == "__main__":
    app.run(debug=False, port=5001)
