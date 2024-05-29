import os

# Dosya yollarını belirtin
original_file_path = r"C:\RTKApp\data\ANKR00TUR_R_20190010000_01D_30S_MO_edited.txt"
new_file_path = original_file_path.replace('.txt', '.rnx')

# Dosya adını değiştir
os.rename(original_file_path, new_file_path)
