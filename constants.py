# SNI 2847:2019 & SNI 1727:2020 & SNI 1726:2019
DATA_TEKNIS = {
    "BETON": {
        "K-175": 14.5, "K-200": 16.6, "K-225": 18.7, 
        "K-250": 20.8, "K-300": 24.9, "K-350": 29.1, "K-400": 33.2
    },
    "BAJA": {
        "Polos (BjTP 280)": 280,
        "Ulir (BjTS 420)": 420
    },
    "BEBAN_HIDUP": {
        "Lantai Hunian": 1.92,
        "Lantai Kantor": 2.40,
        "Lantai Sekolah": 2.40,
        "Gudang Berat": 6.00,
        "Atap Dak": 0.96
    },
    "BEBAN_MATI": {
        "Bata Merah": 2.50,    # kN/m2 per meter tinggi
        "Bata Ringan": 0.75,   # kN/m2 per meter tinggi
        "Spesi/Keramik": 1.10, # kN/m2
        "Plafon/ME": 0.20       # kN/m2
    },
    "GEMPA_KDS": {
        "Rendah": {"rho_s": 0.01, "phi_v": 0.75, "min_s": 200},
        "Sedang": {"rho_s": 0.012, "phi_v": 0.75, "min_s": 150},
        "Tinggi": {"rho_s": 0.015, "phi_v": 0.75, "min_s": 100}
    }
}
