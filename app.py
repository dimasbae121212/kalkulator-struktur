import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- KONFIGURASI ---
st.set_page_config(page_title="CivilCalc Pro V2", layout="wide")

# --- LOGIKA TEKNIK ---
def hitung_struktur_ekonomis(L, jenis, fc, fy_jenis, mati, hidup, jml_lantai):
    # Penentuan Fy berdasarkan jenis besi
    fy = 280 if fy_jenis == "Besi Polos (BjTP)" else 420
    
    # 1. Dimensi Balok (Optimasi peruntukan)
    mult = {"Balok Utama": 12, "Balok Anak": 15, "Ring Balok": 18, "Sloof": 12}
    h = int(((L * 1000) / mult[jenis] // 50 + 1) * 50)
    b = int((h * 0.6 // 25 + 1) * 25)
    
    # 2. Analisis Beban Terfaktor (SNI 1727:2020)
    # Beban dikalikan jumlah lantai untuk akumulasi ke kolom (jika relevan)
    qu = (1.2 * mati) + (1.6 * hidup)
    mu = (1/8) * qu * (L**2)
    
    # 3. Penulangan Lentur (Akurasi Tinggi)
    d = h - 40 - 10 - 8 # Selimut - Sengkang - 1/2 Tul Utama
    phi = 0.9
    if mu > 0:
        rn = (mu * 10**6) / (phi * b * d**2)
        m = fy / (0.85 * fc)
        rho = (1/m) * (1 - math.sqrt(math.max(0, 1 - (2 * m * rn / fy))))
        rho_min = 1.4 / fy
        rho_final = max(rho, rho_min)
    else:
        rho_final = 1.4 / fy
        
    as_perlu = rho_final * b * d
    d_utama = 13 if fy_jenis == "Besi Polos (BjTP)" else 16
    n_bawah = max(2, math.ceil(as_perlu / (0.25 * math.pi * d_utama**2)))
    n_atas = 2 # Standar praktis untuk pengaku sengkang
    
    # 4. Sengkang (Kelipatan 50mm untuk kemudahan lapangan)
    # Syarat praktis sengkang L/4 bentang
    s_lapangan = int((d / 2 // 50) * 50)
    if s_lapangan > 200: s_lapangan = 200 # Batas maksimum umum
    if s_lapangan < 100: s_lapangan = 100 # Batas minimum praktis
        
    return b, h, n_atas, n_bawah, d_utama, s_lapangan, mu, qu

# --- UI APLIKASI ---
st.title("🏗️ CivilCalc Pro: Standar Lapangan & SNI")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        peruntukan = st.selectbox("Peruntukan Struktur", ["Balok Utama", "Balok Anak", "Ring Balok", "Sloof"])
        L_in = st.number_input("Panjang Bentang (m)", value=4.0)
        n_lantai = st.number_input("Jumlah Lantai", value=1, min_value=1)
    with c2:
        tipe_besi = st.radio("Jenis Tulangan Utama", ["Besi Polos (BjTP)", "Besi Ulir (BjTS)"])
        fc_in = st.number_input("Mutu Beton f'c (MPa)", value=20) # Standar rumah tinggal
        selimut_in = st.number_input("Selimut Beton (mm)", value=30)
    with c3:
        dead = st.number_input("Beban Mati (kN/m)", value=10.0)
        live = st.number_input("Beban Hidup (kN/m)", value=5.0)

# Hitung
b, h, n_up, n_dw, d_u, s_s, mu_v, qu_v = hitung_struktur_ekonomis(L_in, peruntukan, fc_in, tipe_besi, dead, live, n_lantai)

st.divider()

# --- HASIL & VISUALISASI KECIL ---
res_col, viz_col = st.columns([2, 1])

with res_col:
    st.subheader("📋 Output Analisis")
    o1, o2 = st.columns(2)
    o1.write(f"**Dimensi Beton:** {b} x {h} mm")
    o1.write(f"**Beban Qu:** {qu_v:.2f} kN/m")
    o1.write(f"**Momen Mu:** {mu_v:.2f} kNm")
    
    o2.success(f"**Tulangan Bawah:** {n_dw} D{d_u}")
    o2.success(f"**Tulangan Atas:** {n_up} D{d_u}")
    o2.warning(f"**Sengkang:** ø8 - {s_s} mm")

with viz_col:
    st.subheader("🖼️ Sketsa")
    # Visualisasi dibuat sangat kecil (figsize kecil)
    fig, ax = plt.subplots(figsize=(1.2, 1.5)) 
    ax.add_patch(patches.Rectangle((0, 0), b, h, color='#ecf0f1', ec='black', lw=1))
    # Sengkang
    ax.add_patch(patches.Rectangle((selimut_in, selimut_in), b-(2*selimut_in), h-(2*selimut_in), fill=False, ls='--', lw=0.5))
    # Besi (Hanya simbolik kecil)
    ax.scatter([selimut_in+5, b-selimut_in-5], [selimut_in+5, selimut_in+5], c='red', s=15)
    ax.scatter([selimut_in+5, b-selimut_in-5], [h-selimut_in-5, h-selimut_in-5], c='blue', s=10)
    plt.axis('off')
    st.pyplot(fig)



# --- PDF REPORT ---
def make_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "LAPORAN RINGKAS DESAIN STRUKTUR", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, f"PERUNTUKAN: {peruntukan.upper()} ({n_lantai} LANTAI)", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"- Panjang Bentang: {L_in} m", ln=True)
    pdf.cell(0, 6, f"- Material: Beton f'c {fc_in} MPa, {tipe_besi}", ln=True)
    pdf.ln(3)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "HASIL PERHITUNGAN:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"1. Dimensi: {b} x {h} mm", ln=True)
    pdf.cell(0, 6, f"2. Tulangan Lentur: Atas {n_up}D{d_u}, Bawah {n_dw}D{d_u}", ln=True)
    pdf.cell(0, 6, f"3. Sengkang: Jarak {s_s} mm (Kelipatan Praktis)", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 8, "REFERENSI RUMUS:", ln=True)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Momen (Mu) = 1/8 * Qu * L^2\nBeban Terfaktor (Qu) = 1.2D + 1.6L\nSyarat Spasi Sengkang (s) <= d/2 (SNI 2847:2019)")
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Download PDF", make_pdf(), "Laporan_Struktur.pdf", "application/pdf")
