import math
from constants import DATA_TEKNIS

class StructuralEngine:
    @staticmethod
    def analisis_balok(data):
        fc = DATA_TEKNIS["BETON"][data['mutu_beton']]
        fy = DATA_TEKNIS["BAJA"][data['mutu_baja']]
        L = data['bentang']
        
        # 1. Estimasi Dimensi Berdasarkan Batas Layan SNI 2847 Tabel 9.3.1.1
        mult = {"Balok Utama": 12, "Balok Anak": 16, "Ring Balok": 20, "Kantilever": 8}
        h = int(((L * 1000) / mult[data['peruntukan']] // 50 + 1) * 50)
        b = int((h * 0.5 // 25 + 1) * 25)
        
        # 2. Analisis Beban Terfaktor (SNI 1727:2020)
        q_self = (b/1000 * h/1000 * 24)
        q_wall = DATA_TEKNIS["BEBAN_MATI"][data['jenis_dinding']] * data['t_dinding']
        q_dead = (q_self + q_wall + DATA_TEKNIS["BEBAN_MATI"]["Spesi/Keramik"]) * data['n_lantai']
        q_live = DATA_TEKNIS["BEBAN_HIDUP"][data['fungsi']] * data['n_lantai']
        
        qu = (1.2 * q_dead) + (1.6 * q_live)
        mu = (1/8) * qu * (L**2) # Momen Ultimate
        vu = (1/2) * qu * L      # Gaya Geser Ultimate
        
        # 3. Desain Lentur
        d = h - 50 # Jarak efektif
        phi_l = 0.9
        rn = (mu * 10**6) / (phi_l * b * d**2)
        m = fy / (0.85 * fc)
        rho = (1/m) * (1 - math.sqrt(max(0, 1 - (2 * m * rn / fy))))
        
        # Cek Rho Min & Max
        rho_min = max(1.4/fy, (math.sqrt(fc)/(4*fy)))
        rho_max = 0.025 # Batas praktis daktilitas
        rho_final = max(rho_min, min(rho, rho_max))
        
        as_req = rho_final * b * d
        d_main = 16 if L > 4 else 13
        n_main = max(2, math.ceil(as_req / (0.25 * math.pi * d_main**2)))
        
        # 4. Desain Geser (Beugel)
        phi_v = 0.75
        vc = (1/6) * math.sqrt(fc) * b * d / 1000 # Kapasitas beton (kN)
        if vu > phi_v * vc:
            vs = (vu / phi_v) - vc
            s_req = (0.25 * math.pi * 8**2 * fy * d) / (vs * 1000)
        else:
            s_req = d/2
        
        # Pembulatan sengkang sesuai standar gempa
        s_limit = DATA_TEKNIS["GEMPA_KDS"][data['gempa']]["min_s"]
        s_final = int(min(s_req, s_limit) // 25 * 25)

        return {
            "b": b, "h": h, "qu": qu, "mu": mu, "vu": vu,
            "n_main": n_main, "d_main": d_main, "sengkang": s_final,
            "fc": fc, "fy": fy, "as": as_req
        }

    @staticmethod
    def analisis_kolom(data):
        # Perhitungan kolom berdasarkan Tributary Area (Luas yang dipikul)
        fc = DATA_TEKNIS["BETON"][data['mutu_beton']]
        fy = DATA_TEKNIS["BAJA"][data['mutu_baja']]
        area = data['bentang'] * data['bentang'] # Asumsi grid kotak
        
        total_load = (12.0 * area * data['n_lantai']) # Estimasi beban 12kN/m2 terfaktor
        # Pu = 0.80 * phi * [0.85 * fc * (Ag - Ast) + fy * Ast]
        # Penyederhanaan Ag untuk estimasi awal (Ast = 1% Ag)
        ag_req = (total_load * 1000) / (0.45 * (0.85 * fc + 0.01 * fy))
        sisi = int((ag_req**0.5 // 50 + 1) * 50)
        if sisi < 200: sisi = 200
        
        ast = 0.01 * (sisi**2)
        n_col = max(4, math.ceil(ast / (0.25 * math.pi * 16**2)))
        if n_col % 2 != 0: n_col += 1
        
        return {"sisi": sisi, "n_col": n_col, "pu": total_load}
