from googleapiclient.discovery import build
import pandas as pd
import requests


def fetch_youtube_data(api_key, channel_id, start_date, end_date):
    video_details = []
    page_token = None

    while True:
        search_url = (
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}"
            f"&type=video&eventType=completed&publishedAfter={start_date}&publishedBefore={end_date}"
            f"&maxResults=50&key={api_key}"
        )

        if page_token:
            search_url += f"&pageToken={page_token}"

        search_response = requests.get(search_url).json()
        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

        if video_ids:
            stats_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={','.join(video_ids)}&key={api_key}"
            stats_response = requests.get(stats_url).json()

            for item in stats_response.get("items", []):
                video_info = {
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "video_url": f"https://www.youtube.com/watch?v={item['id']}",
                    "published_date": item["snippet"].get("publishedAt", "N/A"),
                    "views": item["statistics"].get("viewCount", "N/A"),
                    "likes": item["statistics"].get("likeCount", "N/A"),
                    "comments": item["statistics"].get("commentCount", "N/A"),
                }
                video_details.append(video_info)

        page_token = search_response.get("nextPageToken")
        if not page_token:
            break

    return pd.DataFrame(video_details)
