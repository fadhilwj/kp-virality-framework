import pandas as pd

# 1. Baca kedua file CSV
df_top = pd.read_csv('data/1_karhutla_top.csv')
df_latest = pd.read_csv('data/1_karhutla_latest.csv')

# 2. Gabung atas-bawah (Concat)
df_gabung = pd.concat([df_top, df_latest], ignore_index=True)

# 3. Buang duplikasi berdasarkan ID Cuitan
df_bersih = df_gabung.drop_duplicates(subset=['id'], keep='first')

# 4. Simpan hasil akhir
df_bersih.to_csv('data/dataset_1_karhutla_final.csv', index=False)

print(f"Total data mentah: {len(df_gabung)}")
print(f"Total data bersih (tanpa duplikat): {len(df_bersih)}")