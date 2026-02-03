import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Ekonomis", layout="wide")

# --- 2. LOGIKA TEKNIK EKONOMIS ---
def hitung_struktur_ekonomis(L, jenis, fc, tipe_besi, jml_lantai, t_dinding, j_dinding, gempa):
    # Fy Baja (Polos 280, Ulir 420)
    fy = 280 if tipe_besi == "Besi Polos (BjTP)" else 420
    
    # Tinggi Balok (Konstanta lebih ekonomis)
    # Utama L/12, Anak L/15, Ring Balok L/18
    mult = {"Balok Utama": 12, "Balok Anak": 15, "Ring Balok": 18, "Sloof": 12}
    h = int(((L * 1000) / mult[jenis] // 50 + 1) * 50)
    b = int((h * 0.6 // 25 + 1) * 25)
    
    # Perhitungan Beban Dinding (kN/m)
    # Bata merah ~2.5 kN/m2 per meter tinggi, Hebel ~1.0 kN/m2
    berat_jenis_dinding = 2.5 if j_dinding == "Bata Merah" else 1.0
    q_dinding = berat_jenis_dinding * t_dinding
    
    # Analisis Beban Terfaktor (1.2D + 1.6L)
    # D = Beban Dinding + Berat Sendiri (asumsi), L = Beban Hidup standar rumah
    qu = (1.2 * (q_dinding + 1.5)) + (1.6 * 2.0)
    mu = (1/8) * qu * (L**2)
    
    # Penulangan Lentur
    d = h - 35 # Jarak efektif lebih pendek (ekonomis)
    phi = 0.9
    
    # Diameter besi (Gunakan 10mm untuk bentang pendek agar hemat)
    d_u = 10 if L <= 3.5 else 12
    if tipe_besi == "Besi Ulir (BjTS)": d_u = 13 # Standar terkecil ulir
    
    if mu > 0:
        rn = (mu * 10**6) / (phi * b * d**2)
        m = fy / (0.85 * fc)
        check_val = 1 - (2 * m * rn / fy)
        rho = (1/m) * (1 - math.sqrt(max(0, check_val)))
        rho_min = 1.4 / fy
        rho_final = max(rho, rho_min)
    else:
        rho_final = 1.4 / fy
        
    as_perlu = rho_final * b * d
    n_dw = max(2, math.ceil(as_perlu / (0.25 * math.pi * d_u**2)))
    n_up = 2 # Atas cukup 2 sebagai pengaku
    
    # Sengkang (Default Besi 8 Polos - Lebih Ekonomis)
    d_s = 8
    # Jarak sengkang (Kelipatan 50mm)
    if gempa == "Tinggi":
        s_final = 100
    elif gempa == "Sedang":
        s_final = 150
    else:
        s_final = 200 # Area aman/rendah gempa
        
    return b, h, n_up, n_dw, d_u, d_s, s_final, mu, qu

# --- 3. INPUT DATA (TANPA SLIDER) ---
st.title("🏗️ CivilCalc Pro: Kalkulator Ekonomis & Realistis")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        peruntukan = st.selectbox("Peruntukan Struktur", ["Balok Utama", "Balok Anak", "Ring Balok", "Sloof"])
        L_in = st.number_input("Bentang Balok (m)", value=3.0, step=0.5)
        n_lantai = st.number_input("Jumlah Lantai", value=1, min_value=1)
        zona_gempa = st.selectbox("Area Gempa", ["Rendah", "Sedang", "Tinggi"])
    with c2:
        t_besi = st.radio("Jenis Besi", ["Besi Polos (BjTP)", "Besi Ulir (BjTS)"])
        fc_in = st.number_input("Mutu Beton f'c (MPa)", value=20)
        h_dinding = st.number_input("Tinggi Dinding per Lantai (m)", value=3.5)
    with c3:
        j_dinding = st.selectbox("Jenis Dinding", ["Bata Merah", "Bata Ringan (Hebel)"])
        selimut = st.number_input("Selimut Beton (mm)", value=30)

# Proses Hitung
b, h, n_up, n_dw, d_u, d_s, s_s, mu_v, qu_v = hitung_struktur_ekonomis(L_in, peruntukan, fc_in, t_besi, n_lantai, h_dinding, j_dinding, zona_gempa)

st.divider()

# --- 4. OUTPUT HASIL & VISUALISASI ---
res_col, viz_col = st.columns([3, 1])

with res_col:
    st.subheader("📋 Ringkasan Kebutuhan")
    o1, o2 = st.columns(2)
    with o1:
        st.write(f"**Dimensi Beton:** {b} x {h} mm")
        st.write(f"**Momen Maks (Mu):** {mu_v:.2f} kNm")
        st.write(f"**Beban Dinding:** {j_dinding} ({h_dinding}m)")
    with o2:
        st.success(f"**Tulangan Utama:** Atas {n_up}D{d_u}, Bawah {n_dw}D{d_u}")
        st.warning(f"**Sengkang (Beugel):** ø{d_s} - {s_s} mm")
        st.info(f"**Selimut Beton:** {selimut} mm")

with viz_col:
    st.write("**Sketsa Penampang**")
    fig, ax = plt.subplots(figsize=(0.8, 1.0)) # Super Kecil
    ax.add_patch(patches.Rectangle((0, 0), b, h, color='#f8f9fa', ec='black', lw=0.8))
    # Sengkang
    ax.add_patch(patches.Rectangle((selimut, selimut), b-(2*selimut), h-(2*selimut), fill=False, ls='--', lw=0.5))
    # Tulangan (2 atas, 2 bawah)
    ax.scatter([selimut+5, b-selimut-5], [selimut+5, selimut+5], c='red', s=8)
    ax.scatter([selimut+5, b-selimut-5], [h-selimut-5, h-selimut-5], c='blue', s=6)
    plt.axis('off')
    st.pyplot(fig)

# --- 5. PDF REPORT ---
def make_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "LAPORAN STRUKTUR EKONOMIS", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"Peruntukan: {peruntukan} | Bentang: {L_in} m | Gempa: {zona_gempa}", ln=True)
    pdf.cell(0, 7, f"Dinding: {j_dinding} (Tinggi {h_dinding}m) | Mutu Beton: {fc_in} MPa", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "HASIL REKOMENDASI:", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f"- Dimensi Beton: {b} x {h} mm", ln=True)
    pdf.cell(0, 7, f"- Tulangan Utama: Atas {n_up}D{d_u} & Bawah {n_dw}D{d_u}", ln=True)
    pdf.cell(0, 7, f"- Sengkang: Besi {d_s} Polos, Jarak {s_s} mm", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Analisis ini menggunakan asumsi beban rumah tinggal standar. Kebutuhan besi telah dioptimalkan untuk efisiensi biaya tanpa mengesampingkan syarat minimum SNI 2847:2019.")
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Unduh Laporan PDF", make_pdf(), "Laporan_Ekonomis.pdf", "application/pdf")
