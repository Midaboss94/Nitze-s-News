import os
import smtplib
import hashlib
import requests
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Configuration ────────────────────────────────────────────────────────────
NEWS_API_KEY   = os.environ["NEWS_API_KEY"]
NYT_API_KEY    = os.environ["NYT_API_KEY"]
GMAIL_ADDRESS  = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASS = os.environ["GMAIL_APP_PASS"]
TO_EMAIL       = "milonitze@gmail.com"

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# ── Topics ───────────────────────────────────────────────────────────────────
TOPICS = [
    {
        "label": "World News",
        "emoji": "🌍",
        "nyt_query": "international geopolitics",
        "nyt_section": "world",
        "newsapi_query": "international OR geopolitics OR Ukraine OR China OR Middle East OR Europe",
        "use_nyt": True,
    },
    {
        "label": "USA News",
        "emoji": "🇺🇸",
        "nyt_query": "united states politics government",
        "nyt_section": "us",
        "newsapi_query": "United States OR Congress OR White House OR federal government OR American politics",
        "use_nyt": True,
    },
    {
        "label": "Infrastructure & Industrials",
        "emoji": "🏗️",
        "nyt_query": "infrastructure real estate industrial energy",
        "nyt_section": "business",
        "newsapi_query": "infrastructure OR real estate OR industrial OR construction OR utilities OR energy OR REIT OR manufacturing",
        "use_nyt": True,
    },
    {
        "label": "Tech / AI & Emerging Trends",
        "emoji": "💡",
        "nyt_query": "artificial intelligence technology",
        "nyt_section": "technology",
        "newsapi_query": "artificial intelligence OR machine learning OR tech industry OR OpenAI OR semiconductor OR startup",
        "use_nyt": True,
    },
    {
        "label": "Finance & Markets",
        "emoji": "📈",
        "nyt_query": "investment banking finance wall street",
        "nyt_section": "business",
        "newsapi_query": "investment banking OR mergers acquisitions OR private equity OR Wall Street OR IPO OR hedge fund OR Federal Reserve",
        "use_nyt": True,
    },
]

