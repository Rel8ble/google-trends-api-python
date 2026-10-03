# Google Trends API in Python: scrape interest over time, interest by region, related queries and trending searches to JSON/CSV

A short tutorial for pulling **Google Trends data** (the 0-100 interest-over-time timeline, interest by region, top and rising related queries and topics, and today's trending searches) into Python with the [Google Trends Scraper](https://apify.com/rel8ble/google-trends-scraper) on Apify. Google has no public Trends API, and pytrends often breaks on `429 Too Many Requests`; this works as an unofficial, hosted alternative.

> Disclosure: I built this actor; it's a paid tool on Apify ($2.50 per 1,000 results). The code in this repo is MIT-licensed.

## How it works

Each line in `searchTerms` is one search: a single keyword (`bitcoin`) or up to 5 comma-separated keywords compared on one scale (`chatgpt, gemini, claude`). The actor runs a small plain-HTTP flow per search (cookie warm-up, explore, data widgets) through Apify Proxy. When Google rate-limits a request it rotates to a fresh session and IP and backs off with jitter, and a failed search is retried on its own so it never blocks the rest. No headless browser, no Google account.

## Quick start (Python)

```bash
pip install apify-client
```

```python
from apify_client import ApifyClient

client = ApifyClient("<YOUR_APIFY_TOKEN>")

run = client.actor("rel8ble/google-trends-scraper").call(run_input={
    "searchTerms": ["bitcoin", "chatgpt, gemini, claude"],
    "geo": "US",
    "timeRange": "today 12-m",
})

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    for k in item.get("keywordStats", []):
        print(item["searchTerm"], k["keyword"], k["average"], k["changePercent"])
```

[`example.py`](example.py) is the runnable version: it compares three keywords, prints average/peak/change per keyword and the rising queries, writes the weekly timeline to a CSV (one column per keyword) and lists today's trending searches in the US.

## Quick start (Node.js)

```js
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: '<YOUR_APIFY_TOKEN>' });
const run = await client.actor('rel8ble/google-trends-scraper').call({
    searchTerms: ['air fryer'], geo: 'US', timeRange: 'today 5-y',
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items[0].keywordStats);
```

## Input

| Field | Default | What it does |
|---|---|---|
| `searchTerms` | - | One search per line; up to 5 comma-separated terms on a line are compared on one 0-100 scale |
| `exploreUrls` | - | Links pasted from trends.google.com/trends/explore; keywords, geo, dates, category and search type are read from the URL |
| `geo` | Worldwide | `US`, `GB`, `DE`, or a sub-region like `US-CA` |
| `timeRange` | `today 12-m` | `now 1-H`, `now 4-H`, `now 1-d`, `now 7-d`, `today 1-m`, `today 3-m`, `today 12-m`, `today 5-y`, `all` |
| `customTimeRange` | - | `2024-01-01 2024-12-31` (overrides `timeRange`) |
| `category` | 0 (all) | Google Trends category ID, e.g. 7 Finance, 71 Food & Drink |
| `searchProperty` | `web` | `images`, `news`, `youtube`, `shopping` |
| `regionResolution` | `AUTO` | `COUNTRY`, `REGION` (state), `DMA` (US metro), `CITY` |
| `includeInterestOverTime` / `includeInterestByRegion` / `includeRelatedQueries` / `includeRelatedTopics` | on | Turn off what you don't need for faster runs |
| `trendingNowGeos` | - | Country codes to fetch Google's "Trending now" searches for |

## Output sample (one real comparison, US, past 12 months, arrays trimmed)

```json
{
  "type": "search",
  "searchTerm": "chatgpt, gemini, claude",
  "keywords": ["chatgpt", "gemini", "claude"],
  "geo": "US",
  "timeRange": "today 12-m",
  "hasData": true,
  "keywordStats": [
    { "keyword": "chatgpt", "average": 77.6, "peakValue": 100, "peakDate": "2025-10-19T00:00:00.000Z", "latestValue": 76, "changePercent": -20.2 },
    { "keyword": "gemini", "average": 26.9, "peakValue": 35, "peakDate": "2026-04-12T00:00:00.000Z", "latestValue": 33, "changePercent": 20.9 },
    { "keyword": "claude", "average": 17.9, "peakValue": 34, "peakDate": "2026-05-24T00:00:00.000Z", "latestValue": 19, "changePercent": 263.6 }
  ],
  "interestOverTime": [
    { "date": "2026-09-13T00:00:00.000Z", "formattedTime": "Sep 13 – 19, 2026",
      "values": { "chatgpt": 76, "gemini": 33, "claude": 19 }, "isPartial": false }
  ],
  "interestByRegion": [
    { "geoCode": "US-CA", "geoName": "California", "values": { "chatgpt": 57, "gemini": 26, "claude": 17 } }
  ],
  "regionResolution": "REGION",
  "relatedQueriesRising": [
    { "query": "how to use chatgpt effectively", "keyword": "chatgpt", "value": 2050,
      "formattedValue": "+2,050%", "isBreakout": false,
      "link": "https://trends.google.com/trends/explore?q=how+to+use+chatgpt+effectively&date=today+12-m&geo=US" }
  ],
  "exploreUrl": "https://trends.google.com/trends/explore?q=chatgpt%2Cgemini%2Cclaude&geo=US&date=today+12-m&hl=en-US",
  "scrapedAt": "2026-09-24T05:14:08.994Z"
}
```

A trending-now row (real, US) looks like this:

```json
{ "type": "trending", "geo": "US", "rank": 1, "title": "dodgers schedule",
  "approxTraffic": "1000+", "approxTrafficNumber": 1000, "publishedAt": "2026-09-24T04:40:00.000Z",
  "news": [{ "title": "Dodgers 7-0 Padres (Sep 22, 2026) Game Recap", "url": "https://www.espn.com/mlb/recap/_/gameId/401817044", "source": "ESPN" }] }
```

## Use cases

- **SEO and content planning**: pull `relatedQueriesRising` and breakout terms for your niche every week.
- **Brand and product comparison**: put up to 5 competitors on one line and track `keywordStats` over time.
- **Seasonality and demand by state**: `today 5-y` timelines plus `interestByRegion` for e-commerce planning.
- **Market and attention signals**: scheduled runs for tickers, crypto or brands feeding a dashboard or database.
- **Newsrooms**: daily `trendingNowGeos` with the news stories behind each trend.

## Price

**$2.50 per 1,000 results**, pay per result. One result = one search line (a comparison of up to 5 keywords counts as one, with timeline, regions, queries and topics included) or one trending search. Searches that fail after all retries are not charged. Apify's free plan includes $5 of monthly credit.

## Limits

- Up to 5 keywords per comparison (Google's own limit).
- Values are Google's relative 0-100 index, not absolute search volumes.
- Trending now returns what Google's feed lists per country, typically about 10 searches.
- Related queries and topics only appear when Google has enough volume for the term.

## Links

- Actor on the Apify Store: https://apify.com/rel8ble/google-trends-scraper
- Apify Python client docs: https://docs.apify.com/api/client/python

## License

MIT
