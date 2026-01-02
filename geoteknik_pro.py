import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- CONFIG HALAMAN ---
st.set_page_config(
    page_title="GeoTeknik SmartStudio",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS ---
st.markdown("""
    <style>
    .main-title {font-size: 2.5rem; color: #2c3e50; font-weight: bold;}
    .sub-title {font-size: 1.2rem; color: #7f8c8d;}
    .stMetric {background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #e9ecef;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏗️ SmartStudio Geo-Engineer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Integrated Geotechnical Analysis System (KP-01 & SNI)</div>', unsafe_allow_html=True)
st.markdown("---")

# --- MENU NAVIGASI (TABS) ---
tab1, tab2, tab3 = st.tabs(["🧱 Dinding Gravitasi", "🏢 Dinding Kantilever", "⛰️ Stabilitas Lereng"])

# ==============================================================================
# TAB 1: DINDING GRAVITASI (BATU KALI) - UPDATED
# ==============================================================================
with tab1:
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        st.info("📌 **Input Parameter**")
        
        with st.expander("1. Dimensi Dinding", expanded=True):
            g_H = st.number_input("Tinggi Total (H) [m]", 3.0, 10.0, 4.0, step=0.1)
            g_a = st.number_input("Lebar Atas (a) [m]", 0.3, 2.0, 0.5, step=0.1)
            g_b = st.number_input("Lebar Bawah (b) [m]", 1.0, 10.0, 2.5, step=0.1)
            
        with st.expander("2. Tanah Urug (Backfill)"):
            st.caption("Tanah di belakang dinding")
            g_gs = st.number_input("Berat Isi Tanah (γ) [kN/m3]", value=18.0)
            g_phi = st.slider("Sudut Geser (ϕ) Urugan", 20, 45, 30)
            g_hw = st.slider("Tinggi Muka Air (hw) [m]", 0.0, g_H, 1.0, step=0.1)

        with st.expander("3. Tanah Asli (Pondasi)", expanded=True):
            st.caption("Tanah di bawah dinding")
            g_qa = st.number_input("Daya Dukung Izin (Qa) [kN/m2]", value=150.0, help="Dari data Sondir/Lab")
            g_mu = st.number_input("Koef. Gesek Dasar (μ)", value=0.5, help="Biasanya tan(phi) tanah dasar")
            g_gc = st.number_input("Berat Jenis Dinding [kN/m3]", value=24.0)

    # --- PERHITUNGAN GRAVITASI ---
    # Hitung Berat
    Vol_1 = g_a * g_H
    Vol_2 = 0.5 * (g_b - g_a) * g_H
    W_wall = (Vol_1 + Vol_2) * g_gc
    
    # Momen Tahan
    x1 = (g_b - g_a) + (g_a / 2)
    x2 = (2/3) * (g_b - g_a)
    M_tahan = (Vol_1 * g_gc * x1) + (Vol_2 * g_gc * x2)
    
    # Gaya Dorong (Rankine)
    Ka = np.tan(np.radians(45 - g_phi/2))**2
    Pa = 0.5 * g_gs * (g_H**2) * Ka
    Pw = 0.5 * 9.81 * (g_hw**2)
    P_total = Pa + Pw
    
    # Momen Guling
    M_guling = (Pa * g_H/3) + (Pw * g_hw/3)
    
    # Safety Factor (Guling & Geser)
    SF_guling = M_tahan / M_guling if M_guling > 0 else 999
    SF_geser = (W_wall * g_mu) / P_total if P_total > 0 else 999

    # Cek Daya Dukung (Eksentrisitas)
    X_res = (M_tahan - M_guling) / W_wall
    e = (g_b / 2) - X_res
    q_max = (W_wall / g_b) * (1 + (6 * abs(e) / g_b))

    with col_output:
        st.subheader("📊 Hasil Analisis Visual")
        
        # Kartu Hasil
        c1, c2, c3 = st.columns(3)
        
        # SF Guling
        stat_g = "✅ AMAN" if SF_guling >= 1.5 else "❌ BAHAYA"
        c1.metric("SF Guling", f"{SF_guling:.2f}", stat_g)
        
        # SF Geser
        stat_s = "✅ AMAN" if SF_geser >= 1.5 else "❌ BAHAYA"
        c2.metric("SF Geser", f"{SF_geser:.2f}", stat_s)
        
        # Daya Dukung
        stat_d = "✅ AMAN" if q_max <= g_qa else "❌ AMBLES"
        c3.metric(f"Qmax (< {g_qa})", f"{q_max:.2f}", stat_d, help="Tegangan tanah maksimum yang terjadi di dasar")

        # Visualisasi Plot
        st.write("---")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 1. TANAH ASLI (FOUNDATION) - Baru!
        # Menggambar kotak cokelat tua di bawah y=0
        ax.add_patch(patches.Rectangle((-2, -3), g_b + 6, 3, facecolor='#5d4037', alpha=0.8, label='Tanah Asli (Keras)'))
        ax.text(g_b/2, -1.5, "Tanah Dasar / Pondasi", color='white', ha='center', fontweight='bold')
        
        # 2. DINDING
        poly = [(0,0), (g_b,0), (g_b,g_H), (g_b-g_a,g_H), (0,0)]
        ax.add_patch(patches.Polygon(poly, closed=True, facecolor='#95a5a6', edgecolor='black', hatch='//', label='Dinding'))
        
        # 3. TANAH URUG (BACKFILL)
        ax.fill([g_b, g_b+4, g_b+4, g_b], [0, 0, g_H, g_H], color='#f39c12', alpha=0.3, label='Tanah Urug')
        
        # 4. AIR
        if g_hw > 0:
            ax.fill([g_b, g_b+4, g_b+4, g_b], [0, 0, g_hw, g_hw], color='#3498db', alpha=0.4, label='Muka Air')

        # Garis Tanah
        ax.hlines(0, -2, g_b+4, colors='black', linestyles='-', linewidth=2)
        
        # Anotasi Gaya
        ax.arrow(g_b+2, g_H/3, -1, 0, head_width=0.2, color='red')
        ax.text(g_b+2.2, g_H/3, f"P_total\n{P_total:.1f} kN", color='red')

        ax.set_title("Cross Section View (Penampang Melintang)")
        ax.set_xlim(-2, g_b + 4)
        ax.set_ylim(-3, g_H + 1) # Y-limit diperluas ke bawah biar tanah asli kelihatan
        ax.set_aspect('equal')
        ax.legend(loc='upper left')
        ax.grid(True, linestyle=':', alpha=0.5)
        
        st.pyplot(fig)

# ==============================================================================
# TAB 2: DINDING KANTILEVER (TETAP)
# ==============================================================================
with tab2:
    st.info("💡 Mode Kantilever (Kode tetap sama seperti sebelumnya)")
    # (Kode disederhanakan untuk jawaban ini agar fokus ke Tab 1, 
    # TAPI SAAT KAKAK COPY, PASTIKAN KODE KANTILEVER SEBELUMNYA TETAP ADA DI SINI)
    # Gunakan kode kantilever dari jawaban sebelumnya jika ingin lengkap.
    # Biar tidak error, saya taruh placeholder visual saja di sini.
    st.write("Silakan gunakan modul Gravity Wall yang sudah di-update.")

# ==============================================================================
# TAB 3: STABILITAS LERENG (TETAP)
# ==============================================================================
with tab3:
    st.write("Modul Stabilitas Lereng")
    # (Sama, bagian ini tidak berubah)
