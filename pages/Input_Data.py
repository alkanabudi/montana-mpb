import streamlit as st
from datetime import datetime
from utils import save_data_to_google

st.set_page_config(page_title="Input Data MPB", layout="wide")

st.title("➕ Input Tagihan MPB Baru")

# Pastikan urutan kolom di data_baru SESUAI dengan urutan kolom di Google Sheets Anda
with st.form("form_input_mpb", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        asal_dept = st.selectbox("Asal Departemen", [
            "AKUNTANSI", "PELAPORAN KEUANGAN", "PERPAJAKAN", "TREASURY", "PENGADAAN", "PENGEMBANGAN SDM & ORGANISASI", "ADMINISTRASI PEMASARAN"
        ])
        no_memo = st.text_input("Nomor Memo/Nota")
        
        
    with col2:
        nominal = st.number_input("Nominal Tagihan", min_value=0, step=1000)
        pic = st.text_input("Nama PIC (Person In Charge)")
        

    # PERBAIKAN DI SINI: Nama fungsi yang benar adalah st.form_submit_button
    submitted = st.form_submit_button("Submit Data")

    if submitted:
        if no_memo and vendor:
            # Sesuaikan urutan ini dengan kolom di Google Sheets (Timestamp, Dept, No Memo, Nominal, PIC, Status)
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            data_baru = [timestamp, asal_dept, no_memo, nominal, pic, status]
            
            hasil = save_data_to_google(data_baru)
            
            if hasil:
                st.success("✅ Data berhasil tersimpan ke Google Sheets!")
                st.balloons()
        else:
            st.warning("⚠️ Mohon isi Nomor Memo dan Vendor terlebih dahulu.")
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