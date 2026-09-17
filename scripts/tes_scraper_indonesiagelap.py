import requests
import hashlib
import pandas as pd
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def hash_author_id(raw_id):
    """Anonimisasi identitas pengguna sesuai panduan KP."""
    return hashlib.sha256(str(raw_id).encode('utf-8')).hexdigest()

def get_session():
    """Setup retry with backoff dan pencegahan rate limiting."""
    session = requests.Session()
    retry = Retry(total=4, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def run_local_scraper(keyword, max_pages=3):
    """Menjalankan ekstraksi data simulasi dengan metadata wajib."""
    session = get_session()
    collected_data = []
    
    print(f"[*] Memulai scraping kasus: {keyword}")
    for page in range(1, max_pages + 1):
        print(f"    -> Ekstraksi halaman {page}...")
        time.sleep(2) 
        
        mock_record = {
            "post_id": f"post_{keyword.replace('#', '').lower()}_{page}",
            "parent_post_id": None,
            "timestamp": "2026-08-15 09:30:45",
            "post_type": "Original",
            "author_id": hash_author_id(f"user_asli_{page}"), 
            "follower_count": 1200 + (page * 50),
            "content_hash": hashlib.md5(f"konten uji coba {page}".encode('utf-8')).hexdigest(),
            "collection_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        collected_data.append(mock_record)
    return collected_data

if __name__ == "__main__":
    kasus = "#IndonesiaGelap"
    hasil = run_local_scraper(kasus)
    df = pd.DataFrame(hasil)
    df.to_csv(f"/data/uji_coba_{kasus.replace('#', '')}.csv", index=False)
    print("[*] Selesai! Data uji coba berhasil disimpan ke folder data/")