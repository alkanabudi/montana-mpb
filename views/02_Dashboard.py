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
    df_raw = get_data_from_google()
    df_proc = get_data_mpb_2025()

    # --- 2. PRE-PROCESSING WAKTU ---
    col_tgl_hist = df_raw.columns[0]
    df_raw[col_tgl_hist] = pd.to_datetime(df_raw[col_tgl_hist], errors='coerce')
    
    col_tgl_proc = "Tanggal Dokumen Masuk Akuntansi"
    if not df_proc.empty and col_tgl_proc in df_proc.columns:
        df_proc[col_tgl_proc] = pd.to_datetime(df_proc[col_tgl_proc], errors='coerce')

    # --- 3. METRIK KPI UTAMA ---
    st.markdown("### 📊 Ringkasan Performa Keseluruhan")
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Total Penerimaan", f"{len(df_raw)} Memo")
    
    with m2:
        st.metric("Total Proses", f"{len(df_proc)} Memo")
    
    with m3:
        if "NOMINAL TAGIHAN" in df_raw.columns:
            df_raw["NOMINAL TAGIHAN"] = pd.to_numeric(df_raw["NOMINAL TAGIHAN"], errors='coerce').fillna(0)
            nom_hist = df_raw["NOMINAL TAGIHAN"].sum()
        else: 
            nom_hist = 0
        st.metric("Nilai Penerimaan", f"Rp {nom_hist:,.0f}".replace(",", "."))
    
    with m4:
        if not df_proc.empty and "Nilai Tagihan" in df_proc.columns:
            df_proc["Nilai Tagihan"] = pd.to_numeric(df_proc["Nilai Tagihan"], errors='coerce').fillna(0)
            nom_proc = df_proc["Nilai Tagihan"].sum()
        else: 
            nom_proc = 0
        st.metric("Nilai Proses", f"Rp {nom_proc:,.0f}".replace(",", "."))

    st.divider()

    # --- 4. TABEL RINGKASAN TRANSAKSI TERAKHIR ---
    st.markdown("### 🕒 Transaksi Terkini")
    tab_h, tab_p = st.tabs(["📌 5 Transaksi Terakhir (Penerimaan)", "📄 5 Transaksi Terakhir (Proses)"])

    with tab_h:
        if not df_raw.empty:
            # Ambil 5 terakhir, lalu balik urutan (terbaru di atas)
            latest_h = df_raw.tail(5).iloc[::-1]
            st.dataframe(
                latest_h, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "NOMINAL TAGIHAN": st.column_config.NumberColumn(format="Rp %d"),
                    col_tgl_hist: st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm:ss")
                }
            )
        else:
            st.info("Data penerimaan kosong.")

    with tab_p:
        if not df_proc.empty:
            # Ambil 5 terakhir, lalu balik urutan (terbaru di atas)
            latest_p = df_proc.tail(5).iloc[::-1]
            st.dataframe(
                latest_p, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Nilai Tagihan": st.column_config.NumberColumn(format="Rp %d"),
                    col_tgl_proc: st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm:ss")
                }
            )
        else:
            st.info("Data proses SAP kosong.")

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat dashboard: {e}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)