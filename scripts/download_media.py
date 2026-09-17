import pandas as pd
import requests
import os
import ast
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 1. Siapkan folder penyimpanan (Otomatis dibuat jika belum ada)
folder_path = "data/dataset_media/karhutla"
os.makedirs(folder_path, exist_ok=True)

# 2. Setup Session dengan fitur 'Retry with Backoff' sesuai syarat KP
session = requests.Session()
# Konfigurasi: Coba ulang hingga 5 kali jika gagal, dengan jeda waktu yang bertambah (backoff)
retry_strategy = Retry(
    total=5,
    backoff_factor=1.5, # Jeda waktu antar percobaan
    status_forcelist=[429, 500, 502, 503, 504], # Ulangi jika server Twitter down/limit
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

# 3. Baca file CSV
csv_file = "data/dataset_1_karhutla_merged.csv" 
df = pd.read_csv(csv_file)

print(f"Mulai memindai {len(df)} cuitan untuk mencari media dengan mode Retry-Backoff...")

# 4. Looping setiap baris data
for index, row in df.iterrows():
    tweet_id = str(row['id'])
    media_data = row['extendedEntities']
    
    # Lewati jika cuitan hanya berisi teks murni (NaN atau kosong)
    if pd.notna(media_data) and media_data != '{}':
        try:
            # Ubah string JSON dari CSV menjadi tipe data Dictionary Python
            entities = ast.literal_eval(media_data)
            
            if 'media' in entities:
                for i, media_item in enumerate(entities['media']):
                    media_type = media_item.get('type')
                    media_url = ""
                    ext = ""
                    
                    if media_type == 'photo':
                        media_url = media_item.get('media_url_https')
                        ext = ".jpg"
                        
                    elif media_type in ['video', 'animated_gif']:
                        variants = media_item.get('video_info', {}).get('variants', [])
                        mp4_variants = [v for v in variants if v.get('content_type') == 'video/mp4']
                        
                        if mp4_variants:
                            mp4_variants = sorted(mp4_variants, key=lambda x: x.get('bitrate', 0), reverse=True)
                            media_url = mp4_variants[0].get('url')
                            ext = ".mp4"
                    
                    if media_url:
                        file_name = f"{tweet_id}_{i}{ext}"
                        file_path = os.path.join(folder_path, file_name)
                        
                        # Lewati jika file sudah BERHASIL didownload di percobaan sebelumnya
                        if not os.path.exists(file_path):
                            print(f"Mengunduh: {file_name}")
                            try:
                                # Gunakan session.get yang sudah dipersenjatai Retry
                                response = session.get(media_url, timeout=15) 
                                if response.status_code == 200:
                                    with open(file_path, 'wb') as f:
                                        f.write(response.content)
                                else:
                                    print(f"Gagal mengunduh {file_name} - HTTP {response.status_code}")
                            except Exception as req_err:
                                print(f"Gagal setelah retries untuk {file_name}: {req_err}")
        
        except Exception as e:
            print(f"Error memproses Tweet ID {tweet_id}: {e}")

print("\n🎉 Proses ekstraksi dan pengunduhan media selesai!")