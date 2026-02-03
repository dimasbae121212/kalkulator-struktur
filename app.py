import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Pro V2", layout="wide")

# --- 2. LOGIKA TEKNIK (Sistem Rekomendasi) ---
def hitung_struktur_ekonomis(L, jenis, fc, fy_jenis, mati, hidup, jml_lantai):
    # Penentuan Fy berdasarkan jenis besi (SNI 2052:2017)
    fy = 280 if fy_jenis == "Besi Polos (BjTP)" else 420
    
    # Tinggi Balok berdasarkan peruntukan (SNI 2847:2019)
    # Balok Utama (L/12), Balok Anak (L/15), Ring Balok (L/18), Sloof (L/12)
    mult = {"Balok Utama": 12, "Balok Anak": 15, "Ring Balok": 18, "Sloof": 12}
    h = int(((L * 1000) / mult[jenis] // 50 + 1) * 50)
    b = int((h * 0.6 // 25 + 1) * 25)
    
    # Analisis Beban Terfaktor (SNI 1727:2020)
    # Perhitungan beban kumulatif berdasarkan jumlah lantai
    qu = ((1.2 * mati) + (1.6 * hidup)) * jml_lantai
    mu = (1/8) * qu * (L**2)
    
    # Penulangan Lentur (Akurasi Tinggi & Ekonomis)
    d = h - 40 - 10 - 8 # Jarak efektif (Selimut 40, Sengkang 10, Tul Utama)
    phi = 0.9
    
    if mu > 0:
        rn = (mu * 10**6) / (phi * b * d**2)
        m = fy / (0.85 * fc)
        # Perbaikan baris eror: Menggunakan max() bukan math.max()
        check_val = 1 - (2 * m * rn / fy)
        rho = (1/m) * (1 - math.sqrt(max(0, check_val)))
        
        rho_min = 1.4 / fy
        rho_final = max(rho, rho_min)
    else:
        rho_final = 1.4 / fy
        
    as_perlu = rho_final * b * d
    # Rekomendasi diameter otomatis
    d_utama = 12 if fy_jenis == "Besi Polos (BjTP)" else 13
    if L > 4.5: d_utama = 16 # Naikkan diameter untuk bentang besar
    
    n_bawah = max(2, math.ceil(as_perlu / (0.25 * math.pi * d_utama**2)))
    n_atas = 2 # Tulangan praktis minimal
    
    # Sengkang (Kelipatan 50mm - Standar Lapangan)
    s_praktis = int((d / 2 // 50) * 50)
    s_final = max(100, min(s_praktis, 200)) # Batas antara 100mm - 200mm
        
    return b, h, n_atas, n_bawah, d_utama, s_final, mu, qu

# --- 3. ANTARMUKA PENGGUNA (INPUT ANGKA) ---
st.title("🏗️ CivilCalc Pro: Kalkulator Struktur Akurat")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        peruntukan = st.selectbox("Peruntukan Struktur", ["Balok Utama", "Balok Anak", "Ring Balok", "Sloof"])
        L_in = st.number_input("Panjang Bentang (m)", value=4.0, step=0.5)
        n_lantai = st.number_input("Jumlah Lantai", value=1, min_value=1)
    with c2:
        tipe_besi = st.radio("Jenis Tulangan (SNI 2052)", ["Besi Polos (BjTP)", "Besi Ulir (BjTS)"])
        fc_in = st.number_input("Mutu Beton f'c (MPa)", value=20)
        selimut_in = st.number_input("Selimut Beton (mm)", value=30)
    with c3:
        dead = st.number_input("Beban Mati D (kN/m)", value=10.0)
        live = st.number_input("Beban Hidup L (kN/m)", value=5.0)

# Menghitung hasil
b, h, n_up, n_dw, d_u, s_s, mu_v, qu_v = hitung_struktur_ekonomis(L_in, peruntukan, fc_in, tipe_besi, dead, live, n_lantai)

st.divider()

# --- 4. OUTPUT HASIL & VISUALISASI ---
res_col, viz_col = st.columns([3, 1])

with res_col:
    st.subheader("📋 Detail Rekomendasi")
    o1, o2 = st.columns(2)
    with o1:
        st.write(f"**Dimensi Beton:** {b} x {h} mm")
        st.write(f"**Beban Terfaktor (Qu):** {qu_v:.2f} kN/m")
        st.write(f"**Momen Maksimum (Mu):** {mu_v:.2f} kNm")
    with o2:
        st.success(f"**Tulangan Tarik (Bawah):** {n_dw} D{d_u}")
        st.success(f"**Tulangan Tekan (Atas):** {n_up} D{d_u}")
        st.warning(f"**Sengkang (Beugel):** ø8 - {s_s} mm")

with viz_col:
    # Visualisasi sangat kecil dan proporsional
    st.write("**Sketsa Penampang**")
    fig, ax = plt.subplots(figsize=(1.0, 1.2)) # Sangat Kecil
    ax.add_patch(patches.Rectangle((0, 0), b, h, color='#f2f2f2', ec='black', lw=1))
    # Sengkang garis putus-putus
    ax.add_patch(patches.Rectangle((selimut_in, selimut_in), b-(2*selimut_in), h-(2*selimut_in), fill=False, ls=':', lw=0.6))
    # Posisi Tulangan
    ax.scatter([selimut_in+5, b-selimut_in-5], [selimut_in+5, selimut_in+5], c='red', s=10)
    ax.scatter([selimut_in+5, b-selimut_in-5], [h-selimut_in-5, h-selimut_in-5], c='blue', s=8)
    plt.axis('off')
    st.pyplot(fig)

# --- 5. GENERATE PDF LAPORAN ---
def make_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "LAPORAN ANALISIS STRUKTUR BETON BERTULANG", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, f"DATA INPUT - PERUNTUKAN: {peruntukan.upper()}", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"- Bentang Struktur: {L_in} m | Jumlah Lantai: {n_lantai}", ln=True)
    pdf.cell(0, 6, f"- Mutu Beton (fc'): {fc_in} MPa | Jenis Baja: {tipe_besi}", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "HASIL PERHITUNGAN & ANALISA GAYA:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"1. Beban Terfaktor (Qu = 1.2D + 1.6L): {qu_v:.2f} kN/m", ln=True)
    pdf.cell(0, 6, f"2. Momen Maksimum (Mu = 1/8 * Qu * L^2): {mu_v:.2f} kNm", ln=True)
    pdf.cell(0, 6, f"3. Dimensi Penampang: {b} mm x {h} mm", ln=True)
    pdf.cell(0, 6, f"4. Rekomendasi Tulangan Utama: Atas {n_up}D{d_u}, Bawah {n_dw}D{d_u}", ln=True)
    pdf.cell(0, 6, f"5. Jarak Sengkang (Beugel): {s_s} mm (Batas SNI & Praktis)", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Catatan Teknis: Perhitungan ini mengacu pada batas layan SNI 2847:2019. Laporan ini merupakan estimasi awal dan bukan dokumen perencanaan final konstruksi.")
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Unduh Laporan PDF", make_pdf(), "Laporan_CivilCalc.pdf", "application/pdf")
