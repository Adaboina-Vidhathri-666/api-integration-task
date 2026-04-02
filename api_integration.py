"""
API Integration Script - Weather / Crypto / News
Uses: requests, JSON parsing, search/filter functionality
APIs Used:
  - Weather: Open-Meteo (free, no key needed)
  - Crypto:  CoinGecko (free, no key needed)
  - News:    NewsData.io demo endpoint / GNews (free tier)
"""

import requests
import json
from datetime import datetime

# ─────────────────────────────────────────────
#  WEATHER  (Open-Meteo – no API key required)
# ─────────────────────────────────────────────
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

WMO_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Moderate drizzle",
    55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
    95: "Thunderstorm", 96: "Thunderstorm + hail", 99: "Thunderstorm + heavy hail",
}

def get_coordinates(city: str) -> dict | None:
    """Geocode a city name → lat/lon."""
    resp = requests.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return None
    r = results[0]
    return {"name": r["name"], "country": r.get("country", ""), "lat": r["latitude"], "lon": r["longitude"]}

def fetch_weather(city: str) -> None:
    """Fetch and display current + 3-day forecast for a city."""
    print(f"\n{'='*55}")
    print(f"  🌤  WEATHER  –  {city.title()}")
    print(f"{'='*55}")

    geo = get_coordinates(city)
    if not geo:
        print(f"  ❌  City '{city}' not found.")
        return

    params = {
        "latitude": geo["lat"],
        "longitude": geo["lon"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "auto",
        "forecast_days": 4,
    }
    resp = requests.get(WEATHER_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    cur = data["current"]
    print(f"\n  📍 {geo['name']}, {geo['country']}")
    print(f"  🌡  Temperature : {cur['temperature_2m']} °C")
    print(f"  💧 Humidity    : {cur['relative_humidity_2m']} %")
    print(f"  💨 Wind Speed  : {cur['wind_speed_10m']} km/h")
    print(f"  🌥  Condition   : {WMO_CODES.get(cur['weathercode'], 'Unknown')}")

    print(f"\n  {'─'*45}")
    print(f"  {'Date':<14} {'Condition':<22} {'High':>6} {'Low':>6}")
    print(f"  {'─'*45}")
    daily = data["daily"]
    for i in range(4):
        date  = daily["time"][i]
        label = "Today" if i == 0 else date
        cond  = WMO_CODES.get(daily["weathercode"][i], "?")[:20]
        high  = daily["temperature_2m_max"][i]
        low   = daily["temperature_2m_min"][i]
        print(f"  {label:<14} {cond:<22} {high:>5}°C {low:>5}°C")


# ─────────────────────────────────────────────
#  CRYPTO  (CoinGecko – no API key required)
# ─────────────────────────────────────────────
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

def fetch_crypto(search: str = "", top_n: int = 10) -> None:
    """Fetch top crypto prices; optionally filter by coin name/symbol."""
    print(f"\n{'='*55}")
    print(f"  ₿  CRYPTO PRICES  –  Top {top_n}  |  Filter: '{search or 'none'}'")
    print(f"{'='*55}")

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": "false",
    }
    resp = requests.get(COINGECKO_URL, params=params, timeout=10)
    resp.raise_for_status()
    coins = resp.json()

    # Filter
    if search:
        coins = [c for c in coins if search.lower() in c["name"].lower()
                                   or search.lower() in c["symbol"].lower()]

    coins = coins[:top_n]
    if not coins:
        print(f"  ❌  No coins matching '{search}'.")
        return

    print(f"\n  {'#':<4} {'Coin':<18} {'Symbol':<8} {'Price (USD)':>14} {'24h %':>8} {'Market Cap':>18}")
    print(f"  {'─'*72}")
    for rank, c in enumerate(coins, 1):
        change = c.get("price_change_percentage_24h") or 0
        arrow  = "▲" if change >= 0 else "▼"
        mcap   = f"${c['market_cap']:,.0f}" if c['market_cap'] else "N/A"
        print(f"  {rank:<4} {c['name']:<18} {c['symbol'].upper():<8} "
              f"${c['current_price']:>13,.4f} {arrow}{abs(change):>6.2f}% {mcap:>18}")


# ─────────────────────────────────────────────
#  NEWS  (GNews free API – no key for basic)
# ─────────────────────────────────────────────
GNEWS_URL = "https://gnews.io/api/v4/top-headlines"

def fetch_news(topic: str = "technology", lang: str = "en", max_results: int = 5) -> None:
    """
    Fetch top headlines.  Topic can be: breaking-news, technology, world,
    nation, business, entertainment, sports, science, health.
    NOTE: GNews requires a free API key (https://gnews.io).
          Replace GNEWS_API_KEY below with your key.
          A fallback using the open HackerNews API is provided automatically.
    """
    GNEWS_API_KEY = "demo"   # ← replace with your free key from gnews.io

    print(f"\n{'='*55}")
    print(f"  📰  NEWS  –  Topic: {topic.upper()}  |  Lang: {lang}")
    print(f"{'='*55}")

    # ── Try GNews ──────────────────────────────
    try:
        params = {
            "category": topic,
            "lang": lang,
            "max": max_results,
            "apikey": GNEWS_API_KEY,
        }
        resp = requests.get(GNEWS_URL, params=params, timeout=10)
        data = resp.json()
        articles = data.get("articles", [])
        if articles:
            _print_articles(articles)
            return
    except Exception:
        pass

    # ── Fallback: HackerNews Top Stories (tech) ─
    print("  ℹ  Using HackerNews fallback (add a GNews key for full categories)\n")
    ids_resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
    ids_resp.raise_for_status()
    story_ids = ids_resp.json()[:max_results]

    articles = []
    for sid in story_ids:
        s = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=10).json()
        articles.append({
            "title":       s.get("title", "N/A"),
            "source":      {"name": "HackerNews"},
            "publishedAt": datetime.utcfromtimestamp(s.get("time", 0)).strftime("%Y-%m-%d %H:%M"),
            "url":         s.get("url", f"https://news.ycombinator.com/item?id={sid}"),
        })

    # Filter by topic keyword if provided
    kw = topic.lower()
    filtered = [a for a in articles if kw in a["title"].lower()]
    _print_articles(filtered if filtered else articles)