# ── Song picks ────────────────────────────────────────────────────────────────
SONG_PICKS = [
    ("Lose It", "Fisher", "https://open.spotify.com/search/Lose%20It%20Fisher", "FISHER's breakout track. Raw, relentless tech house that doesn't let up for four minutes."),
    ("Arnold Grove", "John Summit", "https://open.spotify.com/search/Arnold%20Grove%20John%20Summit", "John Summit at his peak — driving bassline, just enough melody to keep it from being pure bludgeon."),
    ("Show Me Love", "Robin S", "https://open.spotify.com/search/Show%20Me%20Love%20Robin%20S", "The original house classic. If you know Chris Lake's world, you need to know where it came from."),
    ("Atmosphere", "Joris Voorn", "https://open.spotify.com/search/Atmosphere%20Joris%20Voorn", "Deep, hypnotic progressive house. The kind of track that makes a dark room feel massive."),
    ("Fading", "Lane 8", "https://open.spotify.com/search/Fading%20Lane%208", "Lane 8 makes melodic house that hits like RÜFÜS but with a darker undertow. Start here."),
    ("Parachute", "Lane 8", "https://open.spotify.com/search/Parachute%20Lane%208", "One of his most emotional tracks — the build in the second half is absurd."),
    ("Cardinal", "Tourist", "https://open.spotify.com/search/Cardinal%20Tourist", "Tourist sits between electronica and deep house. This one is gorgeous and deeply underplayed."),
    ("Nightcrawler", "Bicep", "https://open.spotify.com/search/Nightcrawler%20Bicep", "You have Glue already — Nightcrawler is Bicep's most emotionally charged track. Essential."),
    ("Apricots", "Bicep", "https://open.spotify.com/search/Apricots%20Bicep", "Bicep's Isles album is one of the best electronic albums of the decade. This is the opener."),
    ("Atlas", "Bicep", "https://open.spotify.com/search/Atlas%20Bicep", "More restrained than their club stuff but the atmosphere is unreal. Great for headphones."),
    ("Back & Forth", "Keinemusik", "https://open.spotify.com/search/Back%20%26%20Forth%20Keinemusik", "You have Keinemusik via the Moderat remix — this is their own best track. Deep, hypnotic, long."),
    ("Cola", "CamelPhat, Elderbrook", "https://open.spotify.com/search/Cola%20CamelPhat%20Elderbrook", "One of the defining tracks of the melodic techno crossover moment. Elderbrook's vocal is perfect."),
    ("Stratus", "CamelPhat", "https://open.spotify.com/search/Stratus%20CamelPhat", "Darker and more driving than Cola — shows their range as producers."),
    ("The Path", "CamelPhat, RY X", "https://open.spotify.com/search/The%20Path%20CamelPhat%20RY%20X", "RY X brings the same emotional weight as Curtis Harding on the RÜFÜS track. Stunning collab."),
    ("Beautiful Lie", "Anyma", "https://open.spotify.com/search/Beautiful%20Lie%20Anyma", "Anyma is the biggest name in melodic techno right now. This is his most accessible track."),
    ("Come", "Anyma, Rebūke", "https://open.spotify.com/search/Come%20Anyma%20Rebuke", "More driving than Beautiful Lie but same DNA. Peaked on every major festival stage in 2023."),
    ("In Color", "Massano", "https://open.spotify.com/search/In%20Color%20Massano", "Afterlife label artist with a sound between Anyma and Tale Of Us. This track is a slow burner."),
    ("Offline", "Massano", "https://open.spotify.com/search/Offline%20Massano", "His debut EP track that put him on the map. Melodic, emotional, perfectly paced."),
    ("Moments", "Innellea", "https://open.spotify.com/search/Moments%20Innellea", "German producer on the Afterlife circuit. Dark melodic techno that rewards patience."),
    ("Breathe", "Stephan Bodzin", "https://open.spotify.com/search/Breathe%20Stephan%20Bodzin", "Stephan Bodzin is a legend in melodic techno. Breathe is one of his most accessible entry points."),
    ("Pray for Me", "Peggy Gou", "https://open.spotify.com/search/Pray%20for%20Me%20Peggy%20Gou", "Peggy Gou blends disco and deep house in a way that's completely her own. You need this."),
    ("All That Matters", "Hot Since 82", "https://open.spotify.com/search/All%20That%20Matters%20Hot%20Since%2082", "Driving deep house from one of Ibiza's most consistent selectors."),
    ("Numb", "Elderbrook", "https://open.spotify.com/search/Numb%20Elderbrook", "Elderbrook's solo work is just as strong as his collabs. Melancholic, atmospheric electronica."),
    ("Talking", "Bicep", "https://open.spotify.com/search/Talking%20Bicep", "Rave-influenced but with a melody that sticks with you for days."),
    ("Good Grief", "Tale Of Us", "https://open.spotify.com/search/Good%20Grief%20Tale%20Of%20Us", "Tale Of Us founded Afterlife and this track explains the whole label's aesthetic in six minutes."),
    ("Talisman", "Solomun", "https://open.spotify.com/search/Talisman%20Solomun", "Solomun is the king of Ibiza deep house. Talisman is his most emotionally resonant track."),
    ("Rub a Dub", "Patrick Topping", "https://open.spotify.com/search/Rub%20a%20Dub%20Patrick%20Topping", "Pure tech house fun. No pretension, just an immaculate groove."),
    ("Guru", "Mau P", "https://open.spotify.com/search/Guru%20Mau%20P", "Mau P's biggest track. Hard-hitting tech house that went everywhere in 2023."),
    ("Waiting Game", "Crooked Colours", "https://open.spotify.com/search/Waiting%20Game%20Crooked%20Colours", "Australian trio in the RÜFÜS lane. This one is warmer and more melodic than most of their stuff."),
    ("Fractures", "Bonobo", "https://open.spotify.com/search/Fractures%20Bonobo", "Bonobo sits between jazz and electronic. Fractures is his most urgent and club-ready track."),
    ("Kong", "Bonobo", "https://open.spotify.com/search/Kong%20Bonobo", "Darker and more driving than his usual sound. Worth hearing if you only know his ambient side."),
    ("Opus", "Eric Prydz", "https://open.spotify.com/search/Opus%20Eric%20Prydz", "The most euphoric progressive house track ever made. If you haven't heard this, stop everything."),
    ("Pjanoo", "Eric Prydz", "https://open.spotify.com/search/Pjanoo%20Eric%20Prydz", "The piano riff that defined a generation of progressive house. An absolute landmark."),
    ("Nicte", "Massano, PAWSA", "https://open.spotify.com/search/Nicte%20Massano%20PAWSA", "A more driving, darker side of Massano. Great late night energy."),
    ("Reverie", "Lane 8, Kidnap", "https://open.spotify.com/search/Reverie%20Lane%208%20Kidnap", "Lane 8 and Kidnap is a perfect pairing. Emotional, melodic, and beautifully produced."),
    ("Chest", "John Summit, Hayla", "https://open.spotify.com/search/Chest%20John%20Summit%20Hayla", "Summit adding a vocal element to his usual driving tech house. One of his best recent tracks."),
    ("Your Love", "Franky Wah", "https://open.spotify.com/search/Your%20Love%20Franky%20Wah", "UK producer making emotional melodic house. This one is massive and completely underrated."),
    ("No Sleep", "Fisher, Aatig", "https://open.spotify.com/search/No%20Sleep%20Fisher%20Aatig", "FISHER and Aatig — you know Aatig from Chris Lake collabs. This one hits just as hard."),
    ("Closer", "Pretty Lights", "https://open.spotify.com/search/Closer%20Pretty%20Lights", "Electronic soul at its best. A completely different corner of the genre worth exploring."),
    ("High & Low", "Elderbrook, Rudimental", "https://open.spotify.com/search/High%20Low%20Elderbrook%20Rudimental", "Elderbrook over a more uptempo production. Great energy without losing the emotional core."),
]
# ─────────────────────────────────────────────────────────────────────────────


