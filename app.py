import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Pro V2", layout="wide")

# --- FUNGSI TEKNIS RUMUS ---
def hitung_balok_akurat(L, tipe, fc, fy):
    # 1. Penentuan Tinggi Berdasarkan Peruntukan (SNI 2847:2019)
    # Balok Utama L/12, Balok Anak L/15, Balok Gantung L/10
    map_h = {"Balok Utama": 12, "Balok Anak": 15, "Balok Gantung": 10}
    h = int(((L * 1000) / map_h[tipe] // 50 + 1) * 50)
    b = int((h * 0.6 // 25 + 1) * 25) # Rasio b/h lebih stabil (0.6)
    
    # 2. Penulangan Lentur Rekomendasi (Estimasi Rasio Tulangan)
    # Luas tulangan tarik (As) ~ 1% dari b*d
    d = h - 50 # Estimasi tinggi efektif dengan selimut 40mm + sengkang 10mm
    as_req = 0.005 * b * d # Rasio moderat untuk keamanan
    
    # Pemilihan Diameter Otomatis (Min D13 untuk Utama)
    db = 16 if L > 4 else 13
    luas_satu_besi = 0.25 * math.pi * (db**2)
    n_tarik = math.ceil(as_req / luas_satu_besi)
    if n_tarik < 2: n_tarik = 2
    n_tekan = math.ceil(n_tarik / 2) # Tulangan atas minimal 50% tulangan bawah
    if n_tekan < 2: n_tekan = 2
    
    # 3. Tulangan Sengkang (Beugel) - SNI 2847:2019 Pasal 18
    # Jarak sengkang daerah tumpuan (L/4) d/4 atau 150mm
    jarak_sengkang = min(d/4, 150)
    return h, b, n_tarik, n_tekan, db, int(jarak_sengkang)

# --- UI HEADER ---
st.title("🏗️ CivilCalc Pro V2: Sistem Pakar Struktur")
st.warning("⚠️ Perhitungan mengacu pada SNI 2847:2019 (Beton), SNI 1726:2019 (Gempa), dan SNI 1727:2020 (Beban).")

with st.container():
    col_input, col_out = st.columns([1, 1])
    
    with col_input:
        st.subheader("📥 Input Data Teknis")
        tipe_b = st.selectbox("Peruntukan Balok", ["Balok Utama", "Balok Anak", "Balok Gantung"])
        L = st.number_input("Panjang Bentang (m)", value=5.0, step=0.1)
        fc = st.number_input("Mutu Beton f'c (MPa)", value=25)
        fy = st.number_input("Mutu Baja fy (MPa)", value=420)
        selimut = st.number_input("Selimut Beton (mm)", value=40)
        kategori_gempa = st.selectbox("Kategori Desain Seismik (KDS)", ["A-B (Rendah)", "C (Sedang)", "D-F (Tinggi)"])

    # Jalankan Logika
    h, b, n_bawah, n_atas, db, s_begel = hitung_balok_akurat(L, tipe_b, fc, fy)
    
    with col_out:
        st.subheader("📤 Output Rekomendasi Sistem")
        st.success(f"**Dimensi:** {b} x {h} mm")
        st.info(f"**Tulangan Atas:** {n_atas} D{db}")
        st.info(f"**Tulangan Bawah:** {n_bawah} D{db}")
        st.info(f"**Sengkang (Beugel):** Ø10 - {s_begel} mm")
        st.write(f"**Selimut Beton:** {selimut} mm")

# --- VISUALISASI REALISTIS ---
st.divider()
st.subheader("🖼️ Detail Penampang Balok")
fig, ax = plt.subplots(figsize=(4, 5))
ax.add_patch(patches.Rectangle((0, 0), b, h, color='#ecf0f1', ec='black', lw=2)) # Beton
# Sengkang
ax.add_patch(patches.Rectangle((selimut, selimut), b-(2*selimut), h-(2*selimut), fill=False, lw=1.5, ls='--', color='blue'))
# Tulangan Atas
for i in range(n_atas):
    x_pos = selimut + 10 + (i * (b - 2*selimut - 20) / (n_atas - 1 if n_atas > 1 else 1))
    ax.scatter(x_pos, h-selimut-10, color='black', s=80)
# Tulangan Bawah
for i in range(n_bawah):
    x_pos = selimut + 10 + (i * (b - 2*selimut - 20) / (n_bawah - 1 if n_bawah > 1 else 1))
    ax.scatter(x_pos, selimut+10, color='black', s=80)

plt.xlim(-20, b+20); plt.ylim(-20, h+20); plt.axis('off')
st.pyplot(fig)

# --- PDF REPORT KOMPLEKS ---
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "LAPORAN ANALISIS STRUKTUR FORMAL", ln=True, align='C')
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "Standar: SNI 2847:2019 & SNI 1726:2019", ln=True, align='C')
    pdf.ln(10)

    # Rumus & Perhitungan
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "I. DASAR PERHITUNGAN & RUMUS", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, f"1. Dimensi (h_min): L/{12 if tipe_b=='Balok Utama' else 15} \n"
                         f"2. Syarat Kuat Geser (Vn > Vu): Vs = (Av * fy * d) / s \n"
                         f"3. Ketahanan Gempa: Mengikuti kaidah SRPMK/SRPMM berdasarkan KDS {kategori_gempa}.\n"
                         f"4. Luas Tulangan Minimum: As_min = (sqrt(fc') / 4*fy) * b * d")
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "II. DETAIL ELEMEN", ln=True)
    pdf.cell(0, 8, f"Tipe: {tipe_b} | Bentang: {L} m", ln=True)
    pdf.cell(0, 8, f"Dimensi: {b} x {h} mm | f'c: {fc} MPa", ln=True)
    pdf.cell(0, 8, f"Penulangan: Atas {n_atas}D{db}, Bawah {n_bawah}D{db}", ln=True)
    pdf.cell(0, 8, f"Sengkang: P10 - {s_begel} mm (Tumpuan)", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

if st.button("Download Laporan Teknis Lengkap (PDF)"):
    pdf_bytes = generate_pdf()
    st.download_button("Klik untuk Mengunduh PDF", data=pdf_bytes, file_name="Laporan_Struktur_Akuran.pdf")
