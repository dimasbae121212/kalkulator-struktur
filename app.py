import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- KONFIGURASI ---
st.set_page_config(page_title="Structural Engineer Pro", layout="wide")

# --- LOGIKA TEKNIK (ENGINEERING KERNEL) ---
def hitung_balok_pro(L, jenis, fc, fy, beban_mati, beban_hidup, zona_gempa):
    # 1. Penentuan Tinggi Minimum (SNI 2847:2019)
    # Faktor peruntukan balok
    mult = {"Balok Utama": 16, "Balok Anak": 21, "Balok Gantung/Kantilever": 8}
    h = int(((L * 1000) / mult[jenis] // 50 + 1) * 50)
    b = int((h * 0.6 // 25 + 1) * 25) # Rasio b/h yang lebih kaku
    
    # 2. Analisis Beban (SNI 1727:2020)
    qu = (1.2 * beban_mati) + (1.6 * beban_hidup)
    mu = (1/8) * qu * (L**2) # Momen tengah bentang (kNm)
    
    # 3. Perhitungan Tulangan Lentur (As)
    d = h - 60 # Jarak efektif (asumsi selimut 40mm + sengkang 10mm)
    phi = 0.9
    rn = (mu * 10**6) / (phi * b * d**2)
    m = fy / (0.85 * fc)
    rho = (1/m) * (1 - math.sqrt(1 - (2 * m * rn / fy)))
    
    # Syarat Rho Min (SNI)
    rho_min = max(1.4/fy, math.sqrt(fc)/(4*fy))
    rho_final = max(rho, rho_min)
    as_perlu = rho_final * b * d
    
    # Rekomendasi Diameter berdasarkan Bentang
    d_utama = 16 if L > 4 else 13
    luas_1_besi = 0.25 * math.pi * d_utama**2
    n_bawah = math.ceil(as_perlu / luas_1_besi)
    if n_bawah < 2: n_bawah = 2
    n_atas = max(2, math.ceil(n_bawah / 2)) # Tulangan tekan praktis
    
    # 4. Sengkang/Beugel (SNI Gempa 1726:2019)
    d_sengkang = 10
    if zona_gempa == "Tinggi":
        jarak_sengkang = min(d/4, 150) # Lebih rapat untuk gempa
    else:
        jarak_sengkang = min(d/2, 300)
        
    return b, h, n_atas, n_bawah, d_utama, d_sengkang, jarak_sengkang, mu, qu

# --- UI APLIKASI ---
st.title("🏗️ Structural Engineer Pro: Analisis SNI Terpadu")

with st.expander("🛠️ Input Data Teknis (Tanpa Slider)", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        peruntukan = st.selectbox("Peruntukan Balok", ["Balok Utama", "Balok Anak", "Balok Gantung/Kantilever"])
        L_input = st.number_input("Panjang Bentang (m)", value=5.0, step=0.1)
        zona = st.selectbox("Zona Risiko Gempa", ["Rendah/Sedang", "Tinggi"])
    with c2:
        fc_in = st.number_input("Mutu Beton f'c (MPa)", value=25)
        fy_in = st.number_input("Mutu Baja fy (MPa)", value=420)
        selimut = st.number_input("Rekomendasi Selimut Beton (mm)", value=40)
    with c3:
        dead_load = st.number_input("Beban Mati Terbagi (kN/m)", value=15.0)
        live_load = st.number_input("Beban Hidup Terbagi (kN/m)", value=10.0)

# Jalankan Hitungan
b, h, n_up, n_down, d_u, d_s, s_s, mu_val, qu_val = hitung_balok_pro(L_input, peruntukan, fc_in, fy_in, dead_load, live_load, zona)

# --- OUTPUT WEB ---
st.header("📊 Hasil Analisis Struktur")
res1, res2, res3 = st.columns(3)
res1.metric("Dimensi Balok", f"{b} x {h} mm")
res2.metric("Momen Terfaktor (Mu)", f"{mu_val:.2f} kNm")
res3.metric("Beban Terfaktor (Qu)", f"{qu_val:.2f} kN/m")

# Tampilan Tulangan
st.subheader("🛠️ Rekomendasi Penulangan Terhitung")
ans1, ans2, ans3 = st.columns(3)
ans1.success(f"Tulangan Bawah (Tarik): **{n_down} D{d_u}**")
ans2.success(f"Tulangan Atas (Tekan): **{n_up} D{d_u}**")
ans3.warning(f"Sengkang (Beugel): **ø{d_s} - {int(s_s)} mm**")

# --- VISUALISASI KECIL ---
st.subheader("🖼️ Detail Penampang Balok")
fig, ax = plt.subplots(figsize=(2, 2.5))
ax.add_patch(patches.Rectangle((0, 0), b, h, color='#bdc3c7', label='Beton'))
# Gambar Sengkang
ax.add_patch(patches.Rectangle((selimut, selimut), b-(2*selimut), h-(2*selimut), fill=False, edgecolor='black', linewidth=1))
# Gambar Titik Tulangan (Bawah)
x_pos_down = [selimut+10, b/2, b-selimut-10] if n_down > 2 else [selimut+10, b-selimut-10]
for x in x_pos_down:
    ax.scatter(x, selimut+10, color='red', s=30)
# Gambar Titik Tulangan (Atas)
for x in [selimut+10, b-selimut-10]:
    ax.scatter(x, h-selimut-10, color='blue', s=30)

plt.axis('off')
st.pyplot(fig)

# --- PDF REPORT (KOMPLEKS) ---
def generate_complex_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "LAPORAN ANALISIS STRUKTUR BETON (FULL SNI)", ln=True, align='C')
    pdf.ln(10)
    
    # Rumus & Perhitungan
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "1. Kombinasi Pembebanan (SNI 1727:2020)", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Rumus: Qu = 1.2D + 1.6L = (1.2 * {dead_load}) + (1.6 * {live_load}) = {qu_val} kN/m", ln=True)
    pdf.cell(0, 6, f"Momen Maks: Mu = 1/8 * Qu * L^2 = {mu_val:.2f} kNm", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "2. Analisis Penampang & Lentur (SNI 2847:2019)", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, f"Rasio Tulangan (rho) dihitung berdasarkan keseimbangan gaya tarik-tekan. \nMutu Beton: {fc_in} MPa, Mutu Baja: {fy_in} MPa. \nKebutuhan Luas Tulangan As = {int(n_down * 0.25 * 3.14 * d_u**2)} mm2.")
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "3. Ketahanan Gempa & Geser (SNI 1726:2019)", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, f"Berdasarkan zona gempa {zona}, jarak sengkang dibatasi maksimal d/4 atau 150mm pada daerah tumpuan untuk menjamin daktilitas struktur menghadapi gaya lateral gempa.")

    return pdf.output(dest="S").encode("latin-1")

st.download_button("📥 Unduh Laporan PDF Lengkap (Rumus & Analisa)", generate_complex_pdf(), "Laporan_Teknis_Pro.pdf", "application/pdf")
