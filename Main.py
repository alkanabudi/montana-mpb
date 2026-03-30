import streamlit as st

# 1. Konfigurasi Halaman Dasar
st.set_page_config(
    page_title="MONTANA System", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS REVISI FINAL: TYPOGRAPHY BOLD & CLEAN ---
image_url = "https://storage.googleapis.com/pkg-portal-bucket/images/PG_website1_Kantor-Pusat-Petrokimia-Gresik.jpeg"

final_style = f"""
    <style>
    .stAppHeader {{ visibility: hidden; }}
    
    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* JUDUL UTAMA (MONTANA MPB) */
    .main-title {{
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        font-size: 3.5rem !important;
        font-weight: 850 !important;
        color: #FFFFFF !important;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin-bottom: 0px;
        text-shadow: 3px 3px 10px rgba(0,0,0,0.8);
    }}
    
    /* SUB-JUDUL (GELAP & TAJAM) */
    .sub-title {{
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        text-align: center;
        letter-spacing: 1px;
        margin-top: -10px;
        margin-bottom: 40px;
        text-shadow: 0px 0px 8px rgba(255,255,255,0.8);
    }}

    /* KOTAK LOGIN TRANSPARAN */
    [data-testid="stForm"] {{
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        padding: 45px !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
        max-width: 500px !important;
        margin: auto !important;
    }}

    .stTextInput label {{
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-bottom: 8px;
    }}

    .stButton>button {{
        background-color: #0284c7 !important;
        color: white !important;
        font-weight: 700 !important;
        height: 50px !important;
        border-radius: 12px !important;
        border: none !important;
        margin-top: 15px !important;
    }}

    /* Sembunyikan Navigasi & Sidebar saat Login */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {{ display: none; }}
    </style>
"""

# Inisialisasi Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# --- HALAMAN LOGIN ---
if not st.session_state.logged_in:
    st.markdown(final_style, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Judul & Subjudul
    st.markdown('<p class="main-title">MONTANA MPB</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Monitoring Analitik Tagihan Internal MPB</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.1, 1, 0.1])
    
    with col2:
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="Masukkan username")
            pwd = st.text_input("Password", type="password", placeholder="Masukkan password")
            submitted = st.form_submit_button("MASUK SISTEM", use_container_width=True)
            
            if submitted:
                if user == "admin" and pwd == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.role = "ADMIN"
                    st.rerun()
                elif user == "unit" and pwd == "unit123":
                    st.session_state.logged_in = True
                    st.session_state.role = "UNIT"
                    st.rerun()
                else:
                    st.error("Kredensial salah!")

    st.markdown("<p style='text-align: center; font-size: 0.8em; margin-top: 50px; color: white; opacity: 0.8; text-shadow: 1px 1px 2px black;'>developed by Alkana @ 2026<br>PT Petrokimia Gresik</p>", unsafe_allow_html=True)


else:
    # --- JURUS SECURITY: SEMBUNYIKAN TOTAL UNTUK UNIT ---
    if st.session_state.role == "UNIT":
        st.markdown("""
            <style>
            #MainMenu, header, footer, .stAppDeployButton, [data-testid="stStatusWidget"], #manage-app-button, button[title="View source on GitHub"] {
                visibility: hidden !important; display: none !important;
            }
            .appview-container .main .block-container {
                max-width: 95% !important; padding-top: 1rem !important;
            }
            [data-testid="stSidebar"] {display: flex !important;}
            </style>
        """, unsafe_allow_html=True)
    else:
        # Style khusus ADMIN
        st.markdown("""
            <style>
            .appview-container .main .block-container {
                max-width: 95% !important; padding-top: 1rem !important;
            }
            .stAppHeader {visibility: visible !important;}
            [data-testid="stSidebar"] {display: flex !important;}
            .stAppDeployButton {display:none;}
            </style>
        """, unsafe_allow_html=True)

    # 1. Definisi Halaman (Pastikan file-file ini ada di folder views)
    pg_dash  = st.Page("views/02_Dashboard.py", title="Dashboard", icon="🏠")
    pg_tren  = st.Page("views/03_Analisis_Tren.py", title="Analisis Tren", icon="📈")
    pg_input = st.Page("views/01_Input_Data.py", title="Input Data", icon="➕")
    pg_hist  = st.Page("views/04_History.py", title="History Penerimaan", icon="📜")
    pg_proc  = st.Page("views/05_Tagihan_Proses.py", title="Tagihan Proses", icon="📑")

    # 2. Routing berdasarkan Role
    if st.session_state.role == "ADMIN":
        menu = {
            "Monitoring": [pg_dash, pg_tren, pg_hist, pg_proc],
            "Transaksi": [pg_input]
        }
    else:
        # Role UNIT hanya bisa input dan lihat proses
        menu = {"Layanan": [pg_input, pg_proc]}

    # 3. Inisialisasi Navigasi
    pg = st.navigation(menu, position="sidebar")
    
    # 4. Tampilkan Sidebar Custom (Logout Button)
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.role}")
        st.write(f"Logged in as: **{st.session_state.role}**")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()
        st.divider()

    # 5. JALANKAN HALAMAN (PENTING: Tanpa ini, halaman tidak akan muncul)
    pg.run()
