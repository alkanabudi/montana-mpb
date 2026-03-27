import streamlit as st
from datetime import datetime
from utils import save_data_to_google

# Judul Halaman
st.title("➕ Input Tagihan MPB Baru")

# --- FORM INPUT ---
with st.form("form_input_mpb", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        # Kolom B: ASAL DEPARTEMEN
        asal_dept = st.text_input("ASAL DEPARTEMEN", placeholder="Contoh: KOMUNIKASI KORPORAT")
        # Kolom C: No Memo
        no_memo = st.text_input("No Memo", placeholder="Contoh: 41191/B/KU...")
        
    with col2:
        # Kolom D: NOMINAL TAGIHAN
        nominal = st.number_input("NOMINAL TAGIHAN", min_value=0, step=1)
        # Kolom E: Nama PIC
        pic = st.text_input("Nama PIC (Person In Charge) & EXT", placeholder="Nama dan nomor EXT")

    # Tombol Submit
    submitted = st.form_submit_button("SIMPAN DATA", use_container_width=True, type="primary")

    if submitted:
        # Validasi sederhana
        if asal_dept and no_memo and pic:
            # Kolom A: Waktu (Standar Timestamp)
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # --- DATA HANYA SAMPAI KOLOM E ---
            # Kita tidak mengirim kolom F dan G agar Dropdown di GSheets tetap utuh
            data_baru = [
                timestamp,          # Kolom A
                asal_dept.upper(),  # Kolom B
                no_memo,            # Kolom C
                nominal,            # Kolom D
                pic                 # Kolom E
            ]
            
            # Eksekusi simpan ke baris terakhir
            hasil = save_data_to_google(data_baru)  
            
            if hasil:
                st.success(f"✅ Data Memo **{no_memo}** berhasil tersimpan! ")
                st.balloons()
            else:
                st.error("❌ Gagal menyimpan. Silakan cek koneksi internet atau permission spreadsheet.")
        else:
            st.warning("⚠️ Mohon lengkapi Departemen, Nomor Memo, dan PIC.")

# --- CSS WIDE LAYOUT ---
st.markdown("<style>.block-container {max-width: 95% !important; padding-top: 2rem;}</style>", unsafe_allow_html=True)

# --- FOOTER SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown("<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by <b>Alkana</b><br>© 2026 PT Petrokimia Gresik</div>", unsafe_allow_html=True)