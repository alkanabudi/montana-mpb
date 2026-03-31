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

    df_raw = get_data_from_google()
    if not df_raw.empty:
    # Ganti 'None' atau NaN dengan string kosong agar tidak muncul tulisan None di tabel
    df_raw = df_raw.fillna("")

    # --- 2. CEK DATA KOSONG (PAGAR PENGAMAN) ---
    # Jika df_raw kosong, kita tampilkan peringatan dan STOP kode di sini agar tidak error ke bawah
    if df_raw.empty:
        st.warning("⚠️ Data Penerimaan di Google Sheets masih kosong.")
        st.info("Silakan masukkan data melalui menu Input Tagihan atau isi Google Sheets Anda.")
        
        # Tampilkan metrik nol agar dashboard tidak terlihat rusak
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Penerimaan", "0 Memo")
        m2.metric("Total Proses", "0 Memo")
        m3.metric("Nilai Penerimaan", "Rp 0")
        m4.metric("Nilai Proses", "Rp 0")
        
        st.stop() # BERHENTI DI SINI

    # --- 3. PRE-PROCESSING WAKTU (Hanya jalan jika data ADA) ---
    # Gunakan pengecekan kolom agar tidak error index
    if len(df_raw.columns) > 0:
        col_tgl_hist = df_raw.columns[0]
        df_raw[col_tgl_hist] = pd.to_datetime(df_raw[col_tgl_hist], errors='coerce')
    
    col_tgl_proc = "Tanggal Dokumen Masuk Akuntansi"
    if not df_proc.empty and col_tgl_proc in df_proc.columns:
        df_proc[col_tgl_proc] = pd.to_datetime(df_proc[col_tgl_proc], errors='coerce')

    # --- 4. METRIK KPI UTAMA ---
    st.markdown("### 📊 Ringkasan Performa Keseluruhan")
    m1, m2, m3, m4 = st.columns(4)
    
    # Hitung Metrik dengan aman
    count_raw = len(df_raw)
    count_proc = len(df_proc) if not df_proc.empty else 0
    
    nom_hist = df_raw["NOMINAL TAGIHAN"].sum() if "NOMINAL TAGIHAN" in df_raw.columns else 0
    nom_proc = df_proc["Nilai Tagihan"].sum() if (not df_proc.empty and "Nilai Tagihan" in df_proc.columns) else 0

    with m1:
        st.metric("Total Penerimaan", f"{count_raw} Memo")
    
    with m2:
        st.metric("Total Proses", f"{count_proc} Memo")
    
    with m3:
        st.metric("Nilai Penerimaan", f"Rp {nom_hist:,.0f}".replace(",", "."))
    
    with m4:
        st.metric("Nilai Proses", f"Rp {nom_proc:,.0f}".replace(",", "."))

    st.divider()

    # --- 5. TABEL RINGKASAN TRANSAKSI TERAKHIR ---
    st.markdown("### 🕒 Transaksi Terkini")
    tab_h, tab_p = st.tabs(["📌 5 Transaksi Terakhir (Penerimaan)", "📄 5 Transaksi Terakhir (Proses)"])

    with tab_h:
        # 1. Pastikan kolom Waktu terbaca sebagai tanggal untuk sorting
        # Kita asumsikan kolom pertama (index 0) adalah Waktu/Timestamp
        col_waktu = clean_h.columns[0] 
        
        # Buat kolom sementara untuk sorting agar tidak merusak tampilan teks asli
        clean_h['sort_key'] = pd.to_datetime(clean_h[col_waktu], errors='coerce')
        
        # 2. Urutkan berdasarkan sort_key (Terbaru di atas)
        latest_h = clean_h.sort_values(by='sort_key', ascending=False).head(5)
        
        # 3. Hapus kolom bantuan sorting agar tidak tampil di tabel
        latest_h = latest_h.drop(columns=['sort_key'])

        if not latest_h.empty:
            st.dataframe(
                latest_h, 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("Belum ada transaksi penerimaan.")

except Exception as e:
    # Error log yang lebih spesifik untuk memudahkan Mas Bram debug
    st.error(f"Terjadi kesalahan teknis pada Dashboard: {str(e)}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)