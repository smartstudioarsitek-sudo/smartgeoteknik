import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIG ---
st.set_page_config(page_title="GeoTeknik Pro", layout="wide")
st.title("🚜 Aplikasi Analisis Geoteknik Terpadu")
st.caption("Gravity Wall | Cantilever Wall | Slope Stability")

# --- MENU UTAMA ---
mode = st.sidebar.radio("Pilih Mode Analisis:", 
    ["1. Dinding Gravitasi (Gravity)", "2. Dinding Kantilever (Beton)", "3. Stabilitas Talud (Slope)"])

# =========================================
# MODE 1: DINDING GRAVITASI (Code Lama)
# =========================================
if mode == "1. Dinding Gravitasi (Gravity)":
    st.subheader("Analisis Dinding Penahan Tanah (Tipe Gravitasi)")
    # ... (Gunakan kode Gravity Wall yang sebelumnya Kakak punya di sini) ...
    # Agar hemat tempat, saya persingkat teks ini. 
    # Kakak bisa copy-paste logika perhitungan 'dinding_air.py' kemarin ke sini.
    st.info("💡 Gunakan kode dari 'dinding_air.py' yang sudah sukses kemarin untuk bagian ini.")

# =========================================
# MODE 2: DINDING KANTILEVER (BETON)
# =========================================
elif mode == "2. Dinding Kantilever (Beton)":
    st.subheader("Analisis Dinding Penahan Tanah (Tipe Kantilever)")
    
    with st.sidebar:
        st.header("Dimensi Kantilever")
        H = st.number_input("Tinggi Total (H) [m]", 4.0)
        h_slab = st.number_input("Tebal Pelat Dasar (h_slab) [m]", 0.4)
        b_stem = st.number_input("Tebal Dinding (Stem) [m]", 0.3)
        b_toe = st.number_input("Panjang Kaki Depan (Toe) [m]", 0.8)
        b_heel = st.number_input("Panjang Kaki Belakang (Heel) [m]", 1.5)
        
        st.header("Material")
        gamma_c = 24.0 # Beton
        gamma_s = st.number_input("Berat Isi Tanah (Gamma) [kN/m3]", 18.0)
        phi = st.slider("Sudut Geser (Phi)", 20, 45, 30)
        
    # --- HITUNGAN KANTILEVER ---
    # Lebar total
    B_total = b_toe + b_stem + b_heel
    
    # 1. Berat Sendiri (Beton)
    W_stem = (H - h_slab) * b_stem * gamma_c
    W_base = B_total * h_slab * gamma_c
    
    # 2. Berat Tanah di atas Heel (Penstabil Utama!)
    W_soil = (H - h_slab) * b_heel * gamma_s
    
    Total_Vertikal = W_stem + W_base + W_soil
    
    # Momen Tahan (Terhadap Ujung Toe / Titik O)
    # Lengan momen:
    x_stem = b_toe + (b_stem/2)
    x_base = B_total / 2
    x_soil = b_toe + b_stem + (b_heel/2)
    
    Mr = (W_stem * x_stem) + (W_base * x_base) + (W_soil * x_soil)
    
    # 3. Tekanan Tanah Aktif (Rankine)
    Ka = np.tan(np.radians(45 - phi/2))**2
    Pa = 0.5 * gamma_s * (H**2) * Ka
    Mo = Pa * (H/3) # Momen Guling
    
    # Safety Factor
    SF_Guling = Mr / Mo if Mo > 0 else 999
    
    # Output
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Total Berat Penahan", f"{Total_Vertikal:.2f} kN")
        st.metric("Gaya Dorong (Pa)", f"{Pa:.2f} kN")
        st.write(f"**SF Guling: {SF_Guling:.2f}**")
        if SF_Guling < 1.5: st.error("TIDAK AMAN") 
        else: st.success("AMAN")

    with col2:
        # Visualisasi Sederhana Kantilever
        fig, ax = plt.subplots()
        # Gambar Base
        ax.add_patch(patches.Rectangle((0, 0), B_total, h_slab, fc='gray', ec='black'))
        # Gambar Stem
        ax.add_patch(patches.Rectangle((b_toe, h_slab), b_stem, H-h_slab, fc='gray', ec='black'))
        # Gambar Tanah Urug
        ax.add_patch(patches.Rectangle((b_toe+b_stem, h_slab), b_heel, H-h_slab, fc='orange', alpha=0.3, label='Tanah Urug'))
        
        ax.set_xlim(-1, B_total+1)
        ax.set_ylim(-1, H+1)
        ax.set_aspect('equal')
        st.pyplot(fig)

