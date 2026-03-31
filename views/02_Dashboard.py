import streamlit as st
import pandas as pd
from utils import get_data_from_google, get_data_mpb_2025

# 1. Konfigurasi Layout & CSS
st.markdown("<style>.block-container {max-width: 95% !important; padding-top: 2rem;}</style>", unsafe_allow_html=True)

st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #4da3ff; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; 
        white-space: pre-wrap; 
        background-color: #1e1e1e; 
        border-radius: 5px; 
        color: white; 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏠 Dashboard Ringkasan Performa MPB")

try:
    # --- 1. AMBIL DATA ---
    df_raw_base = get_data_from_google()
    df_proc_base = get_data_mpb_2025()

    # --- 2. CEK DATA KOSONG (PAGAR PENGAMAN) ---
    if df_raw_base.empty:
        st.warning("⚠️ Data Penerimaan di Google Sheets masih kosong.")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Penerimaan", "0 Memo")
        m2.metric("Total Proses", "0 Memo")
        st.stop()

    # Bersihkan data dari None/NaN agar tampilan cantik
    df_raw = df_raw_base.fillna("")
    df_proc = df_proc_base.fillna("")

    # --- 3. METRIK KPI UTAMA ---
    st.markdown("### 📊 Ringkasan Performa Keseluruhan")
    m1, m2, m3, m4 = st.columns(4)
    
    count_raw = len(df_raw)
    count_proc = len(df_proc)
    
    nom_hist = df_raw["NOMINAL TAGIHAN"].sum() if "NOMINAL TAGIHAN" in df_raw.columns else 0
    nom_proc = df_proc["Nilai Tagihan"].sum() if "Nilai Tagihan" in df_proc.columns else 0

    with m1:
        st.metric("Total Penerimaan", f"{count_raw} Memo")
    with m2:
        st.metric("Total Proses", f"{count_proc} Memo")
    with m3:
        st.metric("Nilai Penerimaan", f"Rp {nom_hist:,.0f}".replace(",", "."))
    with m4:
        st.metric("Nilai Proses", f"Rp {nom_proc:,.0f}".replace(",", "."))

    st.divider()

    # --- 4. TABEL RINGKASAN TRANSAKSI TERAKHIR ---
    st.markdown("### 🕒 Transaksi Terkini")
    tab_h, tab_p = st.tabs(["📌 5 Transaksi Terakhir (Penerimaan)", "📄 5 Transaksi Terakhir (Proses)"])

    with tab_h:
        # Filter data dummy jika ada
        clean_h = df_raw[df_raw.iloc[:, 1] != "Belum Ada Data"].copy()
        
        if not clean_h.empty:
            # Sorting berdasarkan kolom pertama (Waktu)
            col_waktu = clean_h.columns[0]
            clean_h['sort_key'] = pd.to_datetime(clean_h[col_waktu], errors='coerce')
            
            # Ambil 5 terbaru
            latest_h = clean_h.sort_values(by='sort_key', ascending=False).head(5)
            latest_h = latest_h.drop(columns=['sort_key'])

            st.dataframe(latest_h, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada transaksi penerimaan.")

    with tab_p:
        if not df_proc.empty:
            clean_p = df_proc.copy()
            # Gunakan kolom tanggal dokumen untuk sorting
            col_tgl_proc = "Tanggal Dokumen Masuk Akuntansi"
            if col_tgl_proc in clean_p.columns:
                clean_p['sort_key'] = pd.to_datetime(clean_p[col_tgl_proc], errors='coerce')
                latest_p = clean_p.sort_values(by='sort_key', ascending=False).head(5)
                latest_p = latest_p.drop(columns=['sort_key'])
            else:
                latest_p = clean_p.tail(5)
                
            st.dataframe(latest_p, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada transaksi proses SAP.")

except Exception as e:
    st.error(f"Terjadi kesalahan teknis pada Dashboard: {str(e)}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)