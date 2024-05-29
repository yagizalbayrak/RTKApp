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
        while True:
            line = file.readline()
            if not line:
                break

            if not header_parsed:
                if "END OF HEADER" in line:
                    header_parsed = True
                continue

            if line[0] == 'G':  # Yeni bir GPS uydu verisi başlat
                current_observation = {}

                # İlk satırdaki veriler
                current_observation["satellite"] = line[1:4].strip()
                current_observation["epoch"] = line[4:23].strip()
                current_observation["sv_clock_bias"] = float(convert_d_to_e(line[23:42].strip()))
                current_observation["sv_clock_drift"] = float(convert_d_to_e(line[42:61].strip()))
                current_observation["sv_clock_drift_rate"] = float(convert_d_to_e(line[61:80].strip()))

                # Devam eden satırlar
                line = file.readline()
                current_observation["IODC"] = line[4:23].strip()
                current_observation["crs"] = float(convert_d_to_e(line[23:42].strip()))
                current_observation["delta_n"] = float(convert_d_to_e(line[42:61].strip()))
                current_observation["M0"] = float(convert_d_to_e(line[61:80].strip()))

                line = file.readline()
                current_observation["cuc"] = float(convert_d_to_e(line[4:23].strip()))
                current_observation["e"] = float(convert_d_to_e(line[23:42].strip()))
                current_observation["cus"] = float(convert_d_to_e(line[42:61].strip()))
                current_observation["sqrtA"] = float(convert_d_to_e(line[61:80].strip()))

                line = file.readline()
                current_observation["toe"] = float(convert_d_to_e(line[4:23].strip()))
                current_observation["cic"] = float(convert_d_to_e(line[23:42].strip()))
                current_observation["omega0"] = float(convert_d_to_e(line[42:61].strip()))
                current_observation["cis"] = float(convert_d_to_e(line[61:80].strip()))

                line = file.readline()
                current_observation["i0"] = float(convert_d_to_e(line[4:23].strip()))
                current_observation["crc"] = float(convert_d_to_e(line[23:42].strip()))
                current_observation["omega"] = float(convert_d_to_e(line[42:61].strip()))
                current_observation["omega_dot"] = float(convert_d_to_e(line[61:80].strip()))

                line = file.readline()
                current_observation["idot"] = float(convert_d_to_e(line[4:23].strip()))
                current_observation["L2_code"] = float(convert_d_to_e(line[23:42].strip()))
                current_observation["GPS_week"] = float(convert_d_to_e(line[42:61].strip()))
                current_observation["L2_P_flag"] = float(convert_d_to_e(line[61:80].strip()))

                line = file.readline()
                current_observation["SV_accuracy"] = float(convert_d_to_e(line[4:23].strip()))
                current_observation["SV_health"] = float(convert_d_to_e(line[23:42].strip()))
                current_observation["TGD"] = float(convert_d_to_e(line[42:61].strip()))
                current_observation["IODC_clock"] = float(convert_d_to_e(line[61:80].strip()))

                line = file.readline()
                current_observation["trans_time"] = float(convert_d_to_e(line[4:23].strip()))

                observations.append(current_observation)
                print(f"Added observation: {current_observation}")

    return observations

def write_observations_to_file(observations, output_path):
    with open(output_path, 'w') as file:
        for obs in observations:
            for key, value in obs.items():
                file.write(f"{key}: {value}\n")
            file.write("\n")


input_path = r"C:\RTKApp\data\navigation\07590920.05n"
header_output_path = r"C:\RTKApp\output\output_header_07590920.txt"
body_output_path = r"C:\RTKApp\output\output_body_07590920.txt"

observations = parse_nav_rinex_body(input_path)
write_observations_to_file(observations, body_output_path)

print(f"Observations written to {body_output_path}")
