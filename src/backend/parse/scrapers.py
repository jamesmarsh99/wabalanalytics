import json
import httpx
from typing import Dict, Optional
import logging
import jmespath
import datetime as dt
from pathlib import Path
from urllib.parse import quote
import pandas as pd

INSTAGRAM_ACCOUNT_DOCUMENT_ID = "9310670392322965"


client = httpx.Client(
    headers={
        # this is internal ID of an instegram backend app. It doesn't change often.
        "x-ig-app-id": "936619743392459",
        # use browser-like features
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

async def scrape_user_posts(username: str, page_size=12, max_pages: Optional[int] = None):
    """Scrape all posts of an Instagram user given the username."""
    base_url = "https://www.instagram.com/graphql/query"
    variables = {
        "after": None,
        "before": None,
        "data": {
            "count": page_size,
            "include_reel_media_seen_timestamp": True,
            "include_relationship_info": True,
            "latest_besties_reel_media": True,
            "latest_reel_media": True
        },
        "first": page_size,
        "last": None,
        "username": f"{username}",
        "__relay_internal__pv__PolarisIsLoggedInrelayprovider": True,
        "__relay_internal__pv__PolarisShareSheetV3relayprovider": True
    }

    prev_cursor = None
    _page_number = 1

    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as session:
        while True:
            body = f"variables={quote(json.dumps(variables, separators=(',', ':')))}&doc_id={INSTAGRAM_ACCOUNT_DOCUMENT_ID}"

            response = await session.post(
                base_url,
                data=body,
                headers={"content-type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()

            with open("ts2.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            posts = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]
            for post in posts["edges"]:
                yield post["node"]

            page_info = posts["page_info"]
            if not page_info["has_next_page"]:
                print(f"scraping posts page {_page_number}")
                break

            if page_info["end_cursor"] == prev_cursor:
                print("found no new posts, breaking")
                break

            prev_cursor = page_info["end_cursor"]
            variables["after"] = page_info["end_cursor"]
            _page_number += 1

            if max_pages and _page_number > max_pages:
                break


def scrape_user(username: str):
    """Scrape Instagram user's data"""
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    return data["data"]["user"]


def parse_user(data: Dict) -> Dict:
    """Parse instagram user's hidden web dataset for user's data"""
    logging.debug("parsing user data {}", data['username'])
    parsed_data = jmespath.search(
        """{
        name: full_name,
        username: username,
        id: id,
        category: category_name,
        business_category: business_category_name,
        phone: business_phone_number,
        email: business_email,
        bio: biography,
        bio_links: bio_links[].url,
        homepage: external_url,        
        followers: edge_followed_by.count,
        follows: edge_follow.count,
        facebook_id: fbid,
        is_private: is_private,
        is_verified: is_verified,
        profile_image: profile_pic_url_hd,
        video_count: edge_felix_video_timeline.count,
        videos: edge_felix_video_timeline.edges[].node.{
            id: id, 
            title: title,
            shortcode: shortcode,
            thumb: display_url,
            url: video_url,
            views: video_view_count,
            tagged: edge_media_to_tagged_user.edges[].node.user.username,
            captions: edge_media_to_caption.edges[].node.text,
            comments_count: edge_media_to_comment.count,
            comments_disabled: comments_disabled,
            taken_at: taken_at_timestamp,
            likes: edge_liked_by.count,
            location: location.name,
            duration: video_duration
        },
        image_count: edge_owner_to_timeline_media.count,
        images: edge_felix_video_timeline.edges[].node.{
            id: id, 
            title: title,
            shortcode: shortcode,
            src: display_url,
            url: video_url,
            views: video_view_count,
            tagged: edge_media_to_tagged_user.edges[].node.user.username,
            captions: edge_media_to_caption.edges[].node.text,
            comments_count: edge_media_to_comment.count,
            comments_disabled: comments_disabled,
            taken_at: taken_at_timestamp,
            likes: edge_liked_by.count,
            location: location.name,
            accesibility_caption: accessibility_caption,
            duration: video_duration
        },
        saved_count: edge_saved_media.count,
        collections_count: edge_saved_media.count,
        related_profiles: edge_related_profiles.edges[].node.username
    }""",
        data,
    )
    COLUMNS_TO_SAVE = ['date', 'followers', 'follows', 'is_private', 'is_verified', 'video_count',
                       'image_count', 'saved_count', 'collections_count']
    parsed_data = {k: v for k, v in parsed_data.items() if k in COLUMNS_TO_SAVE}
    df = pd.DataFrame(parsed_data, index=[0])
    df['date'] = dt.date.today().strftime("%Y-%m-%d")
    return df[COLUMNS_TO_SAVE]

def parse_and_scrape_user(username: str):
    return parse_user(scrape_user(username))

def save_user_data_as_csv(username: Dict, path: str):
    """Save user data as CSV file"""
    df = parse_and_scrape_user(username)
    df.to_csv(path, index=False)
    print(df)
    print(f"Saved instagram data to {path}")

# Example run:
if __name__ == "__main__":
    # TODO: parse args and call the function
    path = Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\instagram\profile\{dt.date.today():%Y%m%d}.csv")
    save_user_data_as_csv("wabiliworkshop", path)

    import asyncio

    async def main():
        posts = [post async for post in scrape_user_posts("wabiliworkshop")]
        post_information_to_keep = ('caption', 'link', 'title', 'comment_count', 'top_likers', 'like_count', 'preview', 'view_count')
        posts_cleaned = [{k: v for k, v in post.items() if k in post_information_to_keep} for post in posts]
        def parse_caption_from_post(post):
            caption = post.pop('caption')
            post['caption'] = caption['text'].replace('\n', ' ').replace(',', ' ')
            post['time'] = pd.Timestamp(caption['created_at'], unit='s')
            return post
        posts_cleaned = [parse_caption_from_post(post) for post in posts_cleaned]
        posts = pd.DataFrame(posts_cleaned)
        path = Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\instagram\posts\{dt.date.today():%Y%m%d}.csv")
        posts.to_csv(path, index=False)

    asyncio.run(main())


