import pandas as pd
import joblib
import mysql.connector
import time
from datetime import datetime

print("Menyiapkan sistem urut waktu (Chronological)...")

# 1. Koneksi ke Database bdiot_smart_lighting
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="", 
    database="bdiot_smart_lighting"
)
cursor = db.cursor()

# 2. Buat tabel otomatis jika belum ada
cursor.execute("""
CREATE TABLE IF NOT EXISTS iot_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    waktu_deteksi DATETIME DEFAULT CURRENT_TIMESTAMP,
    ambient_light_lux INT,
    motion_detected BOOLEAN,
    weather_condition VARCHAR(50),
    keputusan_kecerahan INT
)
""")

# 2.5 Kosongkan isi tabel setiap kali simulator baru dinyalakan
cursor.execute("TRUNCATE TABLE iot_logs")
db.commit()
print("Tabel    database berhasil di-reset!")

# 3. Load Otak AI dan Data Sensor
model = joblib.load('model_cerdas.pkl')
df = pd.read_csv('smart_lighting_dataset_2024.csv')

# Bersihkan data agar AI tidak bingung (tapi timestamp asli tidak dihapus dari df awal)
df_bersih = df.drop(columns=['timestamp', 'zone_id', 'light_intensity_percent'], errors='ignore')
X_simulasi = pd.get_dummies(df_bersih, columns=['day_of_week', 'time_of_day', 'weather_condition'])

print("\n🔌 Simulator IoT Berjalan... Membaca data secara berurutan!")
print("Tekan CTRL + C di terminal untuk mematikan alat.\n")

try:
    # Membaca data berurutan dari baris 0 sampai selesai
    for index in range(len(df)):
        # Ambil data sensor sesuai urutan baris saat ini
        data_sensor = X_simulasi.loc[[index]]
        
        # Ambil data riil untuk disimpan dan ditampilkan
        waktu_sekarang = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lux = int(df.loc[index, 'ambient_light_lux'])
        motion = int(df.loc[index, 'motion_detected'])
        weather = str(df.loc[index, 'weather_condition'])

        # AI memprediksi kecerahan lampu
        prediksi = model.predict(data_sensor)[0]
        keputusan = int(prediksi)

        # Menyimpan hasil ke MySQL
        sql = "INSERT INTO iot_logs (waktu_deteksi, ambient_light_lux, motion_detected, weather_condition, keputusan_kecerahan) VALUES (%s, %s, %s, %s, %s)"
        val = (waktu_sekarang, lux, motion, weather, keputusan)
        cursor.execute(sql, val)
        db.commit()

        # Tampilkan di layar beserta Timestamp asli dari dataset
        print(f"[{waktu_sekarang}] Terkirim! Cuaca: {weather:<7} | Cahaya: {lux:<4} lux | Gerak: {motion} --> 💡 Lampu: {keputusan}%")
        
        # Jeda 2 detik agar tidak terlalu cepat
        time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Simulator IoT dimatikan oleh Yang Mulia.")
    db.close()