import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro-Civil SNI Calculator", layout="wide")

# --- FUNGSI HELPER ---
def hitung_tulangan(luas_target, diameter):
    luas_satu_besi = 0.25 * math.pi * (diameter**2)
    jumlah = math.ceil(luas_target / luas_satu_besi)
    if jumlah < 2: jumlah = 2 # Minimal 2 baris
    return jumlah

# --- UI HEADER ---
st.title("🏗️ Pro-Civil: Perencanaan Struktur Standar SNI")
st.markdown("Aplikasi perancangan balok dan kolom berdasarkan **SNI 2847:2019**, **SNI 1727:2020**, dan **SNI 2052:2017** (Baja Tulangan).")

tabs = st.tabs(["📊 Desain Struktur", "📄 Laporan PDF", "📚 Dokumen Referensi"])

with tabs[0]:
    col_input, col_viz = st.columns([1, 1])
    
    with col_input:
        st.subheader("⚙️ Parameter Material & Beban")
        c1, c2 = st.columns(2)
        with c1:
            fc = st.selectbox("Mutu Beton (f'c) MPa", [20, 25, 30, 35], index=1, help="Beton K-250 setara ~20.8 MPa, K-300 ~25 MPa")
            fy = st.selectbox("Mutu Baja (fy) MPa", [280, 420], index=1, help="BjTS 420 adalah standar terbaru")
        with c2:
            L = st.number_input("Bentang Balok (m)", 1.0, 20.0, 5.0)
            lantai = st.number_input("Jumlah Lantai", 1, 20, 2)

        st.subheader("📐 Opsi Penulangan")
        diam_balok = st.selectbox("Diameter Besi Utama Balok (mm)", [13, 16, 19, 22, 25], index=1)
        diam_kolom = st.selectbox("Diameter Besi Utama Kolom (mm)", [13, 16, 19, 22, 25], index=1)

    # --- LOGIKA PERHITUNGAN DETAIL ---
    # 1. Balok
    h_f = int(((L * 1000) / 16 // 50 + 1) * 50) 
    b_f = int((h_f * 0.5 // 25 + 1) * 25)
    # Rasio tulangan tarik minimal (SNI 2847:2019)
    as_min_balok = (math.sqrt(fc) / (4 * fy)) * b_f * (h_f - 50)
    n_besi_balok = hitung_tulangan(as_min_balok, diam_balok)

    # 2. Kolom
    pu = lantai * 25 * 12 # Asumsi area 25m2 per kolom
    ag_req = (pu * 1000) / (0.35 * fc)
    sisi_k = int((ag_req**0.5 // 50 + 1) * 50)
    if sisi_k < 200: sisi_k = 200
    as_kolom = 0.01 * (sisi_k**2) # Rasio 1%
    n_besi_kolom = hitung_tulangan(as_kolom, diam_kolom)
    if n_besi_kolom % 2 != 0: n_besi_kolom += 1 # Genap untuk kolom

    with col_viz:
        st.subheader("🖼️ Visualisasi Penampang")
        v1, v2 = st.columns(2)
        
        with v1:
            fig1, ax1 = plt.subplots(figsize=(2, 3))
            ax1.add_patch(patches.Rectangle((0, 0), b_f, h_f, color='#bdc3c7'))
            # Titik Tulangan
            ax1.scatter([50, b_f-50], [50, 50], color='black', s=50)
            ax1.set_title(f"Balok {b_f}x{h_f}", fontsize=8)
            plt.axis('off')
            st.pyplot(fig1)
            st.write(f"Tulangan: **{n_besi_balok}D{diam_balok}**")

        with v2:
            fig2, ax2 = plt.subplots(figsize=(2, 3))
            ax2.add_patch(patches.Rectangle((0, 0), sisi_k, sisi_k, color='#34495e', alpha=0.3))
            ax2.set_title(f"Kolom {sisi_k}x{sisi_k}", fontsize=8)
            plt.axis('off')
            st.pyplot(fig2)
            st.write(f"Tulangan: **{n_besi_kolom}D{diam_kolom}**")

with tabs[1]:
    st.subheader("🖨️ Generate Laporan Profesional")
    if st.button("Siapkan Data PDF"):
        # Logika PDF Kompleks
        pdf = FPDF()
        pdf.add_page()
        # Header
        pdf.set_fill_color(44, 62, 80)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 20, "STRUCTURAL DESIGN REPORT", ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 12)
        pdf.ln(25)
        
        # Tabel Data
        pdf.cell(0, 10, "A. PROPERTI MATERIAL", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(100, 8, f"Mutu Beton (f'c): {fc} MPa", border=1)
        pdf.cell(90, 8, f"Mutu Baja (fy): {fy} MPa", border=1, ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "B. DIMENSI & TULANGAN ELEMEN", ln=True)
        pdf.set_font("Arial", "", 10)
        
        # Row Balok
        pdf.cell(40, 8, "Elemen", border=1)
        pdf.cell(60, 8, "Dimensi (mm)", border=1)
        pdf.cell(90, 8, "Tulangan Utama", border=1, ln=True)
        pdf.cell(40, 8, "Balok", border=1)
        pdf.cell(60, 8, f"{b_f} x {h_f}", border=1)
        pdf.cell(90, 8, f"{n_besi_balok} D {diam_balok}", border=1, ln=True)
        
        # Row Kolom
        pdf.cell(40, 8, "Kolom", border=1)
        pdf.cell(60, 8, f"{sisi_k} x {sisi_k}", border=1)
        pdf.cell(90, 8, f"{n_besi_kolom} D {diam_kolom}", border=1, ln=True)

        html = create_download_link(pdf.output(dest="S").encode("latin-1"), "Laporan_Teknis_Struktur.pdf")
        st.markdown(html, unsafe_allow_html=True)

with tabs[2]:
    st.write("### Faktor Perhitungan SNI Utama:")
    st.markdown("""
    - **Faktor Reduksi Kekuatan ($\phi$):** Tekan Terkontrol = 0.65, Lentur = 0.90.
    - **Minimum Tulangan:** Berdasarkan Pasal 9.6.1.2 untuk menjamin kegagalan daktail.
    - **Selimut Beton:** Diasumsikan 40mm (Sesuai paparan cuaca standar Pasal 20.6.1).
    - **Standar Baja:** Mengacu pada **SNI 2052:2017** untuk baja tulangan beton.
    """)

# Fungsi Link Download (Base64)
def create_download_link(val, filename):
    b64 = base64.b64encode(val)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">Klik di sini untuk mengunduh PDF</a>'
