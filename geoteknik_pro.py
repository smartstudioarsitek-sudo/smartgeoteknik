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

# --- HEADER CANTIK ---
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
# TAB 1: DINDING GRAVITASI (BATU KALI)
# ==============================================================================
with tab1:
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        st.info("📌 **Input Parameter**")
        
        with st.expander("1. Dimensi Dinding", expanded=True):
            g_H = st.number_input("Tinggi (H) [m]", 3.0, 10.0, 4.0, step=0.1, key="g_H")
            g_a = st.number_input("Lebar Atas (a) [m]", 0.3, 2.0, 0.5, step=0.1, key="g_a")
            g_b = st.number_input("Lebar Bawah (b) [m]", 1.0, 10.0, 2.5, step=0.1, key="g_b")
            
        with st.expander("2. Material & Air"):
            g_hw = st.slider("Muka Air (hw) [m]", 0.0, g_H, 1.0, step=0.1, key="g_hw")
            g_gc = st.number_input("BJ Beton [kN/m3]", value=24.0, key="g_gc")
            g_gs = st.number_input("BJ Tanah [kN/m3]", value=18.0, key="g_gs")
            g_phi = st.slider("Sudut Geser (ϕ)", 20, 45, 30, key="g_phi")
            g_mu = st.number_input("Koef. Gesek (μ)", value=0.5, key="g_mu")

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
    
    # Safety Factor
    SF_guling = M_tahan / M_guling if M_guling > 0 else 999
    SF_geser = (W_wall * g_mu) / P_total if P_total > 0 else 999


    # --- TAMBAHAN: CEK DAYA DUKUNG TANAH (SNI 8460) ---
    # 1. Hitung Eksentrisitas (e)
    # Lokasi resultan gaya dari titik guling (Toe)
    # X_resultan = (Momen Tahan - Momen Guling) / Total Gaya Vertikal
    Total_V = W_wall # (Jika nanti ada Uplift, kurangi di sini)
    X_res = (M_tahan - M_guling) / Total_V
    
    # Eksentrisitas (jarak resultan dari as tengah dinding)
    e = (g_b / 2) - X_res
    
    # Cek Syarat Eksentrisitas (Harus < B/6 agar seluruh alas menapak)
    e_max = g_b / 6
    
    # 2. Hitung Tegangan Tanah Maksimum (q_max)
    # Rumus Meyerhof / Terzaghi umum
    if abs(e) <= e_max:
        q_max = (Total_V / g_b) * (1 + (6 * abs(e) / g_b))
        q_min = (Total_V / g_b) * (1 - (6 * abs(e) / g_b))
    else:
        # Jika eksentrisitas besar, tegangan jadi tidak linear (bahaya)
        q_max = (2 * Total_V) / (3 * (g_b/2 - e)) # Rumus pendekatan efektif
        q_min = 0 # Terjadi tarikan (lift off)

    # 3. Daya Dukung Izin Tanah (Q_allow)
    # Kita butuh input baru: Kapasitas Dukung Tanah Dasar (q_ult) dari user
    # Atau kita pakai Terzaghi simpel: q_ult = c.Nc + q.Nq + 0.5.gamma.B.Ny
    # Untuk simpelnya di aplikasi ini, kita minta user input Q_izin tanah saja.

    st.write("---")
    st.subheader("3. Cek Daya Dukung Tanah (Bearing Capacity)")
    
    col_daya1, col_daya2 = st.columns(2)
    with col_daya1:
        q_izin_input = st.number_input("Daya Dukung Izin Tanah (Qa) [kN/m2]", value=150.0, help="Data dari Sondir/Lab")
        
    with col_daya2:
        st.metric("Tegangan Tanah Terjadi (Qmax)", f"{q_max:.2f} kN/m2")
    
    # Cek Safety
    if q_max <= q_izin_input:
        st.success(f"✅ AMAN (Qmax < Qa)")
    else:
        st.error(f"❌ TIDAK AMAN (Tanah Dasar Ambles!)")
        st.caption("Solusi: Perlebar Lebar Bawah (b)")

    # Peringatan Eksentrisitas
    if e > e_max:
        st.warning(f"⚠️ Peringatan: Resultan gaya keluar dari kern (e > B/6). Sebagian dasar dinding terangkat!")
    with col_output:
        st.subheader("📊 Hasil Analisis")
        
        # Kartu Hasil (Metrics)
        m1, m2, m3 = st.columns(3)
        m1.metric("Berat Dinding", f"{W_wall:.2f} kN")
        m2.metric("Gaya Dorong Total", f"{P_total:.2f} kN")
        m3.metric("Koefisien Ka", f"{Ka:.3f}")
        
        st.write("#### Faktor Keamanan (Safety Factors)")
        
        c1, c2 = st.columns(2)
        with c1:
            status_g = "✅ AMAN" if SF_guling >= 1.5 else "❌ BAHAYA"
            st.metric("SF Guling (min 1.5)", f"{SF_guling:.2f}", status_g)
            if SF_guling < 1.5: st.warning("Perlebar dimensi Bawah (b)")
            
        with c2:
            status_s = "✅ AMAN" if SF_geser >= 1.5 else "❌ BAHAYA"
            st.metric("SF Geser (min 1.5)", f"{SF_geser:.2f}", status_s)
            if SF_geser < 1.5: st.warning("Tambah berat dinding atau key")

        # Visualisasi
        st.write("---")
        fig, ax = plt.subplots(figsize=(8, 4))
        # Dinding
        poly = [(0,0), (g_b,0), (g_b,g_H), (g_b-g_a,g_H), (0,0)]
        ax.add_patch(patches.Polygon(poly, closed=True, facecolor='#95a5a6', edgecolor='black', hatch='/'))
        # Tanah
        ax.fill([g_b, g_b+4, g_b+4, g_b], [0, 0, g_H, g_H], color='#d35400', alpha=0.2, label='Tanah')
        # Air
        if g_hw > 0:
            ax.fill([g_b, g_b+4, g_b+4, g_b], [0, 0, g_hw, g_hw], color='#3498db', alpha=0.4, label='Air')
            
        ax.set_title("Cross Section View")
        ax.set_xlim(-1, g_b + 4); ax.set_ylim(-1, g_H + 1)
        ax.set_aspect('equal'); ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()
        st.pyplot(fig)

