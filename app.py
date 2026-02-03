import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import math
import base64

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Pro-Civil SNI Calculator", page_icon="🏗️", layout="wide")

# --- 2. FUNGSI HELPER (LOGIKA) ---
def hitung_tulangan(luas_target, diameter):
    luas_satu_besi = 0.25 * math.pi * (diameter**2)
    jumlah = math.ceil(luas_target / luas_satu_besi)
    if jumlah < 2: jumlah = 2 
    return jumlah

# --- 3. UI HEADER & LANDING INFO ---
st.title("🏗️ Pro-Civil: Perencanaan Struktur Standar SNI")
st.markdown("""
Aplikasi ini membantu Insinyur dan Kontraktor dalam mengestimasi dimensi elemen struktur dan kebutuhan penulangan berdasarkan:
* **SNI 2847:2019** (Persyaratan Beton Struktural)
* **SNI 1727:2020** (Beban Desain Minimum)
* **SNI 2052:2017** (Baja Tulangan Beton)
""")

# --- 4. TABS MENU ---
tabs = st.tabs(["📊 Desain Struktur", "📄 Laporan PDF", "📚 Referensi SNI"])

with tabs[0]:
    col_input, col_viz = st.columns([1, 1])
    
    with col_input:
        st.subheader("⚙️ Parameter Material & Beban")
        c1, c2 = st.columns(2)
        with c1:
            fc = st.selectbox("Mutu Beton (f'c) MPa", [20, 25, 30, 35], index=1, help="K-250 ≈ 20 MPa, K-300 ≈ 25 MPa")
            fy = st.selectbox("Mutu Baja (fy) MPa", [280, 420], index=1)
        with c2:
            L = st.number_input("Bentang Balok (m)", 1.0, 20.0, 5.0)
            lantai = st.number_input("Jumlah Lantai", 1, 20, 2)

        st.subheader("📐 Opsi Penulangan")
        ca, cb = st.columns(2)
        with ca:
            diam_balok = st.selectbox("D Utama Balok (mm)", [13, 16, 19, 22, 25], index=1)
        with cb:
            diam_kolom = st.selectbox("D Utama Kolom (mm)", [13, 16, 19, 22, 25], index=1)

    # --- LOGIKA PERHITUNGAN ---
    # Perhitungan Balok (SNI 2847:2019 Tabel 9.3.1.1)
    h_f = int(((L * 1000) / 16 // 50 + 1) * 50) 
    b_f = int((h_f * 0.5 // 25 + 1) * 25)
    as_min_balok = (math.sqrt(fc) / (4 * fy)) * b_f * (h_f - 50)
    n_besi_balok = hitung_tulangan(as_min_balok, diam_balok)

    # Perhitungan Kolom (Estimasi Beban Aksial)
    pu = lantai * 25 * 12 # Area 25m2, Beban 12kN/m2
    ag_req = (pu * 1000) / (0.35 * fc)
    sisi_k = int((ag_req**0.5 // 50 + 1) * 50)
    if sisi_k < 200: sisi_k = 200
    as_kolom = 0.01 * (sisi_k**2) # Rasio 1%
    n_besi_kolom = hitung_tulangan(as_kolom, diam_kolom)
    if n_besi_kolom % 2 != 0: n_besi_kolom += 1

    with col_viz:
        st.subheader("🖼️ Visualisasi Penampang")
        v1, v2 = st.columns(2)
        
        with v1:
            # Sketsa Balok
            fig1, ax1 = plt.subplots(figsize=(2, 2.5))
            ax1.add_patch(patches.Rectangle((0, 0), b_f, h_f, color='#bdc3c7', label='Beton'))
            # Gambar Tulangan Sederhana
            ax1.scatter([50, b_f-50], [50, 50], color='red', s=30)
            ax1.set_title(f"Balok {b_f}x{h_f}", fontsize=9)
            plt.axis('off')
            st.pyplot(fig1)
            st.write(f"Tulangan Utama: **{n_besi_balok} D{diam_balok}**")

        with v2:
            # Sketsa Kolom
            fig2, ax2 = plt.subplots(figsize=(2, 2.5))
            ax2.add_patch(patches.Rectangle((0, 0), sisi_k, sisi_k, color='#34495e', alpha=0.3))
            # Titik sudut tulangan
            ax2.scatter([40, sisi_k-40, 40, sisi_k-40], [40, 40, sisi_k-40, sisi_k-40], color='black', s=30)
            ax2.set_title(f"Kolom {sisi_k}x{sisi_k}", fontsize=9)
            plt.axis('off')
            st.pyplot(fig2)
            st.write(f"Tulangan Utama: **{n_besi_kolom} D{diam_kolom}**")

with tabs[1]:
    st.subheader("🖨️ Generate Laporan Profesional")
    st.write("Klik tombol di bawah ini untuk mengunduh rincian teknis dalam format PDF.")

    # Inisialisasi PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Header Laporan
    pdf.set_fill_color(44, 62, 80)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 20, "STRUCTURAL ANALYSIS REPORT", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(25)
    
    # Bagian 1: Material
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. PROPERTI MATERIAL & INPUT", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 8, f"Mutu Beton (f'c): {fc} MPa", border=1)
    pdf.cell(95, 8, f"Mutu Baja (fy): {fy} MPa", border=1, ln=True)
    pdf.cell(95, 8, f"Bentang Struktur: {L} m", border=1)
    pdf.cell(95, 8, f"Jumlah Lantai: {lantai}", border=1, ln=True)
    
    pdf.ln(5)
    
    # Bagian 2: Hasil
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. HASIL ANALISA DIMENSI & PENULANGAN", ln=True)
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(45, 8, "Elemen", border=1, align='C', fill=True)
    pdf.cell(65, 8, "Dimensi (mm)", border=1, align='C', fill=True)
    pdf.cell(80, 8, "Tulangan (Rekomendasi)", border=1, ln=True, align='C', fill=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(45, 8, "Balok Utama", border=1)
    pdf.cell(65, 8, f"{b_f} x {h_f}", border=1, align='C')
    pdf.cell(80, 8, f"{n_besi_balok} D {diam_balok}", border=1, ln=True, align='C')
    
    pdf.cell(45, 8, "Kolom Utama", border=1)
    pdf.cell(65, 8, f"{sisi_k} x {sisi_k}", border=1, align='C')
    pdf.cell(80, 8, f"{n_besi_kolom} D {diam_kolom}", border=1, ln=True, align='C')

    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "DISCLAIMER: Laporan ini dihasilkan otomatis untuk keperluan estimasi awal. Perhitungan gempa, detail sambungan, dan penulangan geser/sengkang harus dihitung lebih lanjut oleh ahli struktur.")

    # Tombol Download (Cara yang benar di Streamlit)
    pdf_output = pdf.output(dest="S").encode("latin-1")
    st.download_button(
        label="📥 Unduh Laporan PDF",
        data=pdf_output,
        file_name=f"Laporan_Struktur_{L}m.pdf",
        mime="application/pdf"
    )

with tabs[2]:
    st.header("Referensi & Faktor Desain")
    st.markdown("""
    ### Standar Nasional Indonesia (SNI)
    1. **Faktor Reduksi Kekuatan ($\phi$):**
        * Lentur (Balok): 0.90
        * Tekan (Kolom): 0.65 - 0.75
    2. **Beban Terfaktor (U):**
        * $U = 1.2D + 1.6L$ (Kombinasi Beban Mati & Hidup)
    3. **Tinggi Minimum Balok:**
        * Mengacu pada Pasal 9.3.1.1 untuk kontrol lendutan tanpa perhitungan manual.
    4. **Persentase Tulangan Kolom:**
        * Dibatasi minimal 1% dan maksimal 8% dari luas penampang beton (Ag).
    5. **Selimut Beton:**
        * Standar 40mm untuk elemen yang tidak bersentuhan langsung dengan tanah.
    """)
