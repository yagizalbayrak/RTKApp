import georinex as gr
import numpy as np
import os

def load_rinex_obs_nav(obs_path, nav_path):
    # RINEX OBS ve NAV dosyalarını yükler
    obs_data = gr.load(obs_path)
    nav_data = gr.load(nav_path)
    return obs_data, nav_data

def rtk_correction(obs_data, nav_data, reference_position):
    # Bu fonksiyon, RTKLIB veya benzeri bir kütüphane kullanılarak doldurulmalıdır.
    # Burada basitçe ölçümlerden pozisyon hesaplaması ve referans pozisyon ile karşılaştırma simüle edilmektedir.
    # Örnek bir hesaplama yapıyoruz:
    estimated_positions = np.random.normal(loc=reference_position, scale=0.1, size=(len(obs_data.time), 3))
    errors = estimated_positions - reference_position
    return errors

def write_errors_to_file(errors, file_path):
    # Hata vektörlerini belirtilen dosya yoluna yaz
    with open(file_path, 'a') as file:
        for error in errors:
            file.write(f"{error}\n")
        file.write("\n")  # Her çalışma arasında boş bir satır ekleyerek ayır

def main():
    obs_path = r"C:\RTKApp\data\observation\abpo0010.24o"  # Örnek OBS dosya yolu
    nav_path = r"C:\RTKApp\data\navigation\ABPO00MDG_R_20240010000_01D_GN.rnx"  # Örnek NAV dosya yolu
    reference_position = np.array([4097216.5539, 4429119.1897, -2065771.1988])  # Örnek referans konumu

    corrections_folder = r"C:\RTKApp\corrections"
    if not os.path.exists(corrections_folder):
        os.makedirs(corrections_folder)

    corrections_file_path = os.path.join(corrections_folder, "corrections.txt")

    obs_data, nav_data = load_rinex_obs_nav(obs_path, nav_path)
    errors = rtk_correction(obs_data, nav_data, reference_position)
    
    write_errors_to_file(errors, corrections_file_path)
    
    print("Hata vektörleri başarıyla kaydedildi.")

if __name__ == '__main__':
    main()
