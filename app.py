import streamlit as st
from engine import StructuralEngine
from constants import DATA_TEKNIS
from fpdf import FPDF

st.set_page_config(page_title="SNI Structural Suite", layout="wide")

st.sidebar.title("🛠️ Parameter Utama")
peruntukan = st.sidebar.selectbox("Peruntukan Struktur", ["Balok Utama", "Balok Anak", "Ring Balok", "Kantilever", "Kolom"])
bentang = st.sidebar.number_input("Lebar Antar Kolom / Bentang (m)", 1.0, 20.0, 4.0)
n_lantai = st.sidebar.number_input("Jumlah Lantai", 1, 50, 1)
t_lantai = st.sidebar.number_input("Tinggi Tiap Lantai (m)", 2.0, 5.0, 3.5)

c1, c2 = st.columns(2)
with c1:
    mutu_beton = st.selectbox("Mutu Beton", list(DATA_TEKNIS["BETON"].keys()), index=3)
    mutu_baja = st.selectbox("Mutu Baja Utama", list(DATA_TEKNIS["BAJA"].keys()), index=1)
with c2:
    jenis_dinding = st.selectbox("Jenis Dinding", list(DATA_TEKNIS["BEBAN_MATI"].keys())[:2])
    gempa = st.select_slider("Wilayah Gempa", options=["Rendah", "Sedang", "Tinggi"])

if st.button("RUN ANALISIS KOMPLEKS"):
    input_data = {
        "peruntukan": peruntukan, "bentang": bentang, "n_lantai": n_lantai,
        "t_dinding": t_lantai, "mutu_beton": mutu_beton, "mutu_baja": mutu_baja,
        "jenis_dinding": jenis_dinding, "fungsi": "Lantai Hunian", "gempa": gempa
    }

    if peruntukan == "Kolom":
        res = StructuralEngine.analisis_kolom(input_data)
        st.subheader(f"Rekomendasi Kolom: {res['sisi']}x{res['sisi']} mm")
        st.write(f"Tulangan Utama: **{res['n_col']} D16**")
    else:
        res = StructuralEngine.analisis_balok(input_data)
        st.header(f"Hasil Analisis {peruntukan}")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Dimensi Beton", f"{res['b']} x {res['h']} mm")
        k2.metric("Tulangan Utama", f"{res['n_main']} D{res['d_main']}")
        k3.metric("Sengkang Beugel", f"ø8 - {res['sengkang']} mm")

        # --- BAGIAN PERHITUNGAN PALING BAWAH ---
        st.markdown("---")
        st.subheader("📝 Detail Logika & Rumus Perhitungan")
        st.latex(r"Q_u = 1.2 D + 1.6 L")
        st.write(f"Beban Merata Terfaktor: {res['qu']:.2f} kN/m")
        st.latex(r"M_u = \frac{1}{8} \cdot Q_u \cdot L^2")
        st.write(f"Momen Maksimum: {res['mu']:.2f} kNm")
        st.latex(r"A_s = \rho \cdot b \cdot d")
        st.write(f"Luas Tulangan Tarik Perlu: {res['as']:.2f} mm²")

        # --- PDF GENERATOR ---
        class PDF(FPDF):
            def header(self):
                self.set_font('Courier', 'B', 12)
                self.cell(0, 10, 'ENGINEERING CALCULATION REPORT - SNI STANDARDS', 0, 1, 'C')
                self.ln(5)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Courier", size=11)
        
        lines = [
            f"Project: Structural Analysis",
            f"Element: {peruntukan}",
            f"L-Span: {bentang} m | Floors: {n_lantai}",
            "-"*50,
            f"Concrete: {mutu_beton} | Steel: {mutu_baja}",
            f"Seismic Zone: {gempa}",
            "-"*50,
            f"ANALYSIS RESULTS:",
            f"Beam Dimension: {res['b']} x {res['h']} mm",
            f"Main Rebar: {res['n_main']} D{res['d_main']}",
            f"Stirrup: 8 mm @ {res['sengkang']} mm",
            "-"*50,
            f"INTERNAL FORCES:",
            f"Ultimate Load (Qu): {res['qu']:.2f} kN/m",
            f"Ultimate Moment (Mu): {res['mu']:.2f} kNm",
            f"Shear Force (Vu): {res['vu']:.2f} kN"
        ]
        
        for line in lines:
            pdf.cell(0, 8, line, ln=True)

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 DOWNLOAD PROFESSIONAL REPORT", pdf_bytes, "Report_SNI.pdf")