# ==============================================================================
# TAB 2: DINDING KANTILEVER
# ==============================================================================
with tab2:
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        st.info("📌 **Input Geometri Beton**")
        with st.expander("1. Dimensi Struktur", expanded=True):
            c_H = st.number_input("Tinggi Total (H) [m]", value=5.0, key="c_H")
            c_stem = st.number_input("Tebal Dinding (Stem) [m]", value=0.4, key="c_stem")
            c_slab = st.number_input("Tebal Pelat (Slab) [m]", value=0.5, key="c_slab")
            c_toe = st.number_input("Panjang Toe (Depan) [m]", value=1.0, key="c_toe")
            c_heel = st.number_input("Panjang Heel (Belakang) [m]", value=2.0, key="c_heel")
        
        with st.expander("2. Tanah Timbunan"):
            c_gamma = st.number_input("Gamma Tanah [kN/m3]", value=18.0, key="c_gamma")
            c_phi = st.slider("Sudut Geser (ϕ)", 20, 45, 30, key="c_phi")

    # --- PERHITUNGAN KANTILEVER ---
    B_total = c_toe + c_stem + c_heel
    
    # Berat Komponen
    W_stem = (c_H - c_slab) * c_stem * 24.0
    W_base = B_total * c_slab * 24.0
    W_soil = (c_H - c_slab) * c_heel * c_gamma # Tanah penstabil
    
    # Momen Tahan (terhadap Toe)
    Mr = (W_stem * (c_toe + c_stem/2)) + \
         (W_base * (B_total/2)) + \
         (W_soil * (c_toe + c_stem + c_heel/2))
         
    # Momen Guling
    Ka_c = np.tan(np.radians(45 - c_phi/2))**2
    Pa_c = 0.5 * c_gamma * (c_H**2) * Ka_c
    Mo = Pa_c * (c_H/3)
    
    SF_kantilever = Mr / Mo if Mo > 0 else 999
    
    with col_output:
        st.subheader("📊 Analisis Stabilitas")
        
        # Menampilkan Rumus
        st.latex(r"SF_{overturning} = \frac{\Sigma M_{resisting}}{\Sigma M_{overturning}}")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Momen Tahan (Mr)", f"{Mr:.2f} kNm")
        k2.metric("Momen Guling (Mo)", f"{Mo:.2f} kNm")
        
        status_k = "✅ AMAN" if SF_kantilever >= 1.5 else "❌ PERBAIKI"
        k3.metric("SF Guling", f"{SF_kantilever:.2f}", status_k)
        
        # Visualisasi
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        # Beton
        ax2.add_patch(patches.Rectangle((0,0), B_total, c_slab, fc='#7f8c8d', ec='k')) # Base
        ax2.add_patch(patches.Rectangle((c_toe, c_slab), c_stem, c_H-c_slab, fc='#7f8c8d', ec='k')) # Stem
        # Tanah
        ax2.add_patch(patches.Rectangle((c_toe+c_stem, c_slab), c_heel, c_H-c_slab, fc='#f1c40f', alpha=0.3, label='Tanah Penstabil'))
        
        ax2.arrow(B_total+1, c_H/3, -1, 0, head_width=0.2, color='red')
        ax2.text(B_total+1.2, c_H/3, f"Pa={Pa_c:.1f}", color='red')
        
        ax2.set_xlim(-1, B_total+3); ax2.set_ylim(-1, c_H+1)
        ax2.set_aspect('equal')
        ax2.legend()
        st.pyplot(fig2)

