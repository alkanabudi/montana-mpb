import streamlit as st
import pandas as pd
import gspread
import base64
import json
<<<<<<< HEAD
import requests
import google.generativeai as genai
from io import BytesIO
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. FUNGSI KONEKSI GOOGLE SHEETS ---
=======
from oauth2client.service_account import ServiceAccountCredentials

# 1. FUNGSI KONEKSI (Hati-hati, jangan sampai terhapus)
>>>>>>> 502d1c8d5b8397d40dd54d4760e65f6f05846ef1
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        encoded_key = st.secrets["gcp_service_account"]["encoded_key"].strip()
        decoded_bytes = base64.b64decode(encoded_key)
        creds_info = json.loads(decoded_bytes.decode("utf-8"))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception as e:
<<<<<<< HEAD
        st.error(f"Gagal koneksi GSheets: {e}")
        return None

# --- 2. FUNGSI PEMBERSIH ANGKA ---
def to_numeric_clean(series):
    # Hapus Rp, titik, koma agar jadi angka murni untuk perhitungan
    s = series.astype(str).str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce').fillna(0)

# --- 3. FUNGSI AMBIL DATA PENERIMAAN (FILE 1) ---
=======
        st.error(f"Gagal koneksi: {e}")
        return None

# 2. FUNGSI PEMBERSIH ANGKA (Agar Dashboard Standar)
def to_numeric_clean(series):
    s = series.astype(str).str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce').fillna(0)

# 3. AMBIL DATA PENERIMAAN (Dashboard)
>>>>>>> 502d1c8d5b8397d40dd54d4760e65f6f05846ef1
@st.cache_data(ttl=600)
def get_data_from_google():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        nama_file = "Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)"
        spreadsheet = client.open(nama_file)
        sheet = spreadsheet.get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        df = df.loc[:, df.columns.str.strip() != ""]
        if "NOMINAL TAGIHAN" in df.columns:
            df["NOMINAL TAGIHAN"] = to_numeric_clean(df["NOMINAL TAGIHAN"])
        return df
    except Exception as e:
        st.error(f"Gagal tarik data Penerimaan: {e}")
        return pd.DataFrame()

<<<<<<< HEAD
# --- 4. FUNGSI AMBIL DATA TERPROSES (FILE 2) ---
=======
# 4. AMBIL DATA TERPROSES (Dashboard)
>>>>>>> 502d1c8d5b8397d40dd54d4760e65f6f05846ef1
@st.cache_data(ttl=600)
def get_data_mpb_2025():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
<<<<<<< HEAD
    try:
        nama_file_proses = "Memo Perintah Bayar 2025"
        spreadsheet = client.open(nama_file_proses)
        sheet = spreadsheet.get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        df = df.loc[:, df.columns.str.strip() != ""]
        if "Nilai Tagihan" in df.columns:
            df["Nilai Tagihan"] = to_numeric_clean(df["Nilai Tagihan"])
            df["NOMINAL TAGIHAN"] = df["Nilai Tagihan"]
        return df
    except Exception as e:
        st.error(f"Gagal tarik data Terproses: {e}")
        return pd.DataFrame()

# --- 5. FUNGSI SIMPAN DATA (INPUT MENU) ---
def save_data_to_google(data_row):
    client = get_gspread_client()
    if client is None: return False
    try:
=======
    try:
        nama_file_proses = "Memo Perintah Bayar 2025"
        spreadsheet = client.open(nama_file_proses)
        sheet = spreadsheet.get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        df = df.loc[:, df.columns.str.strip() != ""]
        if "Nilai Tagihan" in df.columns:
            df["Nilai Tagihan"] = to_numeric_clean(df["Nilai Tagihan"])
            df["NOMINAL TAGIHAN"] = df["Nilai Tagihan"] # Untuk hitungan total
        return df
    except Exception as e:
        st.error(f"Gagal tarik data Terproses: {e}")
        return pd.DataFrame()

# 5. FUNGSI SIMPAN DATA 
def save_data_to_google(data_row):
    client = get_gspread_client()
    if client is None: return False
    try:
        # Menyimpan ke file Penerimaan
>>>>>>> 502d1c8d5b8397d40dd54d4760e65f6f05846ef1
        nama_file = "Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)"
        sheet = client.open(nama_file).get_worksheet(0)
        sheet.append_row(data_row)
        return True
    except Exception as e:
        st.error(f"Gagal simpan data: {e}")
        return False
<<<<<<< HEAD

# --- 6. FUNGSI AI CHATBOT (BACA PDF GDRIVE) ---
def get_montana_chat_response(user_query):
    # API Key Gemini dari Streamlit Secrets
    try:
        genai.configure(api_key=st.secrets["gemini_api_key"])
    except:
        return "Konfigurasi Gemini API Key tidak ditemukan di Secrets."

    # ID FILE GOOGLE DRIVE MAS BRAM
    # Ganti dengan ID file PDF aturan_mpb.pdf Mas Bram
    file_id = "1jX-yVKyMmIuOOdx7Z-qpEtTYzn_RhNu1" 
    
    url = f'https://drive.google.com/uc?id={file_id}'
    
    text_knowledge = ""
    
    try:
        # Download PDF dari GDrive ke memori
        response = requests.get(url)
        if response.status_code == 200:
            pdf_file = BytesIO(response.content)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text_knowledge += page.extract_text()
        else:
            text_knowledge = "Gagal mengakses dokumen aturan di Google Drive."
    except Exception as e:
        text_knowledge = f"Kesalahan membaca PDF: {str(e)}"

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Anda adalah 'Montana AI' asisten cerdas PT Petrokimia Gresik.
    Tugas Anda menjawab pertanyaan seputar SOP/Aturan MPB berdasarkan data berikut:
    
    {text_knowledge}
    
    ATURAN:
    - Jika jawaban tidak ada di teks, arahkan hubungi Admin (Mas Bram).
    - Gunakan bahasa profesional dan ramah.
    
    Pertanyaan User: {user_query}
    """
    
    try:
        ai_resp = model.generate_content(prompt)
        return ai_resp.text
    except Exception:
        return "Koneksi AI sedang sibuk, silakan coba lagi."
=======
>>>>>>> 502d1c8d5b8397d40dd54d4760e65f6f05846ef1
