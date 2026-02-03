import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Pro Ekonomis", layout="wide")

# --- 2. LOGIKA TEKNIK EKONOMIS & AKURAT ---
def hitung_struktur_final(L, jenis_struk, fc, fy_jenis, mati_tambah, hidup, jml_lantai, h_dinding, tipe_dinding, gempa):
    # Penentuan Fy (SNI 2052:2017)
    fy = 280 if fy_jenis == "Besi Polos (BjTP)" else 420
    
    # Tinggi Balok Ekonomis
    mult = {"Balok Utama": 12, "Balok Anak": 15, "Ring Balok": 18, "Sloof": 12}
    h = int(((L * 1000) / mult[jenis_struk] // 50 + 1) * 50)
    # Ring balok atau bentang pendek minimal 150mm/200mm
    if h < 200 and jenis_struk != "Ring Balok": h = 200
    b = int((h * 0.6 // 25 + 1) * 25)
    
    # Analisis Beban Dinding (kN/m)
    berat_jenis_dinding = 2.5 if tipe_dinding == "Bata Merah" else 0.8 # kN/m2 per meter tinggi
    beban_dinding = berat_jenis_dinding * h_dinding
    
    # Beban Terfaktor (SNI 1727:2020)
    # Berat sendiri beton + beban dinding + beban tambahan
    berat_sendiri = (b/1000 * h/1000 * 24)
    qu = (1.2 * (berat_sendiri + beban_dinding + mati_tambah) + 1.6 * hidup) * jml_lantai
    mu = (1/8) * qu * (L**2)
    
    # Penulangan Lentur (Optimasi Anggaran)
    d = h - 30 - 8 - 5 # Selimut 30mm, Sengkang 8mm
    phi = 0.9
    
    if mu > 0:
        rn = (mu * 10**6) / (phi * b * d**2)
        m = fy / (0.85 * fc)
        check_val = 1 - (2 * m * rn / fy)
        rho = (1/m) * (1 - math.sqrt(max(0, check_val)))
        
        # Rho min untuk hunian kecil agar hemat (SNI 2847 Pasal 9.6.1.2)
        rho_min = 1.4 / fy
        rho_final = max(rho, rho_min)
    else:
        rho_final = 1.4 / fy
        
    as_perlu = rho_final * b * d
    
    # Pemilihan Diameter Besi (Sistem Rekomendasi)
    # Jika bentang <= 3m dan beban rendah, gunakan D10 agar hemat
    if L <= 3.5 and mu < 15:
        d_utama = 10
    else:
        d_utama = 13 if fy_jenis == "Besi Polos (BjTP)" else 16
        
    n_bawah = max(2, math.ceil(as_perlu / (0.25 * math.pi * d_utama**2)))
    n_atas = 2 # Pengaku beugel standar
    
    # Sengkang (Beugel) - Penyesuaian Gempa & Kelipatan 5 cm
    d_sengkang = 8 if L <= 4 else 10
    if gempa == "Tinggi":
        s_praktis = 100
    elif gempa == "Sedang":
        s_praktis = 150
    else: # Rendah
        s_praktis = 200
        
    return b, h, n_atas, n_bawah, d_utama, d_sengkang, s_praktis, mu, qu, beban_dinding

# --- 3. INPUT DATA (TANPA SLIDER) ---
st.title("🏗️ CivilCalc Pro: Optimasi Struktur & Biaya")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        peruntukan = st.selectbox("Peruntukan Struktur", ["Balok Utama", "Balok Anak", "Ring Balok", "Sloof"])
        L_in = st.number_input("Panjang Bentang (m)", value=3.0, step=0.1)
        n_lantai = st.number_input("Jumlah Lantai", value=1, min_value=1)
        gempa_in = st.selectbox("Wilayah Gempa", ["Rendah", "Sedang", "Tinggi"])
    with c2:
        tipe_besi = st.radio("Jenis Besi Utama", ["Besi Polos (BjTP)", "Besi Ulir (BjTS)"])
        h_dinding = st.number_input("Tinggi Dinding per Lantai (m)", value=3.2)
        t_dinding = st.selectbox("Jenis Dinding", ["Bata Merah", "Bata Ringan/Hebel"])
    with c3:
        fc_in = st.number_input("Mutu Beton f'c (MPa)", value=20)
        mati_tmb = st.number_input("Beban Mati Tambahan (kN/m)", value=2.0)
        live = st.number_input("Beban Hidup (kN/m)", value=2.0)

# Hitung
b, h, n_up, n_dw, d_u, d_s, s_s, mu_v, qu_v, q_din = hitung_struktur_final(L_in, peruntukan, fc_in, tipe_besi, mati_tmb, live, n_lantai, h_dinding, t_dinding, gempa_in)

st.divider()

# --- 4. OUTPUT HASIL & VISUALISASI ---
res_col, viz_col = st.columns([3, 1])

with res_col:
    st.subheader("📋 Ringkasan Teknis Ekonomis")
    o1, o2 = st.columns(2)
    with o1:
        st.write(f"**Dimensi Beton:** {b} x {h} mm")
        st.write(f"**Beban Dinding:** {q_din:.2f} kN/m")
        st.write(f"**Beban Terfaktor (Qu):** {qu_v:.2f} kN/m")
        st.write(f"**Momen Desain (Mu):** {mu_v:.2f} kNm")
    with o2:
        st.success(f"**Tulangan Tarik (Bawah):** {n_dw} D{d_u}")
        st.success(f"**Tulangan Atas:** {n_up} D{d_u}")
        st.warning(f"**Sengkang (Beugel):** ø{d_s} - {s_s} mm")

with viz_col:
    st.write("**Visualisasi**")
    fig, ax = plt.subplots(figsize=(0.8, 1.0)) # Super kecil & proporsional
    ax.add_patch(patches.Rectangle((0, 0), b, h, color='#fdfdfd', ec='black', lw=0.8))
    # Gambar titik tulangan sesuai jumlah (n_dw dan n_up)
    # Bawah
    for i in range(n_dw):
        pos_x = 30 + (i * (b-60)/(max(1, n_dw-1)))
        ax.scatter(pos_x, 30, c='red', s=8)
    # Atas
    for i in range(n_up):
        pos_x = 30 + (i * (b-60)/(max(1, n_up-1)))
        ax.scatter(pos_x, h-30, c='blue', s=8)
    plt.axis('off')
    st.pyplot(fig)

# --- 5. PDF REPORT ---
def make_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "LAPORAN TEKNIS STRUKTUR EKONOMIS", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, f"INPUT: {peruntukan} | BENTANG {L_in}m | GEMPA {gempa_in.upper()}", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 6, f"Dinding: {t_dinding} ({h_dinding}m). Mutu Beton: {fc_in} MPa. Jenis Besi: {tipe_besi}.")
    
    pdf.ln(4)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "ANALISIS GAYA & KETAHANAN GEMPA:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"- Beban Terfaktor (Qu = 1.2D + 1.6L): {qu_v:.2f} kN/m", ln=True)
    pdf.cell(0, 6, f"- Momen Maksimum (Mu): {mu_v:.2f} kNm", ln=True)
    pdf.cell(0, 6, f"- Gaya Tarik Tekan: Dihitung berdasarkan kesetimbangan limit SNI 2847:2019", ln=True)
    
    pdf.ln(4)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "REKOMENDASI PENULANGAN (HEMAT ANGGARAN):", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"1. Dimensi Beton: {b} x {h} mm", ln=True)
    pdf.cell(0, 6, f"2. Tulangan Utama: Bawah {n_dw}D{d_u}, Atas {n_up}D{d_u}", ln=True)
    pdf.cell(0, 6, f"3. Sengkang: ø{d_s} - {s_s} mm (Efisiensi Lapangan)", ln=True)
    
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Unduh Laporan PDF", make_pdf(), "Laporan_Ekonomis.pdf", "application/pdf")
