"""
import georinex as gr

def list_obs_types(rinex_path):
    # RINEX dosyasını yükle
    obs = gr.load(rinex_path)
    
    # Mevcut gözlem türlerini listele
    print("Available observation types:", obs.data_vars)
     

rinex_path = r"C:\RTKApp\data\ANKR00TUR_R_20190010000_01D_30S_MO_edited.rnx"
list_obs_types(rinex_path)

"""   


from flask import Flask, render_template
import georinex as gr
import numpy as np

app = Flask(__name__)

def load_rinex_data(rinex_path):
    obs = gr.load(rinex_path)
    L1C_data = obs['L1C'].dropna(dim='time', how='all')
    return L1C_data

def analyze_data(L1C_data):
    mean_values = L1C_data.mean(dim='time')
    std_deviation = L1C_data.std(dim='time')
    return mean_values.values, std_deviation.values

@app.route('/')
def index():
    rinex_path = r"C:\RTKApp\data\ANKR00TUR_R_20190010000_01D_30S_MO_edited.rnx"
    L1C_data = load_rinex_data(rinex_path)
    mean_values, std_deviation = analyze_data(L1C_data)
    return render_template('index.html', mean_values=mean_values, std_deviation=std_deviation)

if __name__ == '__main__':
    app.run(debug=True)

