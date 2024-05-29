import georinex as gr
import numpy as np

# RINEX dosyalarını yükleme
obs_file = r"C:\RTKApp\data\observation\abpo0010.24o"  # Örnek OBS dosya yolu
nav_file = r"C:\RTKApp\data\navigation\ABPO00MDG_R_20240010000_01D_GN.rnx"  # Örnek NAV dosya yolu

obs_data = gr.load(obs_file)
nav_data = gr.load(nav_file)

# OBS verilerindeki gözlemler
observations = obs_data.sel(sv='G01')  # Örnek olarak 'G01' uydusu için gözlemler
print(observations)

# NAV verilerini görüntüleme
print(nav_data)

# Pseudorange ve Carrier Phase verilerini ayıklama
pseudorange = observations['C1'].values  # C1 kod gözlemi
carrier_phase = observations['L1'].values  # L1 taşıyıcı faz gözlemi

# Uyduların konumlarını hesaplama
def calculate_satellite_positions(nav_data, obs_times):
    satellite_positions = {}
    for time in obs_times:
        # 'nearest' yöntemi ile en yakın zaman damgasını bulma
        try:
            satellite_positions[time] = nav_data.sel(time=time, method='nearest').values
        except KeyError as e:
            print(f"Time {time} not found in navigation data: {e}")
            satellite_positions[time] = None
    return satellite_positions

# Pseudorange ve carrier phase düzeltmeleri
def calculate_corrections(pseudorange, carrier_phase, satellite_positions):
    corrections = {}
    # Zaman arası fark
    delta_t = np.diff(pseudorange)
    # Uydu arası fark
    delta_s = pseudorange[:-1] - pseudorange[1:]
    corrections['delta_t'] = delta_t
    corrections['delta_s'] = delta_s
    return corrections

# Uydu konumlarını hesaplama
obs_times = obs_data.time.values
satellite_positions = calculate_satellite_positions(nav_data, obs_times)

# Düzeltmeleri hesaplama
corrections = calculate_corrections(pseudorange, carrier_phase, satellite_positions)
print(corrections)

# Düzeltmeleri txt dosyasına yazma
output_file = 'corrections_output.txt'

with open(output_file, 'w') as f:
    for key, value in corrections.items():
        f.write(f'{key}:\n')
        np.savetxt(f, value, fmt='%0.8f')
        f.write('\n')

print(f'Corrections have been saved to {output_file}')

