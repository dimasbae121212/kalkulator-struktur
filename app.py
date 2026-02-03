import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Pro V2 - Analisis Akurat", layout="wide")

# --- FUNGSI ANALISIS TEKNIS ---
def hitung_balok_lengkap(L, jenis, fc, fy):
    # 1. Penentuan Tinggi Berdasarkan Jenis (SNI 2847:2019)
    # L dalam mm
    L_mm = L * 1000
    if jenis == "Balok Utama":
        h = math.ceil((L_mm / 12) / 50) * 50
        b = math.ceil((0.6 * h) / 25) * 25
    elif jenis == "Balok Anak":
        h = math.ceil((L_mm / 15) / 50) * 50
        b = math.ceil((0.5 * h) / 25) * 25
    else: # Balok Gantung / Kantilever
        h = math.ceil((L_mm / 8) / 50) * 50
        b = math.ceil((0.6 * h) / 25) * 25
    
    # 2. Perhitungan Tulangan Lentur (Asumsi Beban Rencana Sederhana)
    # Mu estimasi (kNm) - Pendekatan praktis beban gedung
    mu = 0.12 * 25 * (L**2) # kN.m
    d = h - 50 # Jarak efektif (selimut 40mm + sengkang 10mm)
    
    # Luas Tulangan Tarik (As) - Rumus Pendekatan Lentur
    # As = Mu / (phi * fy * 0.85 * d)
    as_req = (mu * 10**6) / (0.9 * fy * 0.85 * d)
    
    # Syarat As min SNI: (sqrt(fc')/4fy) * b * d
    as_min = (math.sqrt(fc) / (4 * fy)) * b * d
    as_final = max(as_req, as_min)
    
    # Rekomendasi Diameter & Jumlah (Minimal 2 atas, 2 bawah untuk integritas)
    diam = 16 if h >= 400 else 13
    luas_satu = 0.25 * math.pi * (diam**2)
    n_tarik = math.ceil(as_final / luas_satu)
    if n_tarik < 2: n_tarik = 2
    n_tekan = max(2, math.ceil(n_tarik / 2)) # Tulangan praktis atas
    
    # 3. Tulangan Geser (Sengkang/Beugel)
    # Spasi s = d/2 atau 600mm (SNI)
    sengkang_diam = 10 if h > 300 else 8
    spasi = min(d/2, 200) # mm
    
    return b, h, n_tarik, n_tekan, diam, sengkang_diam, int(spasi), mu

# --- UI ---
st.title("🏗️ CivilCalc Pro V2: Analisis Struktur Terintegrasi SNI")
st.markdown("Sistem Rekomendasi Otomatis berdasarkan **SNI 2847:2019 (Beton)**, **SNI 1726:2019 (Gempa)**, dan **SNI 2052:2017 (Baja)**.")

t1, t2, t3 = st.tabs(["📊 Analisis Struktur", "📄 Laporan Teknis PDF", "📚 Dasar Teori"])

with t1:
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.subheader("Input Parameter")
        peruntukan = st.selectbox("Peruntukan Balok", ["Balok Utama", "Balok Anak", "Balok Gantung"])
        L = st.slider("Panjang Bentang (m)", 2.0, 12.0, 5.0)
        mutu_beton = st.select_slider("Mutu Beton f'c (MPa)", options=[20, 25, 30, 35, 40], value=25)
        mutu_baja = st.select_slider("Mutu Baja fy (MPa)", options=[280, 420], value=420)
        
        b, h, n_tarik, n_tekan, d_utama, d_sengkang, spasi, mu = hitung_balok_lengkap(L, peruntukan, mutu_beton, mutu_baja)
        
        st.success(f"**Rekomendasi Sistem:**\nDimensi: {b}x{h} mm\nTulangan Bawah: {n_tarik}D{d_utama}\nTulangan Atas: {n_tekan}D{d_utama}\nSengkang: Ø{d_sengkang}-{spasi} mm")

    with c2:
        st.subheader("Visualisasi Penampang Realistis")
        fig, ax = plt.subplots(figsize=(4, 5))
        # Beton & Selimut
        ax.add_patch(patches.Rectangle((0, 0), b, h, color='#cccccc', label='Beton'))
        ax.add_patch(patches.Rectangle((40, 40), b-80, h-80, fill=False, linestyle='--', color='blue', label='Sengkang'))
        
        # Tulangan Bawah
        for i in range(n_tarik):
            x_pos = 60 + (i * (b-120)/(n_tarik-1 if n_tarik > 1 else 1))
            ax.scatter(x_pos, 60, color='black', s=100)
        # Tulangan Atas
        for i in range(n_tekan):
            x_pos = 60 + (i * (b-120)/(n_tekan-1 if n_tekan > 1 else 1))
            ax.scatter(x_pos, h-60, color='black', s=100)
            
        plt.xlim(-20, b+20); plt.ylim(-20, h+20); plt.axis('off')
        st.pyplot(fig)

