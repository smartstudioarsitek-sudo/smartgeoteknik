import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIG ---
st.set_page_config(page_title="GeoTeknik Pro", layout="wide")
st.title("🚜 Aplikasi Analisis Geoteknik Terpadu")
st.caption("SmartStudio Engineering | Gravity Wall | Cantilever Wall | Slope Stability")

# --- MENU UTAMA ---
mode = st.sidebar.radio("Pilih Mode Analisis:", 
    ["1. Dinding Gravitasi (Batu Kali)", "2. Dinding Kantilever (Beton)", "3. Stabilitas Talud (Slope)"])

# ==============================================================================
# MODE 1: DINDING GRAVITASI (BATU KALI) - FULL VERSION
# ==============================================================================
if mode == "1. Dinding Gravitasi (Batu Kali)":
    st.subheader("Analisis Dinding Penahan Tanah (Tipe Gravitasi)")
    
    # --- INPUT ---
    with st.sidebar:
        st.header("1. Geometri Dinding")
        H = st.number_input("Tinggi Dinding (H) [m]", 4.0, step=0.1)
        B_top = st.number_input("Lebar Atas (a) [m]", 0.5, step=0.1)
        B_bot = st.number_input("Lebar Bawah (b) [m]", 2.5, step=0.1)
        
        st.header("2. Parameter Tanah & Air")
        h_water = st.slider("Tinggi Muka Air (hw) [m]", 0.0, H, 1.0, step=0.1)
        gamma_concrete = st.number_input("Berat Jenis Beton (kN/m3)", 24.0)
        gamma_soil = st.number_input("Berat Jenis Tanah (kN/m3)", 18.0)
        gamma_water = 9.81
        
        st.header("3. Koefisien")
        phi = st.slider("Sudut Geser Dalam (Phi)", 20, 45, 30)
        mu = st.number_input("Koefisien Gesek Dasar", 0.5)

    # --- PERHITUNGAN ---
    # 1. Berat Dinding
    Vol_1 = B_top * H
    Vol_2 = 0.5 * (B_bot - B_top) * H
    W_wall = (Vol_1 + Vol_2) * gamma_concrete

    # Lengan Momen Tahan
    x1 = (B_bot - B_top) + (B_top / 2)
    x2 = (2/3) * (B_bot - B_top)
    Momen_Tahan = (Vol_1 * gamma_concrete * x1) + (Vol_2 * gamma_concrete * x2)

    # 2. Tekanan Tanah & Air
    phi_rad = np.radians(phi)
    Ka = (np.tan(np.radians(45) - (phi_rad / 2)))**2
    Pa_soil = 0.5 * gamma_soil * (H**2) * Ka
    Ma_soil = Pa_soil * (H / 3)
    
    Pw_water = 0.5 * gamma_water * (h_water**2)
    Ma_water = Pw_water * (h_water / 3)

    P_total = Pa_soil + Pw_water
    Momen_Guling = Ma_soil + Ma_water

    # 3. Safety Factors
    SF_Guling = Momen_Tahan / Momen_Guling if Momen_Guling > 0 else 999
    SF_Geser = (W_wall * mu) / P_total if P_total > 0 else 999

    # --- VISUALISASI ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Total Gaya Dorong", f"{P_total:.2f} kN")
        st.write(f"**SF Guling:** {SF_Guling:.2f} " + ("✅" if SF_Guling >= 1.5 else "❌"))
        st.write(f"**SF Geser:** {SF_Geser:.2f} " + ("✅" if SF_Geser >= 1.5 else "❌"))

    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        # Dinding
        wall_coords = [(0, 0), (B_bot, 0), (B_bot, H), (B_bot - B_top, H), (0, 0)]
        ax.add_patch(patches.Polygon(wall_coords, closed=True, facecolor='gray', edgecolor='black'))
        # Tanah & Air
        ax.fill([B_bot, B_bot+3, B_bot+3, B_bot], [0, 0, H, H], color='#e67e22', alpha=0.3)
        if h_water > 0:
            ax.fill([B_bot, B_bot+3, B_bot+3, B_bot], [0, 0, h_water, h_water], color='blue', alpha=0.4)
        
        ax.set_xlim(-1, B_bot + 4)
        ax.set_ylim(-1, H + 1)
        ax.set_aspect('equal')
        st.pyplot(fig)

