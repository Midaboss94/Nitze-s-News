import os
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ── Configuration ────────────────────────────────────────────────────────────
NEWS_API_KEY   = os.environ["NEWS_API_KEY"]
GMAIL_ADDRESS  = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASS = os.environ["GMAIL_APP_PASS"]
TO_EMAIL       = "milonitze@gmail.com"

TOPICS = [
    {"label": "Business & Markets", "query": "stock market OR economy OR finance OR Wall Street"},
    {"label": "Technology & AI",    "query": "artificial intelligence OR tech industry OR Silicon Valley"},
    {"label": "World News",         "query": "international news OR geopolitics OR global affairs"},
]

SOURCES = "the-wall-street-journal,the-new-york-times,the-atlantic,reuters,associated-press,bloomberg,bbc-news,financial-times"
# ─────────────────────────────────────────────────────────────────────────────


def fetch_articles(query, page_size=5):
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q":        query,
        "from":     yesterday,
        "sortBy":   "popularity",
        "pageSize": page_size,
        "sources":  SOURCES,
        "apiKey":   NEWS_API_KEY,
        "language": "en",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("articles", [])


def build_html(topics_articles):
    date_str = datetime.now().strftime("%A, %B %d, %Y")

    sections = ""
    for topic, articles in topics_articles:
        if not articles:
            continue
        items = ""
        for a in articles:
            source  = a.get("source", {}).get("name", "")
            title   = a.get("title",       "No title")
            desc    = a.get("description") or ""
            url     = a.get("url",         "#")
            items += f"""
            <div style="margin-bottom:20px; padding-bottom:20px; border-bottom:1px solid #e5e7eb;">
              <p style="margin:0 0 4px 0; font-size:12px; color:#6b7280; text-transform:uppercase; letter-spacing:.05em;">{source}</p>
              <a href="{url}" style="font-size:17px; font-weight:600; color:#111827; text-decoration:none; line-height:1.4;">{title}</a>
              <p style="margin:6px 0 0 0; font-size:14px; color:#4b5563; line-height:1.6;">{desc}</p>
            </div>"""

        sections += f"""
        <div style="margin-bottom:36px;">
          <h2 style="font-size:13px; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
                     color:#6b7280; margin:0 0 16px 0; padding-bottom:8px; border-bottom:2px solid #111827;">
            {topic}
          </h2>
          {items}
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0; padding:0; background:#f3f4f6; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6; padding:32px 16px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.1);">

        <!-- Header -->
        <tr>
          <td style="background:#111827; padding:28px 36px;">
            <p style="margin:0; font-size:11px; color:#9ca3af; letter-spacing:.1em; text-transform:uppercase;">Your Morning Brief</p>
            <h1 style="margin:4px 0 0 0; font-size:24px; color:#ffffff; font-weight:700;">{date_str}</h1>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px 36px;">
            {sections}
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f9fafb; padding:20px 36px; border-top:1px solid #e5e7eb;">
            <p style="margin:0; font-size:12px; color:#9ca3af; text-align:center;">
              Powered by NewsAPI &nbsp;·&nbsp; Sources: NYT, WSJ, The Atlantic, Reuters, Bloomberg &amp; more
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Morning Brief — {datetime.now().strftime('%b %d, %Y')}"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.sendmail(GMAIL_ADDRESS, TO_EMAIL, msg.as_string())
    print("Email sent successfully.")


def main():
    topics_articles = []
    for t in TOPICS:
        print(f"Fetching: {t['label']} ...")
        articles = fetch_articles(t["query"])
        topics_articles.append((t["label"], articles))

    html = build_html(topics_articles)
    send_email(html)


if __name__ == "__main__":
    main()
