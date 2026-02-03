import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Konfigurasi Halaman
st.set_page_config(page_title="CivilCalc Pro", layout="wide")

# --- JUDUL & TABS ---
st.title("🏗️ CivilCalc Pro: Visualisator Struktur")
tab1, tab2, tab3 = st.tabs(["📏 Balok & Tulangan", "🧱 Kolom", "📚 Sumber & Referensi"])

# --- TAB 1: BALOK ---
with tab1:
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.subheader("Parameter Balok")
        L = st.slider("Panjang Bentang (m)", 1.0, 15.0, 5.0)
        kondisi = st.selectbox("Tipe Tumpuan", 
                              ["Sederhana (L/16)", "Satu Ujung Menerus (L/18.5)", "Dua Ujung Menerus (L/21)", "Kantilever (L/8)"])
        
        # Logika SNI 2847:2019
        map_kondisi = {"Sederhana (L/16)": 16, "Satu Ujung Menerus (L/18.5)": 18.5, "Dua Ujung Menerus (L/21)": 21, "Kantilever (L/8)": 8}
        h_f = int(((L * 1000) / map_kondisi[kondisi] // 50 + 1) * 50)
        b_f = int((h_f * 0.5 // 25 + 1) * 25)
        
        st.success(f"Rekomendasi: **{b_f} x {h_f} mm**")

    with col2:
        st.subheader("Visualisasi Penampang Balok")
        fig, ax = plt.subplots(figsize=(4, 5))
        # Gambar Beton
        rect = patches.Rectangle((0, 0), b_f, h_f, linewidth=2, edgecolor='black', facecolor='#d3d3d3')
        ax.add_patch(rect)
        # Gambar Tulangan (Asumsi sederhana 4 baris)
        cover = 40 # Selimut beton 40mm
        ax.scatter([cover, b_f-cover, cover, b_f-cover], [cover, cover, h_f-cover, h_f-cover], color='red', s=100, label='Besi Tulangan')
        
        plt.xlim(-50, b_f + 50)
        plt.ylim(-50, h_f + 50)
        plt.title(f"Potongan Balok {b_f}x{h_f}")
        st.pyplot(fig)

# --- TAB 2: KOLOM ---
with tab2:
    col_a, col_b = st.columns([1, 1.5])
    
    with col_a:
        st.subheader("Estimasi Beban Kolom")
        lantai = st.number_input("Jumlah Lantai", 1, 10, 2)
        luas = st.number_input("Luas Area Lantai per Kolom (m²)", 1.0, 100.0, 20.0)
        beban = 12 # kN/m2 (Beban hidup+mati terfaktor rata-rata)
        
        pu = lantai * luas * beban
        # Sisi kolom (Ag = Pu / 0.3fc') dengan fc' default 25
        sisi = int((((pu * 1000) / (0.3 * 25))**0.5 // 50 + 1) * 50)
        if sisi < 150: sisi = 150

        st.metric("Total Beban (Pu)", f"{pu} kN")
        st.info(f"Dimensi Kolom: **{sisi} x {sisi} mm**")

    with col_b:
        st.subheader("Visualisasi Kolom")
        fig2, ax2 = plt.subplots()
        rect_col = patches.Rectangle((0, 0), sisi, sisi, linewidth=2, edgecolor='blue', facecolor='#e0e0e0')
        ax2.add_patch(rect_col)
        # Tulangan sengkang sederhana
        ax2.add_patch(patches.Rectangle((30,30), sisi-60, sisi-60, fill=False, linestyle='--', color='gray'))
        
        plt.xlim(-50, sisi + 50)
        plt.ylim(-50, sisi + 50)
        st.pyplot(fig2)

# --- TAB 3: REFERENSI ---
with tab3:
    st.markdown("""
    ### Dasar Perhitungan:
    1. **SNI 2847:2019**: Tabel 9.3.1.1 untuk *Tinggi Minimum Balok Non-Pratekan*.
    2. **SNI 1727:2020**: Penentuan kombinasi beban terfaktor.
    3. **Asumsi Praktis**: Lebar balok $b = 0.5 \times h$. Dimensi kolom dihitung berdasarkan kapasitas tekan aksial beton tanpa memperhitungkan momen (Kolom Pendek).
    """)
