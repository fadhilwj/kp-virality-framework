import os
import pandas as pd
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv(dotenv_path=".env")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

# Initialize the ApifyClient with your API token
client = ApifyClient(APIFY_API_TOKEN)

# Prepare the Actor input
run_input = {
    "filter:blue_verified": False,
    "filter:consumer_video": False,
    "filter:has_engagement": False,
    "filter:hashtags": False,
    "filter:images": False,
    "filter:links": False,
    "filter:media": False,
    "filter:mentions": False,
    "filter:native_video": False,
    "filter:nativeretweets": False,
    "filter:news": False,
    "filter:pro_video": False,
    "filter:quote": False,
    "filter:replies": False,
    "filter:safe": False,
    "filter:spaces": False,
    "filter:twimg": False,
    "filter:videos": False,
    "filter:vine": False,
    "include:nativeretweets": False,
    "lang": "in",
    "maxItems": 200,
    "queryType": "Latest",
    "searchTerms": [
        "(\"kebakaran hutan\" OR karhutla OR \"kabut asap\") kalimantan"
    ],
    "since_time": "1785888000",
    "until_time": "1788393600"
}

# Run the Actor and wait for it to finish
run = client.actor("CJdippxWmn9uRfooo").call(run_input=run_input) #kaitoeasyapi tweet scraper $0.18/1k tweets

# Fetch and print Actor results from the run's dataset (if there are any)
items = []

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
    items.append(item)

df = pd.DataFrame(items)
df.to_csv("data/1_karhutla_latest.csv", index=False)
print(f"Selesai! {len(df)} cuitan berhasil disimpan ke 1_karhutla_latest.csv")