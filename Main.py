import streamlit as st

# 1. Konfigurasi Halaman Dasar
st.set_page_config(
    page_title="MONTANA System", 
    layout="centered", 
    initial_sidebar_state="expanded" # Dipaksa terbuka agar user HP tidak bingung
)

# --- CSS GLOBAL: LOGIN & UI ---
image_url = "https://storage.googleapis.com/pkg-portal-bucket/images/PG_website1_Kantor-Pusat-Petrokimia-Gresik.jpeg"

# Perhatikan penggunaan {{ dan }} di bawah ini
final_style = f"""
    <style>
    .stAppHeader {{ visibility: hidden; }}
    
    /* BACKGROUND IMAGE */
    .stApp {{
        background-image: url("{image_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* JUDUL UTAMA (MONTANA MPB) */
    .main-title {{
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-size: 3.8rem !important;
        font-weight: 850 !important;
        color: #002D62 !important; 
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin-bottom: 0px;
        text-shadow: 2px 2px 8px rgba(255, 255, 255, 0.8);
    }}
    
    /* SUB-DESKRIPSI */
    .sub-title {{
        color: #002D62 !important;
        text-align: center;
        font-weight: 700;
        font-size: 1.2rem;
        margin-top: -10px;
        margin-bottom: 30px;
        text-shadow: 1px 1px 5px rgba(255, 255, 255, 0.6);
    }}

    /* KOTAK LOGIN TRANSPARAN */
    [data-testid="stForm"] {{
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(20px) !important;
        padding: 40px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2) !important;
        max-width: 450px !important;
        margin: auto !important;
    }}

    /* INPUT TEXT LABEL */
    [data-testid="stForm"] label {{
        color: #002D62 !important;
        font-weight: bold;
    }}
    </style>
"""

# Inisialisasi Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 1. HALAMAN LOGIN ---
if not st.session_state.logged_in:
    st.markdown(final_style, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Judul & Sub-judul dengan CSS Baru
    st.markdown('<p class="main-title">MONTANA MPB</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Monitoring Analitik Tagihan Internal MPB</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.1, 1, 0.1])
    with col2:
        with st.form("login_form"):
            user = st.text_input("Username", placeholder="Masukkan username")
            pwd = st.text_input("Password", type="password", placeholder="Masukkan password")
            submitted = st.form_submit_button("MASUK SISTEM", use_container_width=True)
            
            if submitted:
                # Login Admin
                if user == "admin" and pwd == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.role = "ADMIN"
                    st.rerun()
                # Login Unit
                elif user == "unit" and pwd == "unit123":
                    st.session_state.logged_in = True
                    st.session_state.role = "UNIT"
                    st.rerun()
                else:
                    st.error("Kredensial salah!")
                    
    st.markdown("""
        <p style='text-align: center; color: white; font-weight: bold; opacity: 0.9; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);'>
            developed by AlkaNa Budi @ 2026<br>
            PT Petrokimia Gresik
        </p>
    """, unsafe_allow_html=True)

# --- 2. HALAMAN SETELAH LOGIN ---
else:
    # Sidebar Security & Navigation
    pg_dash  = st.Page("views/02_Dashboard.py", title="Dashboard", icon="🏠")
    pg_tren  = st.Page("views/03_Analisis_Tren.py", title="Analisis Tren", icon="📈")
    pg_input = st.Page("views/01_Input_Data.py", title="Input Data", icon="➕")
    pg_hist  = st.Page("views/04_History.py", title="History Penerimaan", icon="📜")
    pg_proc  = st.Page("views/05_Tagihan_Proses.py", title="Tagihan Proses", icon="📑")

    if st.session_state.role == "ADMIN":
        menu = {
            "Monitoring": [pg_dash, pg_tren, pg_hist, pg_proc],
            "Transaksi": [pg_input]
        }
    else:
        # Menu untuk Unit (Hanya Input & Lihat Proses)
        menu = {"Layanan Unit": [pg_input, pg_proc]}

    pg = st.navigation(menu, position="sidebar")

    # Sidebar Header & Logout
    with st.sidebar:
        st.markdown(f"### 👤 Role: {st.session_state.role}")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.messages = []
            st.rerun()
        st.divider()

    # JALANKAN HALAMAN UTAMA (VIEWS)
    pg.run()

    # --- 3. WIDGET CHATBOT MONTANA AI (FLOATING) ---
    with st.sidebar:
        st.markdown("---")
        with st.expander("💬 Tanya Montana (AI)", expanded=False):
            st.caption("Asisten SOP MPB")
            
            # Chat Interface
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Tanya prosedur..."):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                from utils import get_montana_chat_response
                with st.chat_message("assistant"):
                    with st.spinner("Membaca data..."):
                        response = get_montana_chat_response(prompt)
                        st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})