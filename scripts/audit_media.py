import os
import pandas as pd
import ast

data_dir = "data"
media_dir = "data/dataset_media"

# Ambil semua file CSV final di folder data
csv_files = [f for f in os.listdir(data_dir) if f.startswith("dataset_") and f.endswith("_final.csv")]

laporan = []

for csv_file in csv_files:
    case_name = csv_file.replace("dataset_", "").replace("_final.csv", "")
    df = pd.read_csv(os.path.join(data_dir, csv_file))
    
    # Hitung ekspektasi target media dari kolom extendedEntities
    target_media = 0
    for _, row in df.iterrows():
        media_data = row.get('extendedEntities', None)
        if pd.notna(media_data) and str(media_data).strip() != '{}':
            try:
                entities = ast.literal_eval(str(media_data))
                if 'media' in entities:
                    target_media += len(entities['media'])
            except:
                pass
                
    # Hitung jumlah file fisik di folder
    folder_path = os.path.join(media_dir, case_name)
    terunduh = len(os.listdir(folder_path)) if os.path.exists(folder_path) else 0
    
    status = "✅ Aman" if target_media == terunduh else "⚠️ Cek Ulang"
    
    laporan.append({
        "Kasus": case_name,
        "Target (CSV)": target_media,
        "Terunduh (Folder)": terunduh,
        "Selisih": target_media - terunduh,
        "Status": status
    })
    
# Tampilkan tabel audit
df_laporan = pd.DataFrame(laporan)