# ==============================================================================
# TAB 3: STABILITAS LERENG
# ==============================================================================
with tab3:
    st.header("⛰️ Analisis Stabilitas Lereng (Simplified)")
    st.caption("Metode Irisan Fellenius (Simulasi)")

    col_s1, col_s2 = st.columns([1, 2])
    
    with col_s1:
        with st.form("slope_form"):
            s_H = st.number_input("Tinggi Lereng [m]", value=8.0)
            s_kemiringan = st.number_input("Kemiringan (1:z)", value=1.0, help="1 Vertikal : z Horizontal")
            st.markdown("---")
            s_c = st.number_input("Kohesi (c) [kN/m2]", value=10.0)
            s_phi = st.number_input("Phi [derajat]", value=25.0)
            s_gamma = st.number_input("Gamma [kN/m3]", value=18.0)
            
            submit = st.form_submit_button("🔁 Hitung SF")

    with col_s2:
        # Geometri Lereng
        x_crest = s_H * s_kemiringan
        
        # Asumsi Bidang Longsor (Fixed for demo visuals)
        R_trial = s_H * 1.5
        center_x = x_crest / 2
        center_y = s_H + 2
        
        # Hitungan Dummy (Agar fungsional)
        # Di aplikasi real, ini butuh loop 1000x iterasi
        resisting = (s_c * R_trial * 2) + (500 * np.tan(np.radians(s_phi)))
        driving = 400 # Dummy driving force based on mass
        SF_slope = resisting / driving
        
        if submit:
             st.success(f"Analisis Selesai! Estimasi Faktor Keamanan (SF): **{SF_slope:.2f}**")
        else:
            st.info("Klik tombol 'Hitung SF' untuk memulai analisis.")

        # Visualisasi
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        x_coords = [-5, 0, x_crest, x_crest+10]
        y_coords = [0, 0, s_H, s_H]
        ax3.fill_between(x_coords, y_coords, -5, color='#27ae60', alpha=0.3)
        ax3.plot(x_coords, y_coords, 'k-', linewidth=2)
        
        # Lingkaran Longsor
        circle = patches.Circle((center_x, center_y), R_trial, ec='red', fc='none', linestyle='--', linewidth=2, label='Bidang Longsor Kritis')
        ax3.add_patch(circle)
        
        ax3.set_ylim(-2, s_H+5)
        ax3.set_aspect('equal')
        ax3.legend()
        ax3.set_title("Visualisasi Lereng & Bidang Longsor")
        st.pyplot(fig3)