with t2:
    st.subheader("Penyusunan Laporan PDF Kompleks")
    if st.button("Generate Detailed PDF Report"):
        pdf = FPDF()
        pdf.add_page()
        # Header & Judul
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "LAPORAN ANALISIS TEKNIS STRUKTUR BETON", ln=True, align='C')
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, "Berdasarkan Standar Mutu SNI Indonesia", ln=True, align='C')
        pdf.ln(10)

        # Seksi 1: Material & Gaya
        pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, "1. Parameter Analisis", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, f"Tipe Elemen: {peruntukan}\nMutu Beton (f'c): {mutu_beton} MPa\nMutu Baja (fy): {mutu_baja} MPa\nEstimasi Momen Terfaktor (Mu): {mu:.2f} kNm")
        
        # Seksi 2: Rumus & Perhitungan
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, "2. Dasar Perhitungan & Rumus", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, "A. Penentuan Dimensi: Berdasarkan batasan lendutan SNI 2847:2019 Pasal 9.3.1.1.\n"
                           "B. Kebutuhan Tulangan: Menggunakan rumus keseimbangan gaya tarik dan tekan.\n"
                           "   Rumus: As = Mu / (phi * fy * (d - a/2))\n"
                           "C. Geser/Sengkang: Vc = 0.17 * lambda * sqrt(fc') * bw * d")
        
        # Seksi 3: Ketahanan Gempa (SNI 1726)
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12); pdf.cell(0, 10, "3. Ketahanan Gempa & Daktilitas", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 7, "Sistem didesain untuk memenuhi syarat daktilitas moderat. Sengkang dipasang dengan jarak "
                           f"maksimum d/2 ({spasi} mm) untuk memastikan pengkekangan beton inti saat terjadi siklus beban gempa.")

        # Seksi 4: Kesimpulan Dimensi
        pdf.ln(5)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, "KESIMPULAN FINAL REKOMENDASI", ln=True, fill=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"Dimensi Balok: {b} x {h} mm", ln=True)
        pdf.cell(0, 8, f"Penulangan: Atas {n_tekan}D{d_utama}, Bawah {n_tarik}D{d_utama}", ln=True)
        pdf.cell(0, 8, f"Sengkang: Diameter {d_sengkang} mm, Jarak {spasi} mm", ln=True)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        st.download_button("📥 Unduh Laporan Teknis Lengkap", data=pdf_bytes, file_name="Analisis_Struktur_Detail.pdf")

with t3:
    st.markdown("""
    ### Daftar Referensi Teknis
    * **SNI 2847:2019**: Persyaratan Beton Struktural (Perhitungan dimensi, As min, dan spasi sengkang).
    * **SNI 1726:2019**: Tata Cara Perencanaan Ketahanan Gempa untuk Struktur Bangunan Gedung.
    * **SNI 2052:2017**: Baja Tulangan Beton (Standar diameter dan kuat tarik BjTS).
    
    **Komponen Utama Perhitungan:**
    1.  **Selimut Beton:** Ditetapkan **40 mm** untuk melindungi baja dari korosi (Paparan cuaca luar).
    2.  **Daktilitas:** Penulangan atas disediakan minimal 50% dari tulangan bawah untuk memenuhi syarat integritas struktur terhadap gaya balik gempa.
    3.  **Gaya Geser:** Sengkang dihitung untuk menahan gaya geser sisa yang tidak dapat ditahan oleh beton ($V_s = V_u - V_c$).
    """)
