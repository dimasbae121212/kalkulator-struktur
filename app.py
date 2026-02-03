import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math
import base64

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Pro SNI", page_icon="🏗️", layout="wide")

# --- STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .main-header { color: #2c3e50; font-size: 35px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .guide-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #3498db; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI HELPER ---
def hitung_tulangan(luas_target, diameter):
    luas_satu_besi = 0.25 * math.pi * (diameter**2)
    jumlah = math.ceil(luas_target / luas_satu_besi)
    return max(jumlah, 2)

# --- TABS UTAMA ---
tabs = st.tabs(["👋 Panduan Pengguna", "⚙️ Kalkulator Struktur", "📚 Referensi SNI"])

# --- TAB 0: LANDING PAGE (PANDUAN) ---
with tabs[0]:
    st.markdown('<div class="main-header">Selamat Datang di CivilCalc Pro</div>', unsafe_allow_html=True)
    
    col_guide1, col_guide2 = st.columns(2)
    
    with col_guide1:
        st.markdown("""
        <div class="guide-card">
        <h4>🔍 Cara Menggunakan Aplikasi:</h4>
        1. <b>Tentukan Material:</b> Pilih mutu beton (f'c) dan mutu baja (fy) yang tersedia di toko bangunan lokal.<br><br>
        2. <b>Input Dimensi:</b> Masukkan panjang bentang balok (jarak antar kolom) dan jumlah lantai bangunan.<br><br>
        3. <b>Lihat Visualisasi:</b> Periksa sketsa penampang untuk melihat posisi tulangan.<br><br>
        4. <b>Unduh Laporan:</b> Klik tombol PDF untuk mendapatkan resume teknis siap cetak.
        </div>
        """, unsafe_allow_html=True)
        
    with col_guide2:
        st.info("💡 **Tips untuk Pengguna Awam:**")
        st.write("- **Bentang Balok:** Semakin panjang jarak antar kolom, semakin tinggi balok yang dibutuhkan.")
        st.write("- **Mutu Beton:** Untuk rumah tinggal standar, gunakan f'c 20 atau 25 MPa (setara K-250/K-300).")
        st.write("- **Diameter Besi:** Umumnya menggunakan D13 atau D16 untuk tulangan utama balok rumah 2 lantai.")

    st.markdown("---")
    st.subheader("Visualisasi Elemen Struktur")
    
    st.caption("Ilustrasi hubungan Balok, Kolom, dan Plat sesuai standar penulangan beton.")

# --- TAB 1: KALKULATOR ---
with tabs[1]:
    col_input, col_viz = st.columns([1, 1.2])
    
    with col_input:
        st.subheader("🛠️ Input Parameter")
        c1, c2 = st.columns(2)
        with c1:
            fc = st.selectbox("Mutu Beton (f'c) MPa", [20, 25, 30], index=1)
            fy = st.selectbox("Mutu Baja (fy) MPa", [280, 420], index=1)
        with c2:
            L = st.number_input("Bentang Balok (m)", 1.0, 15.0, 5.0)
            lantai = st.number_input("Jumlah Lantai", 1, 10, 2)
        
        st.subheader("🔩 Pilihan Besi")
        diam_balok = st.selectbox("Diameter Besi Balok (mm)", [10, 13, 16, 19], index=2)
        diam_kolom = st.selectbox("Diameter Besi Kolom (mm)", [10, 13, 16, 19], index=2)

    # Logika Perhitungan (Balok)
    h_f = int(((L * 1000) / 16 // 50 + 1) * 50) 
    b_f = int((h_f * 0.5 // 25 + 1) * 25)
    as_min_balok = (math.sqrt(fc) / (4 * fy)) * b_f * (h_f - 40)
    n_besi_balok = hitung_tulangan(as_min_balok, diam_balok)

    # Logika Perhitungan (Kolom)
    pu = lantai * 25 * 12 
    ag_req = (pu * 1000) / (0.35 * fc)
    sisi_k = max(int((ag_req**0.5 // 50 + 1) * 50), 200)
    as_kolom = 0.01 * (sisi_k**2)
    n_besi_kolom = hitung_tulangan(as_kolom, diam_kolom)
    if n_besi_kolom % 2 != 0: n_besi_kolom += 1

    with col_viz:
        st.subheader("📐 Hasil Desain & Sketsa")
        v1, v2 = st.columns(2)
        
        with v1:
            st.write(f"**Balok: {b_f}x{h_f}**")
            fig1, ax1 = plt.subplots(figsize=(1.5, 2))
            ax1.add_patch(patches.Rectangle((0, 0), b_f, h_f, color='#bdc3c7', label='Beton'))
            ax1.scatter([40, b_f-40], [40, 40], color='red', s=30) # Simbol besi
            plt.axis('off')
            st.pyplot(fig1)
            st.caption(f"Tulangan: {n_besi_balok} D{diam_balok}")

        with v2:
            st.write(f"**Kolom: {sisi_k}x{sisi_k}**")
            fig2, ax2 = plt.subplots(figsize=(1.5, 2))
            ax2.add_patch(patches.Rectangle((0, 0), sisi_k, sisi_k, color='#34495e', alpha=0.3))
            ax2.scatter([40, sisi_k-40, 40, sisi_k-40], [40, 40, sisi_k-40, sisi_k-40], color='red', s=30)
            plt.axis('off')
            st.pyplot(fig2)
            st.caption(f"Tulangan: {n_besi_kolom} D{diam_kolom}")

    # --- PDF GENERATOR ---
    st.divider()
    if st.button("🚀 Siapkan Laporan PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_fill_color(44, 62, 80)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 20, "LAPORAN DESAIN STRUKTUR", ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(25)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "1. DATA MATERIAL", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"- Mutu Beton (f'c): {fc} MPa / Mutu Baja (fy): {fy} MPa", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "2. DETAIL ELEMEN", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f"- Balok: {b_f}x{h_f} mm | Tulangan: {n_besi_balok} D{diam_balok}", ln=True)
        pdf.cell(0, 8, f"- Kolom: {sisi_k}x{sisi_k} mm | Tulangan: {n_besi_kolom} D{diam_kolom}", ln=True)
        
        pdf_out = pdf.output(dest="S").encode("latin-1")
        st.download_button("📥 Unduh Laporan Sekarang", data=pdf_out, file_name="Laporan_SNI.pdf", mime="application/pdf")

# --- TAB 2: REFERENSI ---
with tabs[2]:
    st.write("### Daftar Standar Referensi")
    st.markdown("""
    - **SNI 2847:2019**: Persyaratan Beton Struktural untuk Bangunan Gedung.
    - **SNI 1727:2020**: Beban Desain Minimum untuk Bangunan Gedung.
    - **SNI 2052:2017**: Baja Tulangan Beton (Syarat mutu dan diameter).
    - **Faktor Reduksi ($\phi$):** Lentur (0.9), Geser (0.75), Tekan (0.65).
    """)
