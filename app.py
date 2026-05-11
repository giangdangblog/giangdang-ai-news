import os
import requests
import feedparser

from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from openai import OpenAI

# =========================
# OPENROUTER AI
# =========================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

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
    "căng tin",
    "nhà ăn",
]

# =========================
# TAGS
# =========================

TAGS = [
    "BUSINESS",
    "BLOG",
    "LEARN"
]

# =========================
# FILTER
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

    Hãy viết lại bài viết theo phong cách:

    - business magazine
    - chuyên nghiệp
    - chuẩn SEO
    - có phân tích
    - phong cách thương hiệu cá nhân Giang Đặng
    - có góc nhìn doanh nghiệp
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

    response = client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content

# =========================
# WORDPRESS POST
# =========================

def publish_post(title, content):

    url = f"{WP_URL}/wp-json/wp/v2/posts"

    data = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    response = requests.post(
        url,
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
