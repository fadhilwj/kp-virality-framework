import os
import pandas as pd
import requests
import ast
import time
from dotenv import load_dotenv
from apify_client import ApifyClient
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========================================
# 1. KONFIGURASI 13 KASUS FINAL
# ==========================================
CASES_CONFIG = [
    {
        "case_name": "01_indonesia_gelap",
        "search_terms": '(#indonesiagelap OR #indonesiagelap2025 OR #indonesiaterang OR "peringatan darurat")',
        "lang": "in",
        "since_time": "1738540800",  # 3 Februari 2025
        "until_time": "1740960000"   # 3 Maret 2025
    },
    {
        "case_name": "02_kabur_aja_dulu",
        "search_terms": '(#kaburajadulu OR "kabur aja dulu")',
        "lang": "in",
        "since_time": "1738195200",  # 30 Januari 2025
        "until_time": "1740614400"   # 27 Februari 2025
    },
    {
        "case_name": "03_brave_pink_hero_green",
        "search_terms": '("brave pink" OR "hero green" OR "profil pink hijau" OR "17+8 tuntutan")',
        "lang": "in",
        "since_time": "1755561600",  # 19 Agustus 2025
        "until_time": "1757980800"   # 16 September 2025
    },
    {
        "case_name": "04_utas_layanan_kesehatan",
        "search_terms": 'yurizal (bpjs OR nakes OR antre OR "rumah sakit")',
        "lang": "in",
        "since_time": "1784592000",  # 21 Juli 2026
        "until_time": "1787011200"   # 18 Agustus 2026
    },
    {
        "case_name": "05_isu_demo_agustus",
        "search_terms": '("demo agustus 2026" OR "demo dpr" OR "ruu perampasan aset" OR "perampasan aset" OR ampb OR senayan)',
        "lang": "in",
        "since_time": "1786579200",  # 13 Agustus 2026
        "until_time": "1788998400"   # 10 September 2026
    },
    {
        "case_name": "06_mbg",
        "search_terms": '(mbg OR "makan bergizi gratis" OR "keracunan mbg")',
        "lang": "in",
        "since_time": "1787270400",  # 21 Agustus 2026
        "until_time": "1789689600"   # 18 September 2026
    },
    # {
    #     "case_name": "07_gpt6",
    #     "search_terms": '(gpt6 OR "gpt 6" OR "chatgpt 6" OR "openai gpt6")',
    #     "lang": "en",  # Bahasa Inggris
    #     "since_time": "1787184000",  # 20 Agustus 2026
    #     "until_time": "1789603200"   # 17 September 2026
    # },
    {
        "case_name": "08_ui_bevan_porsche",
        "search_terms": '"mahasiswa ui" AND (bevan OR porsche OR "bawa porsche")',
        "lang": "in",
        "since_time": "1787529600",  # 24 Agustus 2026
        "until_time": "1789948800"   # 21 September 2026
    },
    {
        "case_name": "10_gempa_ntt",
        "search_terms": 'gempa (ntt OR "nusa tenggara timur" OR kupang OR flores)',
        "lang": "in",
        "since_time": "1785542400",  # 1 Agustus 2026
        "until_time": "1787961600"   # 29 Agustus 2026
    },
    {
        "case_name": "11_anak_krakatau",
        "search_terms": '(krakatau OR "anak krakatau" OR erupsi OR "gunung meletus")',
        "lang": "in",
        "since_time": "1787356800",  # 22 Agustus 2026
        "until_time": "1789776000"   # 19 September 2026
    },
    {
        "case_name": "12_reshuffle_purbaya",
        "search_terms": '("reshuffle kemenkeu" OR "reshuffle kementerian keuangan" OR purbaya OR "reshuffle purbaya" OR "purbaya dicabut" OR "purbaya dipecat" OR "purbaya dicopot")',
        "lang": "in",
        "since_time": "1788134400",  # 31 Agustus 2026
        "until_time": "1790553600"   # 28 September 2026
    },
    {
        "case_name": "13_iphone_series",
        "search_terms": '("iphone 18" OR "iphone 18 pro" OR "iphone duo" OR "apple event")',
        "lang": "en",  # Bahasa Inggris
        "since_time": "1787702400",  # 26 Agustus 2026
        "until_time": "1790121600"   # 23 September 2026
    },
    {
        "case_name": "14_maudy_ayunda",
        "search_terms": '("maudy ayunda" OR maudy) (mindfulness OR nirempati OR empati OR "tone deaf")',
        "lang": "in",
        "since_time": "1788134400",  # 31 Agustus 2026
        "until_time": "1790553600"   # 28 September 2026
    }
]

# ==========================================
# 2. SETUP & INISIALISASI
# ==========================================
load_dotenv(dotenv_path=".env")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
client = ApifyClient(APIFY_API_TOKEN)

