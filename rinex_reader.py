import re

# NAV RINEX başlığını ayrıştıran fonksiyon
def decode_nav_rinex_header(file_path):
    header_data = {
        "version": None,
        "type": None,
        "run_by_date": None,
        "ion_alpha": None,
        "ion_beta": None,
        "delta_utc": None,
        "leap_seconds": None,
    }

    def convert_d_to_e(line):
        return line.replace('D', 'E')

    with open(file_path, 'r') as file:
        for line in file:
            label = line[60:].strip()

            if "RINEX VERSION / TYPE" in label:
                header_data["version"] = line[:9].strip()
                header_data["type"] = line[20:40].strip()
            elif "PGM / RUN BY / DATE" in label:
                header_data["run_by_date"] = line[:60].strip()
            elif "ION ALPHA" in label:
                header_data["ion_alpha"] = list(map(float, re.findall(r'[-+]?\d*\.\d+E[-+]?\d+', convert_d_to_e(line[:60]))))
            elif "ION BETA" in label:
                header_data["ion_beta"] = list(map(float, re.findall(r'[-+]?\d*\.\d+E[-+]?\d+', convert_d_to_e(line[:60]))))
            elif "DELTA-UTC: A0,A1,T,W" in label:
                header_data["delta_utc"] = list(map(float, re.findall(r'[-+]?\d*\.\d+E[-+]?\d+', convert_d_to_e(line[:60]))))
            elif "LEAP SECONDS" in label:
                header_data["leap_seconds"] = int(line[:6].strip())
            elif "END OF HEADER" in label:
                break

    return header_data

# NAV RINEX body kısmını ayrıştıran fonksiyon
def parse_nav_rinex_body(file_path):
    observations = []

    def convert_d_to_e(line):
        return line.replace('D', 'E')

    with open(file_path, 'r') as file:
        header_parsed = False
        for line in file:
            if not header_parsed:
                if "END OF HEADER" in line:
                    header_parsed = True
                continue

            if line[0] == 'G':  # İlk satır GPS uydusunu temsil eder
                sv_data = {
                    "satellite": line[:3].strip(),
                    "epoch": line[4:23].strip(),
                    "sv_clock_bias": float(convert_d_to_e(line[23:42].strip())),
                    "sv_clock_drift": float(convert_d_to_e(line[42:61].strip())),
                    "sv_clock_drift_rate": float(convert_d_to_e(line[61:80].strip())),
                    "broadcast_orbit": []
                }
                observations.append(sv_data)
            else:  # Sonraki satırlar veri satırlarıdır
                current_data = re.findall(r'[-+]?\d*\.\d+E[-+]?\d+', convert_d_to_e(line.strip()))
                if observations:
                    observations[-1]["broadcast_orbit"].extend(current_data)

    return observations

# Başlık verilerini dosyaya yazan fonksiyon
def write_header_to_file(header_data, output_path):
    with open(output_path, 'w') as file:
        for key, value in header_data.items():
            file.write(f"{key}: {value}\n")

# Gözlem verilerini dosyaya yazan fonksiyon
def write_observations_to_file(observations, output_path):
    with open(output_path, 'w') as file:
        for obs in observations:
            file.write(f"Satellite: {obs['satellite']}\n")
            file.write(f"Epoch: {obs['epoch']}\n")
            file.write(f"SV Clock Bias: {obs['sv_clock_bias']}\n")
            file.write(f"SV Clock Drift: {obs['sv_clock_drift']}\n")
            file.write(f"SV Clock Drift Rate: {obs['sv_clock_drift_rate']}\n")
            file.write("Broadcast Orbit:\n")
            broadcast_orbit_data = obs['broadcast_orbit']
            broadcast_orbit_labels = [
                "IODC", "crs", "Δn", "M0",
                "cuc", "e", "cus", "sqrtA",
                "toe", "cic", "Ω0", "cis",
                "i0", "crc", "ω", "Ω_dot",
                "idot", "L2_code", "GPS_week", "L2_P_flag",
                "SV_accuracy", "SV_health", "TGD", "IODC_clock",
                "trans_time"
                # Burada diğer broadcast orbit verilerini ekleyebilirsiniz.
            ]
            for i, data in enumerate(broadcast_orbit_data):
                if i < len(broadcast_orbit_labels):
                    label = broadcast_orbit_labels[i]
                else:
                    label = f"Additional Data {i + 1 - len(broadcast_orbit_labels)}"
                file.write(f"  {label}: {data}\n")
            file.write("\n")

# Ana fonksiyon
def main(input_path, header_output_path, body_output_path):
    header_data = decode_nav_rinex_header(input_path)
    observations = parse_nav_rinex_body(input_path)

    write_header_to_file(header_data, header_output_path)
    write_observations_to_file(observations, body_output_path)

    print(f"Header information written to {header_output_path}")
    print(f"Observations written to {body_output_path}")

# Örnek kullanım
input_path = r"C:\RTKApp\data\navigation\07590920.05n"
header_output_path = r"C:\RTKApp\output\output_header_07590920.txt"
body_output_path = r"C:\RTKApp\output\output_body_07590920.txt"
main(input_path, header_output_path, body_output_path)
