import os
import time
import requests
import pandas as pd
from datetime import datetime

# ==========================================
# 1. KONFIGURASI UJI COBA
# ==========================================
TEST_TWEET_IDS = [
    "2100119993363177546", # tweet case maudy ayunda
    "2098817155349479570",
    "2100164813926064200"
]
CASE_NAME = "uji_coba_manual"
INTERVAL_MINUTES = 2
MAX_ITERATIONS = 3

os.makedirs("data/polling", exist_ok=True)
csv_path = f"data/polling/timeseries_{CASE_NAME}.csv"

# ==========================================
# 2. FUNGSI TARIK DATA MANUAL (100% GRATIS)
# ==========================================
def fetch_metrics_manual(tweet_id):
    # Menggunakan endpoint embed/syndication bawaan Twitter (tanpa login)
    url = f"https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "tweet_id": tweet_id,
                "likeCount": data.get("favorite_count", 0),
                "replyCount": data.get("conversation_count", 0),
                "retweetCount": data.get("news_action_type", 0), # Terkadang disembunyikan di versi syndication baru
                "viewCount": data.get("ext_views", {}).get("count", 0) # Menangkap views jika ada
            }
        else:
            print(f"    ❌ Gagal mengambil ID {tweet_id} (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"    ❌ Error koneksi ID {tweet_id}: {e}")
        return None

# ==========================================
# 3. LOOP UJI COBA
# ==========================================
print(f"🚀 Memulai Uji Coba Polling Manual ({MAX_ITERATIONS} iterasi, jeda {INTERVAL_MINUTES} menit)")

for iteration in range(1, MAX_ITERATIONS + 1):
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[Iterasi {iteration}/{MAX_ITERATIONS}] Waktu: {timestamp_now}")
    
    polled_data = []
    for tid in TEST_TWEET_IDS:
        metrics = fetch_metrics_manual(tid)
        if metrics:
            metrics["timestamp"] = timestamp_now
            metrics["case_name"] = CASE_NAME
            polled_data.append(metrics)
            print(f"    ✅ ID {tid} -> Likes: {metrics['likeCount']}, Replies: {metrics['replyCount']}")
            
    if polled_data:
        df_polled = pd.DataFrame(polled_data)
        # Susun urutan kolom
        cols = ["timestamp", "case_name", "tweet_id", "likeCount", "replyCount", "retweetCount", "viewCount"]
        df_polled = df_polled[cols]
        
        # Simpan ke CSV
        df_polled.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)
        print(f"    💾 Data tersimpan ke {csv_path}")
        
    if iteration < MAX_ITERATIONS:
        print(f"Menunggu {INTERVAL_MINUTES} menit...")
        time.sleep(INTERVAL_MINUTES * 60)

print("\n🏁 Uji Coba Selesai!")