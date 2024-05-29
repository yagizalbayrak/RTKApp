import georinex as gr
import numpy as np
import datetime

def load_rinex_data(rinex_path):
    # RINEX dosyasını yükle
    obs = gr.load(rinex_path)
    L1C_data = obs['L1C'].dropna(dim='time', how='all')  # Tamamen NaN olan zamanları kaldır
    return L1C_data

def analyze_data(L1C_data):
    # Veri üzerinde basit istatistiksel analizler yap
    mean_values = L1C_data.mean(dim='time')  # Zaman boyunca ortalama değerleri hesapla
    std_deviation = L1C_data.std(dim='time')  # Standart sapmaları hesapla
    return mean_values.values, std_deviation.values

def save_results_to_file(mean_values, std_deviation, filename="results.txt"):
    # Sonuçları bir txt dosyasına kaydet
    now = datetime.datetime.now()  # Şu anki tarih ve zaman
    with open(filename, 'a') as file:
        file.write(f"Analysis Time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"Mean Values: {mean_values}\n")
        file.write(f"Standard Deviations: {std_deviation}\n")
        file.write("--------------------------------------------------\n")

# Örnek kullanım
rinex_path = r"C:\RTKApp\data\ANKR00TUR_R_20190010000_01D_30S_MO_edited.rnx"
L1C_data = load_rinex_data(rinex_path)
mean_values, std_deviation = analyze_data(L1C_data)

# Sonuçları dosyaya kaydet
save_results_to_file(mean_values, std_deviation)

print("Sonuçlar kaydedildi.")
