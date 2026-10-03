"""Compare keywords on Google Trends and list rising queries + today's trending searches.

Usage:
    pip install -r requirements.txt
    APIFY_TOKEN=<YOUR_APIFY_TOKEN> python example.py
"""
import csv
import os

from apify_client import ApifyClient

TOKEN = os.environ.get("APIFY_TOKEN", "<YOUR_APIFY_TOKEN>")
KEYWORDS = "chatgpt, gemini, claude"  # up to 5, compared on one 0-100 scale
GEO = "US"

client = ApifyClient(TOKEN)
run = client.actor("rel8ble/google-trends-scraper").call(run_input={
    "searchTerms": [KEYWORDS],
    "geo": GEO,
    "timeRange": "today 12-m",
    "trendingNowGeos": [GEO],
})

searches, trending = [], []
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    if item.get("type") == "search":
        searches.append(item)
    elif item.get("type") == "trending":
        trending.append(item)

for s in searches:
    if not s.get("hasData"):
        print(f"No data for {s['searchTerm']}")
        continue
    print(f"\n{s['searchTerm']} ({s['geo']}, {s['timeRange']})")
    for k in s["keywordStats"]:
        print(f"  {k['keyword']:<12} avg {k['average']:>5}  latest {k['latestValue']:>3}  "
              f"peak {k['peakValue']} on {k['peakDate'][:10]}  change {k['changePercent']:+}%")

    print("  Rising queries:")
    for q in s.get("relatedQueriesRising", [])[:10]:
        print(f"    {q['formattedValue']:>10}  {q['query']}  [{q['keyword']}]")

    # Weekly timeline to CSV, one column per keyword
    path = "trends_timeline.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", *s["keywords"], "isPartial"])
        for p in s["interestOverTime"]:
            w.writerow([p["date"][:10], *[p["values"].get(k) for k in s["keywords"]], p["isPartial"]])
    print(f"  Timeline written to {path}")

if trending:
    print(f"\nTrending now in {GEO}:")
    for t in sorted(trending, key=lambda t: t["rank"])[:10]:
        print(f"  #{t['rank']:<3} {t['title']}  ({t.get('approxTraffic', '?')} searches)")
