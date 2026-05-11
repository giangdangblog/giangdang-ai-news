import os
import requests
import feedparser
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_APPLICATION_PASSWORD")

client = OpenAI(api_key=OPENAI_API_KEY)

RSS_FEEDS = [
    "https://vnexpress.net/rss/kinh-doanh.rss",
    "https://cafebiz.vn/thi-truong.rss"
]

KEYWORDS = [
    "kinh doanh",
    "doanh nghiệp",
    "FDI",
    "nhà máy",
    "xây dựng",
    "suất ăn",
    "khu công nghiệp",
]

def keyword_match(title):
    title = title.lower()

    for keyword in KEYWORDS:
        if keyword.lower() in title:
            return True

    return False

def rewrite_article(content):

    prompt = f"""
    Bạn là chuyên gia business content.

    Hãy viết lại bài viết dưới đây theo phong cách:

    - chuyên nghiệp
    - magazine news
    - có góc nhìn phân tích
    - giọng văn thương hiệu cá nhân Giang Đặng
    - chuẩn SEO
    - có tiêu đề hấp dẫn
    - có các heading
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
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

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

        article = requests.get(entry.link)

        soup = BeautifulSoup(article.text, "html.parser")

        paragraphs = soup.find_all("p")

        content = "\n".join([p.get_text() for p in paragraphs])

        rewritten = rewrite_article(content)

        publish_post(title, rewritten)

        posted += 1

print("DONE")