def _print_articles(articles: list) -> None:
    for i, a in enumerate(articles, 1):
        source = a.get("source", {}).get("name", "Unknown")
        date   = a.get("publishedAt", "")[:16]
        title  = a.get("title", "No title")
        url    = a.get("url", "")
        print(f"  {i}. [{source}]  {date}")
        print(f"     {title}")
        print(f"     🔗 {url}")
        print()


# ─────────────────────────────────────────────
#  INTERACTIVE MENU
# ─────────────────────────────────────────────
def main():
    print("\n" + "="*55)
    print("   🌐  API INTEGRATION DASHBOARD")
    print("   Weather  •  Crypto  •  News")
    print("="*55)

    while True:
        print("\n  Select an option:")
        print("  [1] Weather lookup")
        print("  [2] Crypto prices")
        print("  [3] Latest news")
        print("  [4] Run all demos")
        print("  [0] Exit")

        choice = input("\n  Enter choice: ").strip()

        if choice == "1":
            city = input("  Enter city name: ").strip() or "Hyderabad"
            fetch_weather(city)

        elif choice == "2":
            search = input("  Filter by coin name/symbol (blank = top 10): ").strip()
            fetch_crypto(search=search, top_n=10)

        elif choice == "3":
            print("  Topics: technology, world, business, sports, science, health")
            topic = input("  Enter topic (default: technology): ").strip() or "technology"
            fetch_news(topic=topic)

        elif choice == "4":
            fetch_weather("Hyderabad")
            fetch_crypto(search="", top_n=5)
            fetch_news(topic="technology")

        elif choice == "0":
            print("\n  👋  Goodbye!\n")
            break
        else:
            print("  ⚠  Invalid choice. Try again.")


if __name__ == "__main__":
    main()