# ==============================================================================
# MODE 2: DINDING KANTILEVER (BETON)
# ==============================================================================
elif mode == "2. Dinding Kantilever (Beton)":
    st.subheader("Analisis Dinding Penahan Tanah (Tipe Kantilever)")
    
    with st.sidebar:
        st.header("Dimensi Kantilever")
        H = st.number_input("Tinggi Total (H) [m]", 4.0)
        h_slab = st.number_input("Tebal Pelat Dasar [m]", 0.4)
        b_stem = st.number_input("Tebal Dinding (Stem) [m]", 0.3)
        b_toe = st.number_input("Panjang Kaki Depan (Toe) [m]", 0.8)
        b_heel = st.number_input("Panjang Kaki Belakang (Heel) [m]", 1.5)
        
        st.header("Material")
        gamma_c = 24.0
        gamma_s = st.number_input("Berat Isi Tanah [kN/m3]", 18.0)
        phi = st.slider("Sudut Geser (Phi)", 20, 45, 30)
        
    # --- HITUNGAN ---
    B_total = b_toe + b_stem + b_heel
    W_stem = (H - h_slab) * b_stem * gamma_c
    W_base = B_total * h_slab * gamma_c
    W_soil = (H - h_slab) * b_heel * gamma_s # Tanah di atas Heel
    
    # Momen Tahan (Titik guling di ujung Toe)
    x_stem = b_toe + (b_stem/2)
    x_base = B_total / 2
    x_soil = b_toe + b_stem + (b_heel/2)
    
    Mr = (W_stem * x_stem) + (W_base * x_base) + (W_soil * x_soil)
    
    # Gaya Guling
    Ka = np.tan(np.radians(45 - phi/2))**2
    Pa = 0.5 * gamma_s * (H**2) * Ka
    Mo = Pa * (H/3)
    
    SF_Guling = Mr / Mo if Mo > 0 else 999
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Momen Tahan", f"{Mr:.2f} kNm")
        st.metric("Momen Guling", f"{Mo:.2f} kNm")
        st.write(f"**SF Guling: {SF_Guling:.2f}** " + ("✅" if SF_Guling >= 1.5 else "❌"))

    with col2:
        fig, ax = plt.subplots()
        ax.add_patch(patches.Rectangle((0, 0), B_total, h_slab, fc='gray', ec='black')) # Base
        ax.add_patch(patches.Rectangle((b_toe, h_slab), b_stem, H-h_slab, fc='gray', ec='black')) # Stem
        ax.add_patch(patches.Rectangle((b_toe+b_stem, h_slab), b_heel, H-h_slab, fc='orange', alpha=0.3)) # Tanah
        ax.set_xlim(-1, B_total+1); ax.set_ylim(-1, H+1); ax.set_aspect('equal')
        st.pyplot(fig)

# ==============================================================================
# MODE 3: STABILITAS TALUD (SLOPE)
# ==============================================================================
elif mode == "3. Stabilitas Talud (Slope)":
    st.subheader("Analisis Stabilitas Talud (Estimasi Fellenius)")
    
    with st.sidebar:
        H_slope = st.number_input("Tinggi Talud (H) [m]", 5.0)
        S_slope = st.number_input("Kemiringan (1:z)", 1.0)
        c = st.number_input("Kohesi (c) [kN/m2]", 5.0)
        phi_s = st.slider("Phi Tanah", 10, 45, 25)
        gamma = st.number_input("Gamma [kN/m3]", 18.0)
        R = st.slider("Jari-jari Longsor (R)", H_slope, H_slope*3, H_slope*1.5)

    # --- VISUALISASI ---
    x_crest = H_slope * S_slope
    coords_x = [-5, 0, x_crest, x_crest+5]
    coords_y = [0, 0, H_slope, H_slope]
    
    # Asumsi Pusat Lingkaran (Sederhana)
    center_x = x_crest / 2
    center_y = H_slope + (R**2 - (x_crest/2)**2)**0.5
    
    # Hitungan Kasar
    alpha = 60 # Derajat sektor
    L_arc = (alpha/360) * 2 * np.pi * R
    W_mass = ((alpha/360) * np.pi * R**2 * 0.3) * gamma
    
    Resisting = (c * L_arc) + (W_mass * np.cos(np.radians(30)) * np.tan(np.radians(phi_s)))
    Driving = W_mass * np.sin(np.radians(30))
    SF_approx = Resisting / Driving if Driving > 0 else 0
    
    st.write(f"**Estimasi SF (Simplified): {SF_approx:.2f}**")
    
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(coords_x, coords_y, 'k-', linewidth=2)
    ax.fill_between(coords_x, coords_y, -5, color='#8D6E63', alpha=0.5)
    circle = patches.Circle((center_x, center_y), R, edgecolor='r', facecolor='none', linestyle='--')
    ax.add_patch(circle)
    ax.set_ylim(-2, center_y + R/2); ax.set_aspect('equal')
    st.pyplot(fig)
