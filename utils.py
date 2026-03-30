import streamlit as st
import pandas as pd
import gspread
import base64
import json
import requests
import google.generativeai as genai
from io import BytesIO
from pypdf import PdfReader
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. KONEKSI GOOGLE SHEETS ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        encoded_key = st.secrets["gcp_service_account"]["encoded_key"].strip()
        decoded_bytes = base64.b64decode(encoded_key)
        creds_info = json.loads(decoded_bytes.decode("utf-8"))
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
        return gspread.authorize(creds)
    except Exception:
        return None

# --- 2. PEMBERSIH ANGKA ---
def to_numeric_clean(series):
    s = series.astype(str).str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce').fillna(0)

# --- 3. AMBIL DATA PENERIMAAN ---
@st.cache_data(ttl=600)
def get_data_from_google():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        df = df.loc[:, df.columns.str.strip() != ""]
        if "NOMINAL TAGIHAN" in df.columns:
            df["NOMINAL TAGIHAN"] = to_numeric_clean(df["NOMINAL TAGIHAN"])
        return df
    except:
        return pd.DataFrame()

# --- 4. AMBIL DATA TERPROSES ---
@st.cache_data(ttl=600)
def get_data_mpb_2025():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Memo Perintah Bayar 2025").get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        df = df.loc[:, df.columns.str.strip() != ""]
        if "Nilai Tagihan" in df.columns:
            df["Nilai Tagihan"] = to_numeric_clean(df["Nilai Tagihan"])
            df["NOMINAL TAGIHAN"] = df["Nilai Tagihan"]
        return df
    except:
        return pd.DataFrame()

# --- 5. SIMPAN DATA ---
def save_data_to_google(data_row):
    client = get_gspread_client()
    if client is None: return False
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        sheet.append_row(data_row)
        return True
    except:
        return False

# --- 6. AI MONTANA ---
def get_montana_chat_response(user_query):
    try:
        genai.configure(api_key=st.secrets["gemini_api_key"])
        
        # --- DAFTAR MODEL TERBARU 2026 (Urutan Prioritas) ---
        model_names = ['gemini-2.0-flash', 'gemini-1.5-flash-latest', 'gemini-pro']
        
        model = None
        for name in model_names:
            try:
                model = genai.GenerativeModel(name)
                # Tes kecil untuk memastikan model ini tersedia
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                break 
            except:
                continue
        
        if model is None:
            return "Montana sedang sinkronisasi server Google. Coba lagi dalam 1 menit."

        # Ambil Data dari GDrive
        file_id = "1jX-yVKyMmIuOOdx7Z-qpEtTYzn_RhNu1" 
        url = f'https://drive.google.com/uc?id={file_id}&export=download'
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=15)
        
        text_knowledge = ""
        if resp.status_code == 200 and b'%PDF' in resp.content[:4]:
            reader = PdfReader(BytesIO(resp.content))
            for page in reader.pages:
                text_knowledge += page.extract_text()
        else:
            return "Montana gagal mengakses dokumen SOP. Pastikan link GDrive 'Anyone with link'."

        prompt = f"Anda Montana AI. Jawablah berdasarkan data ini: {text_knowledge[:10000]}\n\nUser: {user_query}"
        
        ai_resp = model.generate_content(prompt)
        return ai_resp.text

    except Exception as e:
        return f"Sistem sedang pemeliharaan teknis. (Info: {str(e)})"