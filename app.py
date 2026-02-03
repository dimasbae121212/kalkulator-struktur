import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fpdf import FPDF
import base64

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="CivilCalc Pro + PDF", layout="wide")

# --- FUNGSI GENERATE PDF ---
def create_pdf(b_f, h_f, L, pu, sisi):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Laporan Hasil Perhitungan Struktur Sederhana", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Berdasarkan SNI 2847:2019 & SNI 1727:2020", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "1. Hasil Perhitungan Balok:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"- Panjang Bentang: {L} meter", ln=True)
    pdf.cell(200, 10, f"- Dimensi Rekomendasi: {b_f} mm x {h_f} mm", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "2. Hasil Perhitungan Kolom:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"- Total Beban Terfaktor (Pu): {pu} kN", ln=True)
    pdf.cell(200, 10, f"- Dimensi Kolom: {sisi} mm x {sisi} mm", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 5, "Catatan: Hasil ini adalah estimasi awal. Penulangan detail dan pengecekan gempa harus dilakukan oleh tenaga ahli.")
    
    return pdf.output(dest="S").encode("latin-1")

# --- UI APLIKASI ---
st.title("🏗️ CivilCalc Pro: Struktur & Laporan")
tab1, tab2, tab3 = st.tabs(["📏 Kalkulator", "📊 Visualisasi", "📚 Referensi"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Data Balok")
        L = st.slider("Bentang Balok (m)", 1.0, 15.0, 5.0)
        kondisi = st.selectbox("Tipe Tumpuan", ["Sederhana (L/16)", "Satu Ujung Menerus (L/18.5)", "Dua Ujung Menerus (L/21)", "Kantilever (L/8)"])
        
        map_kondisi = {"Sederhana (L/16)": 16, "Satu Ujung Menerus (L/18.5)": 18.5, "Dua Ujung Menerus (L/21)": 21, "Kantilever (L/8)": 8}
        h_f = int(((L * 1000) / map_kondisi[kondisi] // 50 + 1) * 50)
        b_f = int((h_f * 0.5 // 25 + 1) * 25)
        
    with col2:
        st.subheader("Data Kolom")
        lantai = st.number_input("Jumlah Lantai", 1, 10, 1)
        luas_lantai = st.number_input("Area per Kolom (m2)", 1.0, 100.0, 20.0)
        pu = lantai * luas_lantai * 12 # 12 kN/m2 asumsi beban terfaktor
        sisi = int((((pu * 1000) / (0.3 * 25))**0.5 // 50 + 1) * 50)
        if sisi < 150: sisi = 150

    st.divider()
    
    # Tombol Download
    pdf_data = create_pdf(b_f, h_f, L, pu, sisi)
    st.download_button(
        label="📥 Download Laporan Hasil (PDF)",
        data=pdf_data,
        file_name="Laporan_Struktur.pdf",
        mime="application/pdf"
    )

with tab2:
    # (Kode visualisasi Matplotlib seperti sebelumnya diletakkan di sini)
    c_viz1, c_viz2 = st.columns(2)
    with c_viz1:
        st.write(f"Potongan Balok {b_f}x{h_f}")
        fig1, ax1 = plt.subplots(figsize=(3,4))
        ax1.add_patch(patches.Rectangle((0,0), b_f, h_f, color='gray', alpha=0.3))
        st.pyplot(fig1)
    with c_viz2:
        st.write(f"Potongan Kolom {sisi}x{sisi}")
        fig2, ax2 = plt.subplots(figsize=(3,4))
        ax2.add_patch(patches.Rectangle((0,0), sisi, sisi, color='blue', alpha=0.1))
        st.pyplot(fig2)

with tab3:
    st.info("Referensi: SNI 2847:2019 & SNI 1727:2020")
