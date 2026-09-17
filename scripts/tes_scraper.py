import os
import hashlib
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv(dotenv_path=".env")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

def hash_author_id(raw_id):
    """Menerapkan skema anonimisasi identitas pengguna sesuai panduan KP."""
    if not raw_id:
        return None
    return hashlib.sha256(str(raw_id).encode('utf-8')).hexdigest()

def generate_content_hash(text):
    """Membentuk content hash sebagai dasar deteksi duplikasi (reupload)."""
    if not text:
        return None
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def run_apify_scraper(keyword, max_items=20):
    print(f"[*] Menghubungi Apify untuk mengambil data kasus: {keyword}...")
    
    client = ApifyClient(APIFY_API_TOKEN)
    
    actor_id = "apidojo/tweet-scraper" 
    
    run_input = {
        "searchTerms": [keyword],
        "maxItems": max_items,
        "tweetLanguage": "id"
    }
    
    print("    -> Mengeksekusi penarikan data mentah dari X (tunggu beberapa menit)...")
    run = client.actor(actor_id).call(run_input=run_input)
    
    print("    -> Data mentah berhasil ditarik! Memproses ke struktur format KP...")
    collected_data = []
    
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        post_type = "Original"
        if item.get("isReply"):
            post_type = "Reply"
        elif item.get("isQuote"):
            post_type = "Quote"
        elif item.get("isRetweet"):
            post_type = "Repost"

        parent_id = item.get("quoteId") or item.get("inReplyToTweetId") or None

        record = {
            "post_id": item.get("id"),
            "parent_post_id": parent_id,
            "timestamp": pd.to_datetime(item.get("createdAt")).strftime("%Y-%m-%d %H:%M:%S") if item.get("createdAt") else None,
            "post_type": post_type,
            "author_id": hash_author_id(item.get("author", {}).get("id")),
            "follower_count": item.get("author", {}).get("followers", 0),
            "content_hash": generate_content_hash(item.get("text")),
            "collection_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "post_url": item.get("url"),
            "likes": item.get("likeCount", 0),
            "retweets": item.get("retweetCount", 0),
            "replies": item.get("replyCount", 0)
        }
        collected_data.append(record)
        
    return collected_data

if __name__ == "__main__":
    kasus_target = "#IndonesiaGelap"
    # tarik 10 data asli dulu sebagai pembuktian integrasi API
    hasil_data = run_apify_scraper(kasus_target, max_items=10)
    
    if hasil_data:
        df = pd.DataFrame(hasil_data)
        tanggal_hari_ini = datetime.now().strftime('%Y%m%d')
        output_file = f"/data/raw_{kasus_target.replace('#', '')}_{tanggal_hari_ini}.csv"
        
        df.to_csv(output_file, index=False)
        print(f"[*] Berhasil! {len(hasil_data)} baris data asli tersimpan di: {output_file}")
    else:
        print("[!] Tidak ada data yang ditemukan. Coba cek koneksi atau limit Apify.")