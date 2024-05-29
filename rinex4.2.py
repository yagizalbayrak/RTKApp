import georinex as gr
import numpy as np

# Sabitler
c = 299792458  # Işık hızı (m/s)
f_L1 = 1575.42e6  # L1 frekansı (Hz)
lambda_L1 = c / f_L1  # L1 dalga boyu (m)

# RINEX dosyasını oku
rinex_file_o = r"C:\RTKApp\data\observation\07590920.05o"
rinex_file_n = r"C:\RTKApp\data\navigation\07590920.05n"

obs_data = gr.load(rinex_file_o)
nav_data = gr.load(rinex_file_n)

# Örnek olarak ilk gözlem epochunu alalım
epoch_time = obs_data.time.values[0]

# Gözlem verilerini çekelim
obs_epoch = obs_data.sel(time=epoch_time)

# Pseudorange ve Carrier Phase ölçümleri
P1 = obs_epoch['C1'].values  # Pseudorange (m)
L1 = obs_epoch['L1'].values  # Carrier Phase (cycle)
Phi1 = L1 * lambda_L1  # Carrier Phase (m)

# Navigasyon verilerinden uydu saat hatalarını hesaplama
def satellite_clock_correction(nav_data, prn, epoch_time):
    # Uydu saat hatası hesaplama
    sv_clock_bias = nav_data.sel(sv=prn)['SVclockBias'].values
    sv_clock_drift = nav_data.sel(sv=prn)['SVclockDrift'].values
    sv_clock_drift_rate = nav_data.sel(sv=prn)['SVclockDriftRate'].values

    trans_time = nav_data.sel(sv=prn)['TransTime'].values
    
    # trans_time'ı kontrol edip datetime64 formatına dönüştürme
    if isinstance(trans_time, (np.datetime64, np.ndarray)):
        trans_time_sec = trans_time.astype('datetime64[s]').astype(float)
    else:
        # trans_time'ı datetime64 formatına dönüştürme
        trans_time_sec = np.datetime64(trans_time, 's').astype(float)

    # epoch_time'ı saniyeye dönüştürme
    epoch_time_sec = np.datetime64(epoch_time, 's').astype(float)

    # Zaman farkını hesaplama
    t = epoch_time_sec - trans_time_sec
    
    dt = sv_clock_bias + sv_clock_drift * t + sv_clock_drift_rate * t**2
    
    return dt

# Örnek PRN (uydu numarası)
prn = obs_epoch.sv.values[0]

# Uydu saat hatasını hesapla
dT_s = satellite_clock_correction(nav_data, prn, epoch_time)

# Alıcı saat hatası (örnek olarak sıfır alındı, gerçek uygulamalarda bu hesaplanmalıdır)
dT = 0

# Gerçek mesafeyi hesaplama (basitleştirilmiş, burada sadece pseudorange kullanılmıştır)
rho = P1 - c * (dT - dT_s)

# İyonosferik ve troposferik hatalar (basitleştirilmiş, burada sıfır alınmıştır)
I = 0  # İyonosferik hata (örnek değeri)
T = 0  # Troposferik hata (örnek değeri)
epsilon_p = 0  # Diğer hatalar (örnek değeri)
epsilon_phi = 0  # Diğer hatalar (örnek değeri)
N = 0  # Faz kayması (örnek değeri)

# Pseudorange denklemi
P = rho + c * (dT - dT_s) + I + T + epsilon_p

# Carrier Phase denklemi
Phi = rho + c * (dT - dT_s) + N * lambda_L1 + I - T + epsilon_phi

print(f'Pseudorange (P): {P} meters')
print(f'Carrier Phase (Phi): {Phi} meters')
