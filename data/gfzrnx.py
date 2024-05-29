import subprocess

def read_rinex_file(input_file):
    try:
        # GFZRNX komutunu çalıştır
        result = subprocess.run([r"C:\RTKApp\data\gfzrnx_2.1.9_win11_64.exe", '-finp', input_file, '-show'], capture_output=True, text=True)
        
        # Çıktıyı al ve işleyin
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"An error occurred: {e}")

# RINEX dosyasını okuma örneği
input_file = r"C:\RTKApp\data\observation\base123i.24o"
read_rinex_file(input_file)
