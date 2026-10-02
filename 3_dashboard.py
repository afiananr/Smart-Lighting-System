import streamlit as st
import pandas as pd
import mysql.connector
import time

# 1. Konfigurasi Halaman Dashboard
st.set_page_config(page_title="Smart City Lighting Dashboard", layout="wide")
st.title("🏙️ Smart Street Lighting Dashboard")

# 2. Fungsi untuk mengambil data dari MySQL
def get_data():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="bdiot_smart_lighting"
    )
    cursor = db.cursor(dictionary=True)
    # Ambil 50 data terakhir yang masuk
    cursor.execute("SELECT * FROM iot_logs ORDER BY waktu_deteksi DESC LIMIT 50")
    result = cursor.fetchall()
    db.close()
    
    return pd.DataFrame(result)

# 3. Area untuk merender ulang dashboard secara real-time
placeholder = st.empty()

print("Dashboard berjalan! Buka link Local URL di browser.")

while True:
    df = get_data()
    
    with placeholder.container():
        if not df.empty:
            # Ambil data baris pertama (paling baru)
            data_terbaru = df.iloc[0]
            
            # --- BAGIAN A: TEKS KEPUTUSAN AI & REKOMENDASI TINDAKAN ---
            st.subheader("🤖 Analisis & Rekomendasi Sistem")
            
            cuaca = data_terbaru['weather_condition']
            gerak = "Ada" if data_terbaru['motion_detected'] == 1 else "Tidak Ada"
            cahaya = data_terbaru['ambient_light_lux']
            lampu = data_terbaru['keputusan_kecerahan']
            waktu = data_terbaru['waktu_deteksi']
            
            # 1. Logika Keputusan Dasar
            if lampu == 100:
                st.error(f"🚨 **[{waktu}] VISIBILITAS MAKSIMAL:** AI memaksimalkan lampu di angka **100%**.")
            elif lampu == 30:
                st.success(f"🍃 **[{waktu}] MODE HEMAT ENERGI:** AI menurunkan kecerahan lampu menjadi **30%**.")
            else:
                st.info(f"☀️ **[{waktu}] SIANG HARI:** AI mematikan lampu (**0%**).")

            # 2. LOGIKA REKOMENDASI (Sistem Pakar)
            rekomendasi = []
            
            # Kasus 1: Anomali Sensor (Siang hari tapi lampu nyala)
            if cahaya > 800 and lampu > 0:
                rekomendasi.append("⚠️ **Peringatan Anomali:** Cahaya lingkungan terang tapi lampu tetap menyala. **Rekomendasi:** Teknisi harap segera mengecek kemungkinan kerusakan atau kotoran pada sensor LDR di tiang.")
                
            # Kasus 2: Cuaca Buruk
            if cuaca in ['Rain', 'Storm']:
                rekomendasi.append(f"🌧️ **Tindakan Preventif ({cuaca}):** Terdeteksi curah hujan tinggi. **Rekomendasi:** Jadwalkan pembersihan panel surya dari sisa lumpur/daun besok pagi agar pengisian baterai optimal.")
                
            # Kasus 3: Keamanan Ekstra
            if cuaca == 'Foggy' and data_terbaru['motion_detected'] == 1:
                rekomendasi.append("🌫️ **Keamanan Lalu Lintas:** Jarak pandang rendah karena kabut dan ada aktivitas warga. **Rekomendasi:** Aktifkan peringatan rambu lalu lintas berkedip di area ini.")
            
            # Menampilkan kotak rekomendasi jika ada masalah
            if rekomendasi:
                st.markdown("### 💡 Rekomendasi Tindakan Operasional:")
                for rek in rekomendasi:
                    st.warning(rek)
            else:
                st.markdown("### 💡 Rekomendasi Tindakan Operasional:")
                st.success("✅ Sistem berjalan normal. Tidak ada tindakan pemeliharaan yang diperlukan saat ini.")
            
            # --- BAGIAN B: METRIK ANGKA ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Kecerahan Lampu Saat Ini", f"{lampu}%")
            col2.metric("Sensor Cahaya (Lux)", f"{cahaya} lux")
            col3.metric("Status Gerakan", f"{gerak} Gerakan")
            
            st.markdown("---")
            
            # --- BAGIAN C: GRAFIK & TABEL ---
            col_grafik, col_tabel = st.columns([2, 1])
            
            with col_grafik:
                st.subheader("📈 Tren Penggunaan Energi")
                # Balik urutan data agar grafik berjalan dari kiri ke kanan
                df_grafik = df.sort_values(by='waktu_deteksi')
                st.line_chart(data=df_grafik, x='waktu_deteksi', y='keputusan_kecerahan')
                
            with col_tabel:
                st.subheader("📋 Riwayat Log Sensor")
                st.dataframe(df[['waktu_deteksi', 'weather_condition', 'keputusan_kecerahan']], height=350)
                
        else:
            st.warning("⏳ Menunggu data masuk dari Simulator IoT...")
            
    # Jeda 3 detik sebelum refresh halaman
    time.sleep(3)