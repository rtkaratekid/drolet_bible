#!/usr/bin/python3
import html
import os
from googleapiclient.errors import HttpError
import googleapiclient.discovery
import sys

# Add a max to prevent getting stuck in a loop. 20*50 = 1000 videos should be enough for anyone.
MAX_ITERATIONS = 20

# Set up the YouTube Data API client
api_service_name = "youtube"
api_version = "v3"
api_key = os.environ["YOUTUBE_API_KEY"]

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

# Define the search query parameters
channel_id = "UCBYi9loicyfSythDfUKWmfA"
search_query = "Climber's Progression Series"  # Replace with the search query to find the videos

html_content = "<html>"
# html_content += "<head><title>Drolet Bible</title></head>"
html_content += "<body><h1>The Drolet Bible</h1>"  # Add this line to display the title in the body
html_content += "<img src='cult.jpg' alt='Cult Image'>"  # Add this line to include the image

nextPageToken = None

# Fetch all the videos from the channel
for _ in range(MAX_ITERATIONS):
    try:
        search_response = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            q=search_query,
            type="video",
            pageToken=nextPageToken,
            maxResults=50  # Fetch only 50 videos at a time
        ).execute()

        search_results = search_response.get("items", [])

        # sort them by the date they were published
        search_results.sort(key=lambda x: x["snippet"]["publishedAt"])

        for result in search_results:
            title = result["snippet"]["title"]
            decoded_title = html.unescape(title)

            if "Climber's Progression Series" not in decoded_title and "Rock Climber's Improvement Checklist" not in decoded_title and "Climb Harder on Crimps" not in decoded_title:
                continue

            video_id = result["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            html_content += f'<h2><a href="{video_url}">{decoded_title}</a></h2>'

            video_id = result["id"]["videoId"]
            video_response = youtube.videos().list(
                part="snippet",
                id=video_id
            ).execute()
            video_description = video_response.get("items", [])[0]["snippet"]["description"]
            video_description = video_description.split("\n")

            # remove all the lines that don't start with a timestamp formatted like "00:00"
            chapters = [line for line in video_description if len(line) >= 5 and line[2] == ":" and line[5] == " "]
            html_content += "<ol>"
            for i, chapter in enumerate(chapters):
                chapter_parts = chapter.split(" ")
                if len(chapter_parts) >= 2:
                    chapter_title = " ".join(chapter_parts[1:])
                    chapter_timestamp = chapter_parts[0]
                    minutes, seconds = chapter_timestamp.split(":")
                    chapter_url = f"{video_url}&t={minutes}m{seconds}s"
                    html_content += f"<li><a href='{chapter_url}'>{chapter_title}</a></li>"
            html_content += "</ol>"

        nextPageToken = search_response.get("nextPageToken")
        if nextPageToken is None:
            # No more results
            break

    except HttpError as e:
        print("An error occurred while fetching videos from the channel.")
        print(f"Error details: {e}")
        sys.exit(1)

html_content += "</body></html>"

# Write the HTML content to the drolet_bible.html file
with open("drolet_bible.html", "w") as f:
    f.write(html_content)

# Write the Markdown content to the README.md file
with open("README.md", "w") as f:
    f.write(html_content)

