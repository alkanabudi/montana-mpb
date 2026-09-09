import streamlit as st
from datetime import datetime
from utils import extract_and_verify_memo_pdf, save_data_to_google


uploaded_file = st.file_uploader("Unggah Memo MPB (PDF)", type=["pdf"])

if uploaded_file is not None:
    data_ext, checks, err = extract_and_verify_memo_pdf(uploaded_file)
    if err:
        st.error(f"Gagal membaca PDF: {err}")
    else:
        # Tampilkan hasil ekstraksi ke form review
        st.success("Memo berhasil diekstraksi!")
        st.write("Nomor Memo:", data_ext["no_memo"])
        st.write("Nominal:", data_ext["nominal"])