import streamlit as st
from utils import get_data_from_google

# Konfigurasi halaman agar lebar
st.set_page_config(page_title="Histori Penerimaan", layout="wide")

st.title("📜 Histori Seluruh Penerimaan")

try:
    # Mengambil data menggunakan fungsi yang ada di utils.py
    df_raw = get_data_from_google()
    
    # Fitur Pencarian khusus di halaman Histori
    search = st.text_input("🔍 Cari Data (Nomor Memo, Vendor, atau Departemen):")
    
    if search:
        # Mencari keyword di seluruh kolom
        df_display = df_raw[df_raw.apply(lambda row: search.lower() in row.astype(str).str.lower().values, axis=1)]
    else:
        df_display = df_raw

    st.info(f"Ditemukan {len(df_display)} data.")
    
    # Menampilkan Tabel Utama (Tanpa Index agar lebih rapi)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Fitur Download untuk laporan
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Laporan (CSV)",
        data=csv,
        file_name="histori_mpb.csv",
        mime="text/csv",
    )

except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat halaman Histori: {e}")

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
    
    # --- FOOTER ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)