def get_daily_song():
    day_seed = datetime.now().strftime("%Y-%m-%d")
    idx = int(hashlib.md5(day_seed.encode()).hexdigest(), 16) % len(SONG_PICKS)
    return SONG_PICKS[idx]


def fetch_nyt_articles(query, section, max_results=4):
    """Fetch from NYT Article Search API, prioritizing by relevance and recency."""
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d")
    today     = datetime.utcnow().strftime("%Y%m%d")
    try:
        url = "https://api.nytimes.com/svc/search/v2/articlesearch.json"
        params = {
            "q":           query,
            "fq":          f'section_name:("{section}")',
            "begin_date":  yesterday,
            "end_date":    today,
            "sort":        "relevance",
            "api-key":     NYT_API_KEY,
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        docs = r.json().get("response", {}).get("docs", [])
        results = []
        for d in docs[:max_results]:
            headline = d.get("headline", {}).get("main", "")
            abstract = d.get("abstract", "") or d.get("snippet", "")
            web_url  = d.get("web_url", "#")
            source   = "The New York Times"
            if headline:
                results.append({"title": headline, "description": abstract, "url": web_url, "source": source})
        return results
    except Exception as e:
        print(f"NYT fetch error: {e}")
        return []


def fetch_newsapi_articles(query, max_results=4):
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        params = {
            "q":        query,
            "from":     yesterday,
            "sortBy":   "popularity",
            "pageSize": max_results,
            "language": "en",
            "apiKey":   NEWS_API_KEY,
        }
        resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        results = []
        for a in articles:
            if a.get("title") and a.get("description") and "[Removed]" not in a.get("title", ""):
                results.append({
                    "title":       a.get("title", ""),
                    "description": a.get("description", ""),
                    "url":         a.get("url", "#"),
                    "source":      a.get("source", {}).get("name", ""),
                })
        return results
    except Exception as e:
        print(f"NewsAPI fetch error: {e}")
        return []


def fetch_articles_for_topic(topic):
    """Try NYT first, fall back to NewsAPI if not enough results."""
    articles = []
    if topic.get("use_nyt"):
        articles = fetch_nyt_articles(topic["nyt_query"], topic["nyt_section"])
    if len(articles) < 2:
        print(f"  NYT returned {len(articles)}, supplementing with NewsAPI...")
        newsapi = fetch_newsapi_articles(topic["newsapi_query"])
        articles = articles + newsapi
    return articles[:4]


def generate_section_summary(topic_label, articles):
    """Use Claude to write a digest summary from the article headlines and abstracts."""
    if not articles:
        return "No articles available for this section today."

    article_text = "\n\n".join(
        f"Source: {a['source']}\nHeadline: {a['title']}\nAbstract: {a['description']}"
        for a in articles
    )

    prompt = f"""You are writing the '{topic_label}' section of a morning news briefing email called Nitze's News.

Here are today's top articles on this topic:

{article_text}

Write a 3-5 sentence summary of what is happening in this topic area today. Write it like a smart, concise morning briefing — not a list of article summaries, but a cohesive paragraph that tells the reader what's going on. Be direct and informative. Do not use bullet points. Do not mention article titles or sources by name. Do not use em dashes."""

    try:
        resp = requests.post(
            ANTHROPIC_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 300,
                "messages":   [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"].strip()
    except Exception as e:
        print(f"Claude summary error: {e}")
        # Fallback: just use the first abstract
        return articles[0]["description"] if articles else "No summary available."


def fetch_trending_stocks():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/trending/US?count=10"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return [item["symbol"] for item in r.json()["finance"]["result"][0]["quotes"]][:10]
    except Exception:
        return ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","JPM","GS","BAC"]


def fetch_market_snapshot():
    indices, stocks = [], []
    for symbol, name in [("^GSPC", "S&P 500"), ("^IXIC", "Nasdaq")]:
        try:
            r    = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            meta = r.json()["chart"]["result"][0]["meta"]
            price, prev = meta.get("regularMarketPrice", 0), meta.get("chartPreviousClose", 0)
            chg  = price - prev
            pct  = (chg / prev * 100) if prev else 0
            indices.append({"name": name, "price": f"{price:,.2f}", "chg": f"{'▲' if chg>=0 else '▼'} {abs(chg):,.2f} ({abs(pct):.2f}%)", "color": "#16a34a" if chg>=0 else "#dc2626"})
        except Exception:
            indices.append({"name": name, "price": "N/A", "chg": "N/A", "color": "#888"})

    for symbol in fetch_trending_stocks():
        try:
            r    = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            meta = r.json()["chart"]["result"][0]["meta"]
            price, prev = meta.get("regularMarketPrice", 0), meta.get("chartPreviousClose", 0)
            chg  = price - prev
            pct  = (chg / prev * 100) if prev else 0
            stocks.append({"symbol": symbol, "price": f"${price:,.2f}", "chg": f"{'▲' if chg>=0 else '▼'} {abs(pct):.2f}%", "color": "#16a34a" if chg>=0 else "#dc2626"})
        except Exception:
            stocks.append({"symbol": symbol, "price": "N/A", "chg": "N/A", "color": "#888"})

    return indices, stocks


# ── HTML rendering ────────────────────────────────────────────────────────────

def render_market_snapshot(indices, stocks):
    index_cards = "".join(f"""
    <td width="50%" style="padding:0 6px;">
      <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:14px 16px;">
        <p style="margin:0 0 4px 0;font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.08em;font-family:-apple-system,sans-serif;">{i['name']}</p>
        <p style="margin:0 0 2px 0;font-size:22px;font-weight:700;color:#1a1a1a;font-family:-apple-system,sans-serif;">{i['price']}</p>
        <p style="margin:0;font-size:13px;font-weight:600;color:{i['color']};font-family:-apple-system,sans-serif;">{i['chg']}</p>
      </div>
    </td>""" for i in indices)

    stock_rows = "".join(f"""
    <tr>
      <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;"><span style="font-size:14px;font-weight:700;color:#1a1a1a;font-family:-apple-system,sans-serif;">{s['symbol']}</span></td>
      <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;text-align:right;"><span style="font-size:14px;color:#374151;font-family:-apple-system,sans-serif;">{s['price']}</span></td>
      <td style="padding:10px 0;border-bottom:1px solid #f3f4f6;text-align:right;"><span style="font-size:13px;font-weight:600;color:{s['color']};font-family:-apple-system,sans-serif;">{s['chg']}</span></td>
    </tr>""" for s in stocks)

    return f"""
    <tr><td style="padding:28px 0 0 0;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="padding-bottom:14px;border-bottom:3px solid #1a1a1a;">
          <span style="font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#1a1a1a;font-family:-apple-system,sans-serif;">📊 Quick Daily Market Snapshot</span>
        </td></tr>
        <tr><td style="padding-top:16px;"><table width="100%" cellpadding="0" cellspacing="0"><tr>{index_cards}</tr></table></td></tr>
        <tr><td style="padding-top:20px;">
          <p style="margin:0 0 10px 0;font-size:12px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.08em;font-family:-apple-system,sans-serif;">Trending Stocks</p>
          <table width="100%" cellpadding="0" cellspacing="0">{stock_rows}</table>
        </td></tr>
      </table>
    </td></tr>"""


def render_news_section(topic, articles, summary):
    if not articles:
        return ""

    links = "".join(f"""
    <tr><td style="padding:8px 0;border-bottom:1px solid #f3f4f6;">
      <span style="font-size:11px;font-weight:700;color:#888;font-family:-apple-system,sans-serif;">{a['source']} &nbsp;</span>
      <a href="{a['url']}" style="font-size:13px;color:#1a1a1a;text-decoration:none;font-family:-apple-system,sans-serif;">{a['title']} &rarr;</a>
    </td></tr>""" for a in articles)

    return f"""
    <tr><td style="padding:28px 0 0 0;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="padding-bottom:14px;border-bottom:3px solid #1a1a1a;">
          <span style="font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#1a1a1a;font-family:-apple-system,sans-serif;">{topic['emoji']} {topic['label']}</span>
        </td></tr>
        <tr><td style="padding:16px 0 14px 0;">
          <p style="margin:0;font-size:14px;color:#1a1a1a;line-height:1.75;font-family:Georgia,serif;">{summary}</p>
        </td></tr>
        <tr><td style="padding-top:4px;">
          <p style="margin:0 0 8px 0;font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.08em;font-family:-apple-system,sans-serif;">Read More</p>
          <table width="100%" cellpadding="0" cellspacing="0">{links}</table>
        </td></tr>
      </table>
    </td></tr>"""


def render_song_section(song):
    track, artist, link, blurb = song
    return f"""
    <tr><td style="padding:28px 0 0 0;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="padding-bottom:14px;border-bottom:3px solid #1a1a1a;">
          <span style="font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#1a1a1a;font-family:-apple-system,sans-serif;">🎵 Song of the Day</span>
        </td></tr>
        <tr><td style="padding:18px 0;">
          <p style="margin:0 0 2px 0;font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:.08em;font-family:-apple-system,sans-serif;">{artist}</p>
          <a href="{link}" style="font-size:18px;font-weight:700;color:#1a1a1a;text-decoration:none;display:block;margin-bottom:8px;font-family:Georgia,serif;">{track}</a>
          <p style="margin:0 0 12px 0;font-size:13px;color:#555;line-height:1.6;font-family:Georgia,serif;">{blurb}</p>
          <a href="{link}" style="display:inline-block;background:#1DB954;color:#fff;font-size:12px;font-weight:700;text-decoration:none;padding:8px 16px;border-radius:20px;font-family:-apple-system,sans-serif;">Listen on Spotify &rarr;</a>
        </td></tr>
      </table>
    </td></tr>"""


def build_html(indices, stocks, topic_sections, song):
    date_str  = datetime.now().strftime("%A, %B %d, %Y")
    market    = render_market_snapshot(indices, stocks)
    sections  = "".join(render_news_section(t, a, s) for t, a, s in topic_sections)
    song_sec  = render_song_section(song)

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Georgia,'Times New Roman',serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f4;padding:32px 16px;">
    <tr><td align="center">
      <table width="620" cellpadding="0" cellspacing="0" style="background-color:#fff;">
        <tr><td style="padding:36px 40px 24px 40px;border-bottom:3px solid #1a1a1a;">
          <p style="margin:0 0 6px 0;font-size:11px;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:#888;font-family:-apple-system,sans-serif;">{date_str}</p>
          <h1 style="margin:0;font-size:38px;font-weight:700;color:#1a1a1a;letter-spacing:-1px;font-family:Georgia,serif;">Nitze's News</h1>
          <p style="margin:8px 0 0 0;font-size:13px;color:#888;font-family:-apple-system,sans-serif;">Your daily briefing on markets, world affairs, and industry</p>
        </td></tr>
        <tr><td style="padding:0 40px 40px 40px;">
          <table width="100%" cellpadding="0" cellspacing="0">
            {market}
            {sections}
            {song_sec}
          </table>
        </td></tr>
        <tr><td style="padding:20px 40px;background-color:#f9f9f9;border-top:1px solid #eee;">
          <p style="margin:0;font-size:11px;color:#aaa;text-align:center;font-family:-apple-system,sans-serif;">
            Nitze's News &nbsp;·&nbsp; NYT, NewsAPI &amp; Yahoo Finance &nbsp;·&nbsp; Delivered daily at 8 AM ET
          </p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Nitze's News — {datetime.now().strftime('%A, %b %d')}"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.sendmail(GMAIL_ADDRESS, TO_EMAIL, msg.as_string())
    print("Email sent successfully.")


def main():
    print("Fetching market data...")
    indices, stocks = fetch_market_snapshot()

    topic_sections = []
    for t in TOPICS:
        print(f"Fetching: {t['label']} ...")
        articles = fetch_articles_for_topic(t)
        print(f"  Got {len(articles)} articles, generating summary...")
        summary  = generate_section_summary(t["label"], articles)
        topic_sections.append((t, articles, summary))

    song = get_daily_song()
    print(f"Today's song: {song[0]} — {song[1]}")

    html = build_html(indices, stocks, topic_sections, song)
    send_email(html)
    print("Done.")


if __name__ == "__main__":
    main()
