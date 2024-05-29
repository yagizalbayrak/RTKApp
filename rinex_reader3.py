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
    observation_labels = [
        "satellite", "epoch", "sv_clock_bias", "sv_clock_drift", "sv_clock_drift_rate",
        "IODC", "crs", "delta_n", "M0",
        "cuc", "e", "cus", "sqrtA",
        "toe", "cic", "omega0", "cis",
        "i0", "crc", "omega", "omega_dot",
        "idot", "L2_code", "GPS_week", "L2_P_flag",
        "SV_accuracy", "SV_health", "TGD", "IODC_clock",
        "trans_time"
    ]

    def convert_d_to_e(line):
        return line.replace('D', 'E')

    with open(file_path, 'r') as file:
        header_parsed = False
        data_matrix = []
        current_sv_data = []

        for line in file:
            if not header_parsed:
                if "END OF HEADER" in line:
                    header_parsed = True
                continue

            if line[0] == "G":  # Yeni bir GPS uydu verisi başlat
                if current_sv_data:
                    data_matrix.append(current_sv_data)
                
                current_sv_data = [
                    line[:3].strip(),  # satellite
                    line[4:23].strip(),  # epoch
                    float(convert_d_to_e(line[23:42].strip())),  # sv_clock_bias
                    float(convert_d_to_e(line[42:61].strip())),  # sv_clock_drift
                    float(convert_d_to_e(line[61:80].strip()))  # sv_clock_drift_rate
                ]

            else:  # Sonraki satırlar veri satırlarıdır
                values = list(map(float, re.findall(r'[-+]?\d*\.\d+E[-+]?\d+', convert_d_to_e(line.strip()))))
                current_sv_data.extend(values)

        if current_sv_data:
            data_matrix.append(current_sv_data)

    # Matrisi gözlemler listesine dönüştürme
    for data in data_matrix:
        observation = {}
        for i, label in enumerate(observation_labels):
            observation[label] = data[i]
        observations.append(observation)

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
            for key, value in obs.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")

# Ana fonksiyon
def main(input_path, header_output_path, body_output_path):
    header_data = decode_nav_rinex_header(input_path)
    observations = parse_nav_rinex_body(input_path)

    write_header_to_file(header_data, header_output_path)
    write_observations_to_file(observations, body_output_path)

    print(f"Header information written to {header_output_path}")
    print(f"Observations written to {body_output_path}")


input_path = r"C:\RTKApp\data\navigation\07590920.05n"
header_output_path = r"C:\RTKApp\output\output_header_07590920.txt"
body_output_path = r"C:\RTKApp\output\output_body_07590920.txt"
main(input_path, header_output_path, body_output_path)
