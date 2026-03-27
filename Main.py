import streamlit as st

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="MONTANA System", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# --- CSS UNTUK LOGIN CLEAN ---
hide_elements = """
    <style>
    .stAppHeader {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Box Login Putih */
    div[data-testid="stVerticalBlock"] > div:has(input) {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    .stTextInput label { color: #1e293b !important; font-weight: bold; }
    h2, p { color: #1e293b !important; }
    
    /* Sembunyikan border form standar Streamlit agar lebih clean */
    [data-testid="stForm"] {
        border: none;
        padding: 0;
    }
    </style>
"""

# Inisialisasi Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# --- HALAMAN LOGIN ---
if not st.session_state.logged_in:
    st.markdown(hide_elements, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    
    with col2:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/785/785116.png", width=70) 
        st.markdown("<h2 style='margin-bottom:0;'>MONTANA MPB</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.8em; margin-bottom:20px;'>Monitoring Analitik Tagihan Internal MPB</p>", unsafe_allow_html=True)
        
        # --- IMPLEMENTASI FORM UNTUK FITUR ENTER ---
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="Masukkan username")
            pwd = st.text_input("Password", type="password", placeholder="Masukkan password")
            
            # Gunakan form_submit_button agar Enter berfungsi
            submitted = st.form_submit_button("MASUK SISTEM", use_container_width=True, type="primary")
            
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
        
        st.markdown("<p style='text-align: center; font-size: 0.7em; margin-top: 20px; color: #64748b;'>developed by Alkana</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- SISTEM NAVIGASI (SETELAH LOGIN) ---
else:
    # Suntikkan CSS WIDE LAYOUT
    st.markdown("""
        <style>
        .appview-container .main .block-container {
            max-width: 95% !important;
            padding-top: 1rem !important;
            padding-right: 1rem !important;
            padding-left: 1rem !important;
        }
        .stAppHeader {visibility: visible !important;}
        [data-testid="stSidebar"] {display: flex !important;}
        </style>
    """, unsafe_allow_html=True)

    # Definisi Halaman
    pg_dash  = st.Page("views/02_Dashboard.py", title="Dashboard", icon="🏠")
    pg_tren  = st.Page("views/03_Analisis_Tren.py", title="Analisis Tren", icon="📈")
    pg_input = st.Page("views/01_Input_Data.py", title="Input Data", icon="➕")
    pg_hist  = st.Page("views/04_History.py", title="History Penerimaan", icon="📜")
    pg_proc  = st.Page("views/05_Tagihan_Proses.py", title="Tagihan Proses", icon="📑")

    # Routing Role
    if st.session_state.role == "ADMIN":
        menu = {
            "Monitoring": [pg_dash, pg_tren, pg_hist, pg_proc],
            "Transaksi": [pg_input]
        }
    else:
        menu = {"Layanan": [pg_input, pg_proc]}

    # Jalankan Navigasi
    pg = st.navigation(menu, position="sidebar")
    
    with st.sidebar:
        st.write(f"Logged in as: **{st.session_state.role}**")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.rerun()
        st.divider()

    pg.run()