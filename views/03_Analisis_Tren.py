import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import get_data_from_google, get_data_mpb_2025, create_pdf_report_mpb

# 1. Konfigurasi Layout (Wide)
st.markdown("<style>.block-container {max-width: 95% !important; padding-top: 2rem;}</style>", unsafe_allow_html=True)

st.title("📈 Analisis Performa & Komparasi MPB")

try:
    # --- 1. AMBIL DATA ---
    df_raw = get_data_from_google()
    df_proc = get_data_mpb_2025()

    with st.expander("🛠 Debug Data Sistem"):
        st.write(f"Baris Penerimaan: {len(df_raw)} | Baris Proses: {len(df_proc)}")

    # --- 2. KONVERSI TANGGAL ---
    col_tgl_hist = df_raw.columns[0]
    df_raw[col_tgl_hist] = pd.to_datetime(df_raw[col_tgl_hist], errors='coerce')
    
    col_tgl_proc = "Tanggal Dokumen Masuk Akuntansi"
    if not df_proc.empty:
        df_proc[col_tgl_proc] = pd.to_datetime(df_proc[col_tgl_proc], errors='coerce')
        df_proc = df_proc.dropna(subset=[col_tgl_proc])

    df_raw = df_raw.dropna(subset=[col_tgl_hist])

    # Ekstrak Tahun & Bulan
    df_raw['Tahun'] = df_raw[col_tgl_hist].dt.year.astype(int)
    df_raw['Bulan'] = df_raw[col_tgl_hist].dt.month_name()
    
    if not df_proc.empty:
        df_proc['Tahun'] = df_proc[col_tgl_proc].dt.year.astype(int)
        df_proc['Bulan'] = df_proc[col_tgl_proc].dt.month_name()

    # --- 3. SIDEBAR FILTERS ---
    st.sidebar.header("🔍 Filter Analisis")
    all_years = sorted(list(set(df_raw['Tahun'].unique()) | (set(df_proc['Tahun'].unique()) if not df_proc.empty else set())), reverse=True)
    sel_year = st.sidebar.selectbox("Pilih Tahun", all_years if all_years else [2026])
    
    months_order = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
    sel_months = st.sidebar.multiselect("Pilih Bulan", months_order)

    # Filtering Data
    df_h_f = df_raw[df_raw['Tahun'] == int(sel_year)]
    df_p_f = df_proc[df_proc['Tahun'] == int(sel_year)] if not df_proc.empty else pd.DataFrame()
    
    if sel_months:
        df_h_f = df_h_f[df_h_f['Bulan'].isin(sel_months)]
        if not df_p_f.empty:
            df_p_f = df_p_f[df_p_f['Bulan'].isin(sel_months)]

    # --- 4. TAMPILAN TAB GRAFIK ---
    t1, t2, t3, t4 = st.tabs(["📅 Tren Waktu", "🏢 Distribusi Unit", "💰 Analisis Nominal", "📊 Komparasi Qty"])

    with t1:
        st.subheader(f"Trend Bulanan Tahun {sel_year}")
        g1 = df_h_f.groupby('Bulan').size().reindex(months_order).reset_index(name='Jumlah'); g1['Sumber'] = 'Penerimaan'
        if not df_p_f.empty:
            g2 = df_p_f.groupby('Bulan').size().reindex(months_order).reset_index(name='Jumlah'); g2['Sumber'] = 'Proses (SAP)'
            df_trend = pd.concat([g1, g2]).dropna(subset=['Jumlah'])
        else:
            df_trend = g1.dropna(subset=['Jumlah'])
        st.plotly_chart(px.line(df_trend, x='Bulan', y='Jumlah', color='Sumber', markers=True, category_orders={"Bulan": months_order}), use_container_width=True)

    with t2:
        st.subheader("Beban Kerja Per Departemen")
        u1 = df_h_f["ASAL DEPARTEMEN"].value_counts().reset_index(); u1.columns = ["Unit", "Jumlah"]; u1["Tipe"] = "Penerimaan"
        u2 = df_p_f["Unit Kerja"].value_counts().reset_index() if not df_p_f.empty else pd.DataFrame(columns=["Unit", "Jumlah"])
        if not u2.empty:
            u2.columns = ["Unit", "Jumlah"]; u2["Tipe"] = "Proses"
        st.plotly_chart(px.bar(pd.concat([u1, u2]), y="Unit", x="Jumlah", color="Tipe", barmode="group", orientation='h'), use_container_width=True)

    with t3:
        st.subheader("Analisis Nominal & Status SAP")
        if not df_p_f.empty:
            c1, c2 = st.columns(2)
            with c1:
                top_v = df_p_f.groupby('Vendor')['Nilai Tagihan'].sum().sort_values(ascending=False).head(10).reset_index()
                st.plotly_chart(px.pie(top_v, values='Nilai Tagihan', names='Vendor', hole=0.3, title="Top 10 Vendor"), use_container_width=True)
            with c2:
                if "No MVP" in df_p_f.columns:
                    df_p_f["Status"] = df_p_f["No MVP"].apply(lambda x: "Done" if str(x).strip() != "" else "Pending")
                    st.plotly_chart(px.pie(df_p_f, names="Status", color_discrete_map={"Done":"#10B981","Pending":"#EF4444"}), use_container_width=True)

    with t4:
        st.subheader(f"Bar Chart Komparatif Harian (Tahun {sel_year})")
        if not df_h_f.empty:
            res_h = df_h_f.groupby(df_h_f[col_tgl_hist].dt.date).size().reset_index(name='Qty')
            res_h.columns = ['Tanggal', 'Qty']
            res_h['Tipe'] = 'Masuk'
            
            res_p = pd.DataFrame(columns=['Tanggal', 'Qty', 'Tipe'])
            if not df_p_f.empty:
                res_p = df_p_f.groupby(df_p_f[col_tgl_proc].dt.date).size().reset_index(name='Qty')
                res_p.columns = ['Tanggal', 'Qty']
                res_p['Tipe'] = 'Proses'
            
            df_c = pd.concat([res_h, res_p])
            fig_bar = px.bar(df_c, x='Tanggal', y='Qty', color='Tipe', barmode='group', text_auto=True,
                             color_discrete_map={'Masuk': '#3B82F6', 'Proses': '#10B981'})
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- 5. FITUR CETAK LAPORAN PDF PRO (ATM STYLE) ---
    st.markdown("### 🖨️ Cetak Laporan PDF Profesional")
    st.info("Download rekapitulasi PDF dengan analisis rekomendasi otomatis berbasis filter di atas.")
    
    with st.expander("⚙️ Pengaturan Cetak Laporan", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            list_dept_f = sorted(df_h_f['ASAL DEPARTEMEN'].unique())
            sel_dept_pdf = st.selectbox("Pilih Departemen untuk Laporan", list_dept_f)
        with c2:
            period_val = f"{', '.join(sel_months) if sel_months else 'Tahunan'} {sel_year}"
            period_str = st.text_input("Periode Laporan", value=period_val)

        # Filter data untuk dikirim ke PDF generator
        df_pdf_data = df_h_f[df_h_f['ASAL DEPARTEMEN'] == sel_dept_pdf].copy()

        if st.button("📥 Generate & Download PDF Report", use_container_width=True, type="primary"):
            if not df_pdf_data.empty:
                with st.spinner(f"Menganalisis data {sel_dept_pdf}..."):
                    pdf_bytes, err = create_pdf_report_mpb(df_pdf_data, sel_dept_pdf, period_str)
                    
                    if err:
                        st.error(f"Gagal Cetak: {err}")
                    else:
                        st.success("✅ Laporan PDF siap diunduh!")
                        st.download_button(
                            label="💾 Download File PDF",
                            data=pdf_bytes,
                            file_name=f"Montana_Report_{sel_dept_pdf.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            else:
                st.warning("Data untuk departemen terpilih kosong pada filter ini.")

except Exception as e:
    st.error(f"Kesalahan Sistem: {e}")

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)