# Setup Session untuk Download Media (Retry Backoff)
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

os.makedirs("data", exist_ok=True)

# ==========================================
# 3. FUNGSI-FUNGSI PIPELINE
# ==========================================

def run_scraper(case_name, query_type, search_terms, since, until, lang_code):
    print(f"\n[{case_name}] Memulai Scraping '{query_type}' (Bahasa: {lang_code})...")
    run_input = {
        "filter:blue_verified": False, "filter:consumer_video": False,
        "filter:has_engagement": False, "filter:hashtags": False,
        "filter:images": False, "filter:links": False,
        "filter:media": False, "filter:mentions": False,
        "filter:native_video": False, "filter:nativeretweets": False,
        "filter:news": False, "filter:pro_video": False,
        "filter:quote": False, "filter:replies": False,
        "filter:safe": False, "filter:spaces": False,
        "filter:twimg": False, "filter:videos": False,
        "filter:vine": False, "include:nativeretweets": False,
        "lang": lang_code, # Parameter dinamis bahasa diinjeksi di sini
        "maxItems": 200,
        "queryType": query_type,
        "searchTerms": [search_terms],
        "since_time": since,
        "until_time": until
    }
    
    run = client.actor("CJdippxWmn9uRfooo").call(run_input=run_input)
    
    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)
        
    df = pd.DataFrame(items)
    file_path = f"data/{case_name}_{query_type.lower()}.csv"
    df.to_csv(file_path, index=False)
    print(f"[{case_name}] Sukses Scraping '{query_type}': {len(df)} cuitan disimpan ke {file_path}")
    return file_path

def run_merger(case_name, file_top, file_latest):
    print(f"[{case_name}] Menggabungkan dan membuang duplikat...")
    df_top = pd.read_csv(file_top)
    df_latest = pd.read_csv(file_latest)
    
    df_gabung = pd.concat([df_top, df_latest], ignore_index=True)
    df_bersih = df_gabung.drop_duplicates(subset=['id'], keep='first')
    
    final_path = f"data/dataset_{case_name}_final.csv"
    df_bersih.to_csv(final_path, index=False)
    print(f"[{case_name}] Data final bersih: {len(df_bersih)} cuitan tersimpan di {final_path}")
    return final_path, df_bersih

def run_media_downloader(case_name, df_final):
    folder_path = f"data/dataset_media/{case_name}"
    os.makedirs(folder_path, exist_ok=True)
    
    print(f"[{case_name}] Mulai mengunduh media ke {folder_path}...")
    
    for index, row in df_final.iterrows():
        tweet_id = str(row.get('id', ''))
        media_data = row.get('extendedEntities', None)
        
        if pd.notna(media_data) and media_data != '{}':
            try:
                entities = ast.literal_eval(str(media_data))
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
                            
                            if not os.path.exists(file_path):
                                try:
                                    response = session.get(media_url, timeout=15)
                                    if response.status_code == 200:
                                        with open(file_path, 'wb') as f:
                                            f.write(response.content)
                                except Exception as req_err:
                                    print(f"    -> Gagal mengunduh {file_name}: {req_err}")
            except Exception as e:
                print(f"    -> Error parsing media untuk Tweet {tweet_id}: {e}")
    print(f"[{case_name}] Unduh media selesai!")

# ==========================================
# 4. EKSEKUSI MASTER LOOP
# ==========================================
if __name__ == "__main__":
    print(f"🚀 Memulai Master Pipeline untuk {len(CASES_CONFIG)} Kasus...")
    
    for config in CASES_CONFIG:
        case = config["case_name"]
        
        try:
            print(f"\n{'='*50}\nMEMPROSES KASUS: {case.upper()}\n{'='*50}")
            
            # 1. Scrape Top & Latest (Mengirimkan variabel bahasa dari config)
            file_top = run_scraper(
                case, "Top", config["search_terms"], 
                config["since_time"], config["until_time"], config["lang"]
            )
            file_latest = run_scraper(
                case, "Latest", config["search_terms"], 
                config["since_time"], config["until_time"], config["lang"]
            )
            
            # 2. Merge Dataset
            final_csv, df_final = run_merger(case, file_top, file_latest)
            
            # 3. Download Media
            run_media_downloader(case, df_final)
            
            print(f"✅ KASUS {case.upper()} SELESAI 100%!")
            
            # Jeda 10 detik sebelum lanjut agar sistem Apify/Twitter tidak melimitasi request
            time.sleep(10) 
            
        except Exception as e:
            print(f"❌ ERROR FATAL PADA KASUS {case}: {e}")
            print("Melanjutkan ke kasus berikutnya...")

    print("\n🎉 SEMUA KASUS TELAH SELESAI DIPROSES!")