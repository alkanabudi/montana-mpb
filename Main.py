import streamlit as st

# 1. Konfigurasi Halaman Dasar
st.set_page_config(
    page_title="MONTANA System", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- CSS GLOBAL: LOGIN & CHATBOT UI ---
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
        font-family: 'Segoe UI', Roboto, sans-serif;
        font-size: 3.5rem !important;
        font-weight: 850 !important;
        color: #FFFFFF !important;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 5px;
        text-shadow: 3px 3px 10px rgba(0,0,0,0.8);
    }}
    
    /* KOTAK LOGIN TRANSPARAN */
    [data-testid="stForm"] {{
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(15px) !important;
        padding: 45px !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
        max-width: 500px !important;
        margin: auto !important;
    }}

    /* STYLE KHUSUS EXPANDER CHATBOT AGAR TERLIHAT FLOATING */
    .stExpander {{
        border: 1px solid #0284c7 !important;
        border-radius: 15px !important;
        background-color: white !important;
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
    st.markdown('<p class="main-title">MONTANA MPB</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:white; text-align:center; font-weight:600;">Monitoring Analitik Tagihan Internal MPB</p>', unsafe_allow_html=True)
    
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
    st.markdown("<p style='text-align: center; color: white; opacity: 0.8;'>developed by Alkana @ 2026<br>PT Petrokimia Gresik</p>", unsafe_allow_html=True)

# --- 2. HALAMAN SETELAH LOGIN ---
else:
    # Pengaturan Sidebar & Security per Role
    if st.session_state.role == "UNIT":
        st.markdown("<style>[data-testid='stSidebar'] {display: flex !important;} #MainMenu, header {visibility: hidden;}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>[data-testid='stSidebar'] {display: flex !important;}</style>", unsafe_allow_html=True)

    # Definisi Halaman (Routing)
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
        menu = {"Layanan": [pg_input, pg_proc]}

    pg = st.navigation(menu, position="sidebar")

    # Logout Button di Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.role}")
        if st.button("🚪 Keluar Sistem", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.role = None
            st.session_state.messages = [] # Reset chat saat logout
            st.rerun()
        st.divider()

    # JALANKAN HALAMAN UTAMA
    pg.run()

    # --- 3. WIDGET CHATBOT MONTANA AI (FLOATING) ---
    # Widget ini ditaruh di bawah pg.run() agar selalu muncul di setiap halaman
    st.markdown("---")
    with st.expander("💬 Tanya Montana (AI Assistant)", expanded=False):
        st.caption("Tanyakan tentang aturan, SOP, atau prosedur MPB")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input Chat
        if prompt := st.chat_input("Apa yang ingin Anda tanyakan?"):
            # Tampilkan pesan user
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Panggil fungsi AI dari utils
            from utils import get_montana_chat_response
            with st.chat_message("assistant"):
                with st.spinner("Montana sedang membaca SOP..."):
                    response = get_montana_chat_response(prompt)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})