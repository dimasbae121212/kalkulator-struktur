import streamlit as st

st.set_page_config(page_title="SNI Beam Calculator", page_icon="🏗️")

st.title("🏗️ Kalkulator Struktur Balok SNI")
st.markdown("---")

# Bagian 1: Dimensi Geometri
st.header("1. Dimensi & Properti")
col1, col2 = st.columns(2)

with col1:
    L = st.number_input("Panjang Bentang (m)", min_value=1.0, value=5.0)
    kondisi = st.selectbox("Kondisi Tumpuan", 
                          ["Sederhana (L/16)", "Satu Ujung Menerus (L/18.5)", 
                           "Dua Ujung Menerus (L/21)", "Kantilever (L/8)"])

# Logika SNI 2847:2019 untuk h_min
map_kondisi = {"Sederhana (L/16)": 16, "Satu Ujung Menerus (L/18.5)": 18.5, 
               "Dua Ujung Menerus (L/21)": 21, "Kantilever (L/8)": 8}
h_min = (L * 1000) / map_kondisi[kondisi]
h_final = int((h_min // 50 + 1) * 50) # Pembulatan ke atas per 50mm
b_final = int((h_final * 0.5 // 25 + 1) * 25) # Lebar setengah tinggi

with col2:
    st.info(f"**Hasil Estimasi Dimensi:**\nTinggi (h): {h_final} mm\nLebar (b): {b_final} mm")

# Bagian 2: Analisa Beban Sederhana (SNI 1727:2020)
st.header("2. Analisa Beban Rencana")
q_dead = st.number_input("Beban Mati / Dead Load (kN/m)", value=10.0)
q_live = st.number_input("Beban Hidup / Live Load (kN/m)", value=5.0)

# Kombinasi Beban U = 1.2D + 1.6L
qu = (1.2 * q_dead) + (1.6 * q_live)
st.warning(f"Beban Terfaktor (Qu): **{qu:.2f} kN/m**")

# Bagian 3: Output Momen Maksimum
st.header("3. Gaya Dalam (Momen)")
mu = (1/8) * qu * (L**2)
st.success(f"Momen Maksimum Terfaktor (Mu): **{mu:.2f} kNm**")

st.caption("Catatan: Gunakan hasil ini sebagai referensi awal. Perhitungan penulangan detail tetap diperlukan.")