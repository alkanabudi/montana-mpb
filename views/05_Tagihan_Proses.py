import streamlit as st
import pandas as pd
from utils import get_data_mpb_2025

st.title("📑 Monitoring Tagihan Terproses")

try:
    # 1. Ambil Data
    df_proc = get_data_mpb_2025()
    role = st.session_state.get("role")

    if not df_proc.empty:
        # --- PERBAIKAN URUTAN (SORTING DEFAULT) ---
        # Membalik urutan agar baris terakhir di Sheets muncul paling atas di tabel
        df_proc = df_proc.iloc[::-1].reset_index(drop=True)

        # --- BAGIAN PANEL PENCARIAN & FILTER ---
        st.markdown(f"### 🔍 Panel {'Monitoring' if role == 'ADMIN' else 'Pencarian'}")
        
        col_f1, col_f2 = st.columns([1, 2])
        
        with col_f1:
            list_unit = sorted(df_proc["Unit Kerja"].unique().tolist())
            selected_unit = st.selectbox("Pilih Unit Kerja:", ["Semua Unit"] + list_unit)

        with col_f2:
            search_query = st.text_input(
                "Cari Cepat (Vendor / No MVP / Keterangan):", 
                placeholder="Ketik kata kunci lalu tekan Enter..."
            )

        # --- LOGIKA FILTERING ---
        df_filtered = df_proc.copy()

        if selected_unit != "Semua Unit":
            df_filtered = df_filtered[df_filtered["Unit Kerja"] == selected_unit]
        
        if search_query:
            mask = df_filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search_query.lower()).any(), axis=1)
            df_filtered = df_filtered[mask]

        # --- LOGIKA TAMPILAN BERDASARKAN ROLE ---
        
        # Kondisi A: Jika Login sebagai ADMIN (Buka Semua)
        if role == "ADMIN":
            st.divider()
            st.success(f"Mode Admin: Menampilkan **{len(df_filtered)}** data tagihan (Urut Terbaru).")
            
            st.dataframe(
                df_filtered, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Nilai Tagihan": st.column_config.NumberColumn(format="Rp %d"),
                }
            )

        # Kondisi B: Jika Login sebagai UNIT (Tabel muncul hanya jika dicari)
        else:
            if (selected_unit != "Semua Unit") or (search_query.strip() != ""):
                st.divider()
                if not df_filtered.empty:
                    st.info(f"Ditemukan **{len(df_filtered)}** data yang sesuai (Urut Terbaru).")
                    st.dataframe(
                        df_filtered, 
                        use_container_width=True, 
                        hide_index=True,
                        column_config={
                            "Nilai Tagihan": st.column_config.NumberColumn(format="Rp %d"),
                        }
                    )
                else:
                    st.warning("Data tidak ditemukan.")
            else:
                st.info("Silakan masukkan Unit Kerja atau kata kunci untuk mencari data tagihan.")

    else:
        st.info("Database kosong atau tidak dapat diakses.")

except Exception as e:
    st.error(f"Terjadi kesalahan sistem: {e}")

# Paksa layout tetap wide
st.markdown("<style>.block-container {max-width: 95% !important;}</style>", unsafe_allow_html=True)

# --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)