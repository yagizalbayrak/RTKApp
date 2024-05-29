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
        current_sv_data = None

        for line in file:
            if not header_parsed:
                if "END OF HEADER" in line:
                    header_parsed = True
                continue

            if line[0] == 'G':  # İlk satır GPS uydusunu temsil eder
                if current_sv_data:
                    observations.append(current_sv_data)
                
                current_sv_data = {
                    "satellite": line[:3].strip(),
                    "epoch": line[4:23].strip(),
                    "sv_clock_bias": float(convert_d_to_e(line[23:42].strip())),
                    "sv_clock_drift": float(convert_d_to_e(line[42:61].strip())),
                    "sv_clock_drift_rate": float(convert_d_to_e(line[61:80].strip())),
                    "IODC": None,
                    "crs": None,
                    "delta_n": None,
                    "M0": None,
                    "cuc": None,
                    "e": None,
                    "cus": None,
                    "sqrtA": None,
                    "toe": None,
                    "cic": None,
                    "omega0": None,
                    "cis": None,
                    "i0": None,
                    "crc": None,
                    "omega": None,
                    "omega_dot": None,
                    "idot": None,
                    "L2_code": None,
                    "GPS_week": None,
                    "L2_P_flag": None,
                    "SV_accuracy": None,
                    "SV_health": None,
                    "TGD": None,
                    "IODC_clock": None,
                    "trans_time": None
                }

            elif current_sv_data is not None:  # Sonraki satırlar veri satırlarıdır
                values = list(map(float, re.findall(r'[-+]?\d*\.\d+E[-+]?\d+', convert_d_to_e(line.strip()))))
                if len(values) == 4:
                    if current_sv_data["IODC"] is None:
                        current_sv_data["IODC"] = values[0]
                        current_sv_data["crs"] = values[1]
                        current_sv_data["delta_n"] = values[2]
                        current_sv_data["M0"] = values[3]
                    elif current_sv_data["cuc"] is None:
                        current_sv_data["cuc"] = values[0]
                        current_sv_data["e"] = values[1]
                        current_sv_data["cus"] = values[2]
                        current_sv_data["sqrtA"] = values[3]
                    elif current_sv_data["toe"] is None:
                        current_sv_data["toe"] = values[0]
                        current_sv_data["cic"] = values[1]
                        current_sv_data["omega0"] = values[2]
                        current_sv_data["cis"] = values[3]
                    elif current_sv_data["i0"] is None:
                        current_sv_data["i0"] = values[0]
                        current_sv_data["crc"] = values[1]
                        current_sv_data["omega"] = values[2]
                        current_sv_data["omega_dot"] = values[3]
                    elif current_sv_data["idot"] is None:
                        current_sv_data["idot"] = values[0]
                        current_sv_data["L2_code"] = values[1]
                        current_sv_data["GPS_week"] = values[2]
                        current_sv_data["L2_P_flag"] = values[3]
                    elif current_sv_data["SV_accuracy"] is None:
                        current_sv_data["SV_accuracy"] = values[0]
                        current_sv_data["SV_health"] = values[1]
                        current_sv_data["TGD"] = values[2]
                        current_sv_data["IODC_clock"] = values[3]
                    elif current_sv_data["trans_time"] is None:
                        current_sv_data["trans_time"] = values[0]

        if current_sv_data:
            observations.append(current_sv_data)

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
            file.write(f"IODC: {obs['IODC']}\n")
            file.write(f"crs: {obs['crs']}\n")
            file.write(f"delta_n: {obs['delta_n']}\n")
            file.write(f"M0: {obs['M0']}\n")
            file.write(f"cuc: {obs['cuc']}\n")
            file.write(f"e: {obs['e']}\n")
            file.write(f"cus: {obs['cus']}\n")
            file.write(f"sqrtA: {obs['sqrtA']}\n")
            file.write(f"toe: {obs['toe']}\n")
            file.write(f"cic: {obs['cic']}\n")
            file.write(f"omega0: {obs['omega0']}\n")
            file.write(f"cis: {obs['cis']}\n")
            file.write(f"i0: {obs['i0']}\n")
            file.write(f"crc: {obs['crc']}\n")
            file.write(f"omega: {obs['omega']}\n")
            file.write(f"omega_dot: {obs['omega_dot']}\n")
            file.write(f"idot: {obs['idot']}\n")
            file.write(f"L2_code: {obs['L2_code']}\n")
            file.write(f"GPS_week: {obs['GPS_week']}\n")
            file.write(f"L2_P_flag: {obs['L2_P_flag']}\n")
            file.write(f"SV_accuracy: {obs['SV_accuracy']}\n")
            file.write(f"SV_health: {obs['SV_health']}\n")
            file.write(f"TGD: {obs['TGD']}\n")
            file.write(f"IODC_clock: {obs['IODC_clock']}\n")
            file.write(f"trans_time: {obs['trans_time']}\n")
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
