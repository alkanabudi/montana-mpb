import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_data_from_google, get_data_mpb_2025

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Analisis Tren MPB", layout="wide")

# --- CUSTOM CSS FOOTER & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    [data-testid="stMetricValue"] { font-size: 24px; color: #4da3ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Analisis Performa & Distribusi MPB")

try:
    # 2. AMBIL DATA
    df_hist = get_data_from_google()
    df_proc = get_data_mpb_2025()

    # --- PRE-PROCESSING WAKTU (Agar Slicer Berjalan) ---
    col_tgl_hist = df_hist.columns[0]
    df_hist[col_tgl_hist] = pd.to_datetime(df_hist[col_tgl_hist], dayfirst=True, errors='coerce')
    
    col_tgl_proc = "Tanggal Dokumen Masuk Akuntansi"
    if col_tgl_proc in df_proc.columns:
        df_proc[col_tgl_proc] = pd.to_datetime(df_proc[col_tgl_proc], dayfirst=True, errors='coerce')

    # Tambah Kolom Tahun & Nama Bulan
    df_hist['Tahun'] = df_hist[col_tgl_hist].dt.year.fillna(0).astype(int)
    df_hist['Bulan'] = df_hist[col_tgl_hist].dt.month_name()
    df_proc['Tahun'] = df_proc[col_tgl_proc].dt.year.fillna(0).astype(int)
    df_proc['Bulan'] = df_proc[col_tgl_proc].dt.month_name()

    # --- SIDEBAR SLICER (SAMA DENGAN DASHBOARD) ---
    st.sidebar.header("🔍 Slicer Analisis")
    
    list_tahun = sorted(list(set(df_hist['Tahun'].unique()) | set(df_proc['Tahun'].unique())), reverse=True)
    if 0 in list_tahun: list_tahun.remove(0)
    
    sel_year = st.sidebar.selectbox("Pilih Tahun Analisis", ["Semua Tahun"] + [str(t) for t in list_tahun])
    
    list_bulan = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
    sel_months = st.sidebar.multiselect("Filter Bulan", list_bulan)

    # Fungsi Filter
    def apply_filter(df, year, months):
        temp = df.copy()
        if year != "Semua Tahun":
            temp = temp[temp['Tahun'] == int(year)]
        if months:
            temp = temp[temp['Bulan'].isin(months)]
        return temp

    df_hist_f = apply_filter(df_hist, sel_year, sel_months)
    df_proc_f = apply_filter(df_proc, sel_year, sel_months)

    # --- TAB ANALISA ---
    tab1, tab2 = st.tabs(["📊 Perbandingan Penerimaan VS Proses", "⏳ Analisa Status & Waktu"])

    with tab1:
        st.subheader(f"Volume Tagihan Periode: {sel_year}")
        
        # Penyiapan data Bar Chart
        v1 = df_hist_f["ASAL DEPARTEMEN"].value_counts().reset_index()
        v1.columns = ["Unit", "Jumlah"]; v1["Sumber"] = "History"

        v2 = df_proc_f["Unit Kerja"].value_counts().reset_index()
        v2.columns = ["Unit", "Jumlah"]; v2["Sumber"] = "Proses 2025"

        df_compare = pd.concat([v1, v2])

        fig_compare = px.bar(
            df_compare, y="Unit", x="Jumlah", color="Sumber",
            barmode="group", height=max(600, len(df_compare) * 20),
            color_discrete_map={"History": "#004280", "Proses 2025": "#4da3ff"},
            labels={"Unit": "Departemen", "Jumlah": "Total Memo"}
        )
        fig_compare.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=250))
        st.plotly_chart(fig_compare, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Distribusi Status (History)")
            fig_pie = px.pie(df_hist_f, names="STATUS", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with c2:
            st.subheader("Tren Harian Input (Proses)")
            if not df_proc_f.empty:
                # Tren berdasarkan tanggal
                df_day = df_proc_f.groupby(df_proc_f[col_tgl_proc].dt.date).size().reset_index(name='Jumlah')
                fig_line = px.line(df_day, x=col_tgl_proc, y='Jumlah', title="Volume Masuk Harian")
                st.plotly_chart(fig_line, use_container_width=True)

    # --- FOOTER ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("<div style='text-align: center; color: grey;'>Developed by <b>Alkana</b></div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Gagal memuat analisa: {e}")

 # --- FOOTER DI SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 0.8em;'>
        Developed by <b>Alkana</b><br>
        © 2026 Penerimaan Tagihan PT Petrokimia Gresik
    </div>
    """,
    unsafe_allow_html=True
)