# =========================================
# MODE 3: STABILITAS TALUD (SLOPE STABILITY)
# =========================================
elif mode == "3. Stabilitas Talud (Slope)":
    st.subheader("Analisis Stabilitas Talud (Metode Fellenius Sederhana)")
    st.caption("Simulasi Bidang Longsor Lingkaran (Circular Slip)")
    
    with st.sidebar:
        st.header("Geometri Talud")
        H_slope = st.number_input("Tinggi Talud (H) [m]", 5.0)
        S_slope = st.number_input("Kemiringan (1:z)", 1.0, help="Misal 1:1, masukkan 1")
        
        st.header("Tanah")
        c = st.number_input("Kohesi (c) [kN/m2]", 5.0)
        phi_s = st.slider("Phi Tanah", 10, 45, 25)
        gamma = st.number_input("Gamma [kN/m3]", 18.0)
        
        st.header("Bidang Longsor (Trial)")
        R = st.slider("Jari-jari Bidang Longsor (R)", H_slope, H_slope*3, H_slope*1.5)
        
    # --- VISUALISASI & HITUNGAN SIMPEL ---
    # Koordinat Talud
    # (0,0) di kaki talud (toe)
    x_crest = H_slope * S_slope
    coords_x = [-5, 0, x_crest, x_crest+5]
    coords_y = [0, 0, H_slope, H_slope]
    
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(coords_x, coords_y, 'k-', linewidth=2, label="Permukaan Tanah")
    ax.fill_between(coords_x, coords_y, -5, color='#8D6E63', alpha=0.5)
    
    # Gambar Lingkaran Longsor (Asumsi pusat lingkaran tegak lurus tengah lereng agar simpel)
    # User bisa menggeser pusat lingkaran sebenarnya, tapi untuk demo kita fix dulu
    center_x = x_crest / 2
    center_y = H_slope + (R**2 - (x_crest/2)**2)**0.5 # Hitung Y agar lingkaran pas kena toe (approx)
    
    # Gambar Busur (Arc)
    theta = np.linspace(180, 360, 100) # Full circle range dummy
    # Logic plotting arc sederhana
    circle = patches.Circle((center_x, center_y), R, edgecolor='r', facecolor='none', linestyle='--', label='Bidang Longsor')
    ax.add_patch(circle)
    
    # Hitungan Kasar Fellenius (Hanya Estimasi untuk Demo)
    # SF = (c.L + W.cos.tan) / W.sin
    # Kita asumsikan panjang busur (L) dan berat (W) dari geometri kasar
    
    # Sudut juring (approximate)
    alpha = 60 # Derajat (asumsi sektor longsor)
    L_arc = (alpha/360) * 2 * np.pi * R
    Area_slice = (alpha/360) * np.pi * R**2 * 0.3 # Faktor koreksi luas segmen (kasar)
    W_mass = Area_slice * gamma
    
    # Gaya Penahan
    Resisting = (c * L_arc) + (W_mass * np.cos(np.radians(30)) * np.tan(np.radians(phi_s)))
    # Gaya Penggerak
    Driving = W_mass * np.sin(np.radians(30))
    
    SF_approx = Resisting / Driving if Driving > 0 else 0
    
    st.write(f"**Estimasi SF (Simplified): {SF_approx:.2f}**")
    st.info("Catatan: Ini adalah hitungan simulasi. Untuk hasil akurat, diperlukan iterasi metode irisan (slices) yang membagi tanah menjadi pias-pias kecil.")
    
    ax.plot(center_x, center_y, 'rx', markersize=10, label="Pusat Rotasi")
    ax.set_ylim(-2, center_y + R + 2)
    ax.set_xlim(-5, x_crest + 10)
    ax.set_aspect('equal')
    ax.legend()
    st.pyplot(fig)