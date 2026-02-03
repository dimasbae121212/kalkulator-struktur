import streamlit as st

# Pengaturan halaman
st.set_page_config(page_title="CivilCalc SNI", page_icon="🏗️", layout="wide")

# Gaya CSS khusus agar lebih menarik
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ CivilCalc: Struktur Beton Bertulang")
st.markdown("Aplikasi perhitungan dimensi dan penulangan berdasarkan **SNI 2847:2019** & **SNI 1727:2020**.")

# Tab Menu agar interaktif
tab1, tab2, tab3 = st.tabs(["📏 Balok & Tulangan", "🧱 Kolom", "📚 Sumber Referensi"])

with tab1:
    st.header("Perhitungan Balok")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("Input Data")
        L = st.number_input("Panjang Bentang (m)", min_value=1.0, value=5.0, key="L_balok")
        kondisi = st.selectbox("Kondisi Tumpuan", 
                              ["Sederhana (L/16)", "Satu Ujung Menerus (L/18.5)", 
                               "Dua Ujung Menerus (L/21)", "Kantilever (L/8)"], key="cond_balok")
        fy = st.number_input("Mutu Baja/Fy (MPa)", value=420) # Standar SNI terbaru
        fc = st.number_input("Mutu Beton/Fc' (MPa)", value=25)

    # Logika Dimensi
    map_kondisi = {"Sederhana (L/16)": 16, "Satu Ujung Menerus (L/18.5)": 18.5, "Dua Ujung Menerus (L/21)": 21, "Kantilever (L/8)": 8}
    h_min = (L * 1000) / map_kondisi[kondisi]
    h_f = int((h_min // 50 + 1) * 50)
    b_f = int((h_f * 0.5 // 25 + 1) * 25)

    with c2:
        st.subheader("Hasil Estimasi")
        st.metric("Tinggi Balok (h)", f"{h_f} mm")
        st.metric("Lebar Balok (b)", f"{b_f} mm")
        
        # Estimasi Tulangan Sederhana (Rasio 1% - 1.5% luas penampang)
        luas_tulangan = 0.01 * b_f * h_f
        st.write(f"**Estimasi Luas Tulangan Tarik:** {luas_tulangan:.2 eye} mm²")
        st.caption("Gunakan 3D16 atau 4D16 berdasarkan kebutuhan luas di atas.")

with tab2:
    st.header("Perhitungan Kolom")
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Beban Terpusat")
        n_lantai = st.number_input("Jumlah Lantai", min_value=1, value=1)
        area_beban = st.number_input("Luas Area yang Dipikul (m²)", value=25.0, help="Contoh: Jika kolom menahan plat 5x5m, isi 25")
        beban_unit = st.number_input("Estimasi Beban per m² (kN/m²)", value=12.0, help="Beban mati + hidup terfaktor")
        
        pu = n_lantai * area_beban * beban_unit # Total beban aksial terfaktor

    with col_b:
        st.subheader("Dimensi Kolom")
        # Rumus praktis kolom pendek: Ag = Pu / (0.3 * fc')
        ag_req = (pu * 1000) / (0.3 * fc)
        sisi_kolom = int((ag_req**0.5 // 50 + 1) * 50)
        if sisi_kolom < 150: sisi_kolom = 150 # Minimum praktis
        
        st.metric("Total Beban Aksial (Pu)", f"{pu:.2f} kN")
        st.metric("Dimensi Kolom Rekomendasi", f"{sisi_kolom} x {sisi_kolom} mm")
        
        # Tulangan Kolom (SNI: 1% - 8% dari Ag)
        ast_min = 0.01 * (sisi_kolom**2)
        st.write(f"**Luas Tulangan Utama (1%):** {ast_min:.2f} mm²")

with tab3:
    st.header("Referensi Perhitungan")
    st.markdown("""
    Perhitungan dalam aplikasi ini mengacu pada standar nasional Indonesia terbaru:
    1.  **SNI 2847:2019**: Persyaratan Beton Struktural untuk Bangunan Gedung (Tabel 9.3.1.1 untuk tebal minimum balok).
    2.  **SNI 1727:2020**: Beban Desain Minimum dan Kriteria Terkait untuk Bangunan Gedung (Kombinasi beban $1.2D + 1.6L$).
    3.  **Pedoman Perencanaan Pembebanan untuk Rumah dan Gedung (PPPURG 1987)**: Untuk estimasi beban mati komponen bangunan.
    
    *Disclaimer: Hasil aplikasi ini adalah untuk keperluan edukasi dan estimasi awal. Untuk konstruksi nyata, konsultasikan dengan ahli struktur bersertifikat.*
    """)
