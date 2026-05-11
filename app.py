import os
import requests
import feedparser
import google.generativeai as genai

from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

# =========================
# GEMINI CONFIG
# =========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# WORDPRESS CONFIG
# =========================

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_APPLICATION_PASSWORD")

# =========================
# RSS FEEDS
# =========================

RSS_FEEDS = [
    "https://vnexpress.net/rss/kinh-doanh.rss",
    "https://cafebiz.vn/thi-truong.rss",
]

# =========================
# KEYWORDS
# =========================

KEYWORDS = [
    "kinh doanh",
    "doanh nghiệp",
    "FDI",
    "nhà máy",
    "xây dựng",
    "suất ăn",
    "khu công nghiệp",
    "logistics",
    "đầu tư",
]

# =========================
# FILTER KEYWORD
# =========================

def keyword_match(title):

    title = title.lower()

    for keyword in KEYWORDS:
        if keyword.lower() in title:
            return True

    return False

# =========================
# AI REWRITE
# =========================

def rewrite_article(content):

    prompt = f"""
    Bạn là chuyên gia business content và SEO.

    Hãy viết lại bài viết dưới đây theo phong cách:

    - chuyên nghiệp
    - magazine news
    - business insight
    - có góc nhìn phân tích
    - mang thương hiệu cá nhân Giang Đặng
    - chuẩn SEO
    - có tiêu đề hấp dẫn
    - có heading H2
    - có kết luận

    Cuối bài:
    - thêm English Summary
    - thêm Chinese Summary
    - thêm dòng:
      'Bản dịch được hỗ trợ bởi trí tuệ nhân tạo.'

    Nội dung:
    {content[:6000]}
    """

    response = model.generate_content(prompt)

    return response.text

# =========================
# WORDPRESS PUBLISH
# =========================

def publish_post(title, content):

    post_url = f"{WP_URL}/wp-json/wp/v2/posts"

    data = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    response = requests.post(
        post_url,
        json=data,
        auth=HTTPBasicAuth(WP_USERNAME, WP_PASSWORD)
    )

    print(response.text)

# =========================
# MAIN
# =========================

posted = 0

for rss in RSS_FEEDS:

    feed = feedparser.parse(rss)

    for entry in feed.entries:

        if posted >= 2:
            break

        title = entry.title

        if not keyword_match(title):
            continue

        print(f"Đang xử lý: {title}")

        try:

            article = requests.get(entry.link)

            soup = BeautifulSoup(article.text, "html.parser")

            paragraphs = soup.find_all("p")

            content = "\n".join([p.get_text() for p in paragraphs])

            rewritten = rewrite_article(content)

            publish_post(title, rewritten)

            posted += 1

        except Exception as e:

            print("Lỗi:", e)

print("DONE")
