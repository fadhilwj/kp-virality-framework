import os
import shutil
import pandas as pd

# 1. Konfigurasi Path (Sesuaikan jika nama folder karhutla-mu berbeda)
csv_gpt6_path = "data/dataset_07_gpt6_merged.csv"
folder_campur = "data/dataset_media/karhutla"  # Folder yang ketambahan media GPT6
folder_gpt6 = "data/dataset_media/07_gpt6"     # Folder tujuan yang benar

# Buat folder target jika belum ada
os.makedirs(folder_gpt6, exist_ok=True)

# 2. Ambil daftar ID Tweet khusus kasus GPT-6
print("Membaca dataset GPT-6...")
df_gpt6 = pd.read_csv(csv_gpt6_path)

# Ubah ID menjadi string untuk dicocokkan dengan nama file
gpt6_ids = set(df_gpt6['id'].astype(str))
print(f"Ditemukan {len(gpt6_ids)} ID Tweet unik dari kasus GPT-6.")

# 3. Proses pemisahan file
moved_count = 0
if not os.path.exists(folder_campur):
    print(f"Folder {folder_campur} tidak ditemukan. Cek kembali path-nya.")
else:
    print(f"Memeriksa file di {folder_campur}...\n")
    for filename in os.listdir(folder_campur):
        # Ekstrak Tweet ID dari nama file (ambil angka sebelum underscore pertama)
        file_tweet_id = filename.split('_')[0]
        
        # Jika ID file tersebut ada di dalam daftar dataset GPT-6, pindahkan
        if file_tweet_id in gpt6_ids:
            source_path = os.path.join(folder_campur, filename)
            dest_path = os.path.join(folder_gpt6, filename)
            
            shutil.move(source_path, dest_path)
            moved_count += 1
            print(f"Dipindahkan: {filename}")

    print(f"\nSelesai! {moved_count} file media berhasil dipulangkan ke folder 07_gpt6.")