import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Ekonomis SNI", page_icon="🏗️", layout="wide")

# --- 2. LOGIKA TEKNIK EKONOMIS ---
def hitung_struktur_pro(L, jenis, fc, fy_jenis, jml_lantai, t_dinding, j_dinding, gempa):
    # Properti Material
    fy = 280 if fy_jenis == "Besi Polos (BjTP)" else 420
    berat_dinding = 2.5 if j_dinding == "Bata Merah (Berat)" else 1.0 # kN/m2
    
    # 1. Dimensi Balok (Ekonomis)
    mult = {"Balok Utama": 12, "Balok Anak": 15, "Ring Balok": 18, "Sloof": 12}
    h = int(((L * 1000) / mult[jenis] // 50 + 1) * 50)
    b = int((h * 0.6 // 25 + 1) * 25)
    
    # 2. Analisis Beban (Dihitung per meter lari)
    beban_dinding = t_dinding * berat_dinding
    beban_mati_tambahan = 5.0 # Plafon, keramik, dll
    dead_total = (beban_dinding + beban_mati_tambahan) * jml_lantai
    live_total = 2.5 * jml_lantai # Beban hidup hunian standar
    
    qu = (1.2 * dead_total) + (1.6 * live_total)
    mu = (1/8) * qu * (L**2)
    
    # 3. Penulangan Lentur
    d = h - 35 # Jarak efektif (Selimut beton lebih tipis untuk efisiensi)
    phi = 0.9
    
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
    
    # Rekomendasi Diameter (Ekonomis: Besi 10 untuk bentang pendek)
    d_u = 10 if L <= 3.5 else 13
    n_bawah = max(2, math.ceil(as_perlu / (0.25 * math.pi * d_u**2)))
    n_atas = 2 # Praktis
    
    # 4. Sengkang (Beugel)
    d_s = 8 # Gunakan besi 8 polos sesuai permintaan
    if gempa == "Tinggi":
        s_final = 100
    elif gempa == "Sedang":
        s_final = 125
    else:
        s_final = 150 # Sengkang ekonomis 15 cm
        
    return b, h, n_atas, n_bawah, d_u, d_s, s_final, mu, qu

# --- 3. INPUT DATA ---
st.title("🏗️ CivilCalc Pro: Optimasi Anggaran & SNI")

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        peruntukan = st.selectbox("Peruntukan Struktur", ["Balok Utama", "Balok Anak", "Ring Balok", "Sloof"])
        L_in = st.number_input("Panjang Bentang (m)", value=3.0, step=0.1)
        n_lantai = st.number_input("Jumlah Lantai", value=1, min_value=1)
        gempa_in = st.selectbox("Area Risiko Gempa", ["Rendah", "Sedang", "Tinggi"])
    with c2:
        t_dinding = st.number_input("Tinggi Dinding (m)", value=3.0)
        j_dinding = st.selectbox("Jenis Dinding", ["Bata Merah (Berat)", "Hebel (Ringan)"])
        tipe_besi = st.radio("Jenis Tulangan Utama", ["Besi Polos (BjTP)", "Besi Ulir (BjTS)"])
    with c3:
        fc_in = st.number_input("Mutu Beton f'c (MPa)", value=20)
        selimut_in = st.number_input("Selimut Beton (mm)", value=30)

# Proses Hitung
b, h, n_up, n_dw, d_u, d_s, s_s, mu_v, qu_v = hitung_struktur_pro(L_in, peruntukan, fc_in, tipe_besi, n_lantai, t_dinding, j_dinding, gempa_in)

st.divider()

# --- 4. OUTPUT & VISUALISASI ---
res_col, viz_col = st.columns([3, 1])

with res_col:
    st.subheader("📋 Ringkasan Hasil (Ekonomis)")
    o1, o2 = st.columns(2)
    with o1:
        st.write(f"**Dimensi Beton:** {b} x {h} mm")
        st.write(f"**Momen Maks (Mu):** {mu_v:.2f} kNm")
        st.write(f"**Beban Terfaktor:** {qu_v:.2f} kN/m")
    with o2:
        st.success(f"**Tulangan Bawah:** {n_dw} D{d_u}")
        st.success(f"**Tulangan Atas:** {n_up} D{d_u}")
        st.warning(f"**Sengkang:** ø{d_s} - {s_s} mm")

with viz_col:
    st.write("**Penampang**")
    fig, ax = plt.subplots(figsize=(0.8, 1.0)) # Visualisasi Diperkecil
    ax.add_patch(patches.Rectangle((0, 0), b, h, color='#f2f2f2', ec='black', lw=0.8))
    # Sengkang
    ax.add_patch(patches.Rectangle((selimut_in, selimut_in), b-(2*selimut_in), h-(2*selimut_in), fill=False, ls=':', lw=0.5))
    
    # Tulangan Bawah (Dinamis sesuai hasil hitungan)
    dx = (b - 2*selimut_in) / (n_dw - 1) if n_dw > 1 else 0
    for i in range(n_dw):
        ax.scatter(selimut_in + i*dx, selimut_in + 5, c='red', s=8)
    # Tulangan Atas
    for i in [selimut_in+5, b-selimut_in-5]:
        ax.scatter(i, h-selimut_in-5, c='blue', s=6)
        
    plt.axis('off')
    st.pyplot(fig)

# --- 5. PDF REPORT ---
def make_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "LAPORAN TEKNIS STRUKTUR EKONOMIS", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"Peruntukan: {peruntukan} | Bentang: {L_in} m | Gempa: {gempa_in}", ln=True)
    pdf.cell(0, 6, f"Beban Dinding: {j_dinding} (Tinggi {t_dinding}m)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "HASIL REKOMENDASI:", ln=True)
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 6, f"- Beton: {b}x{h} mm", ln=True)
    pdf.cell(0, 6, f"- Tulangan: Atas {n_up}D{d_u}, Bawah {n_dw}D{d_u}", ln=True)
    pdf.cell(0, 6, f"- Sengkang: Besi {d_s} Jarak {s_s} mm", ln=True)
    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Unduh Laporan PDF", make_pdf(), "Laporan_Ekonomis.pdf", "application/pdf")
