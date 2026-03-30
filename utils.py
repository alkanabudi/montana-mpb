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

# --- 3. FUNGSI PEMBERSIH KOLOM DUPLIKAT ---
def fix_duplicate_columns(headers):
    clean_headers = []
    for i, h in enumerate(headers):
        new_h = h.strip() if h.strip() != "" else f"Kolom_{i}"
        if new_h in clean_headers:
            new_h = f"{new_h}_{i}"
        clean_headers.append(new_h)
    return clean_headers

# --- 4. AMBIL DATA DARI GOOGLE SHEETS ---
@st.cache_data(ttl=60)
def get_data_from_google():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if len(list_of_lists) <= 1:
            return pd.DataFrame()
        
        headers = fix_duplicate_columns(list_of_lists[0])
        df = pd.DataFrame(list_of_lists[1:], columns=headers)
        
        if "NOMINAL TAGIHAN" in df.columns:
            df["NOMINAL TAGIHAN"] = to_numeric_clean(df["NOMINAL TAGIHAN"])
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=60)
def get_data_mpb_2025():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Memo Perintah Bayar 2025").get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists or len(list_of_lists) <= 1:
            return pd.DataFrame()
            
        headers = fix_duplicate_columns(list_of_lists[0])
        df = pd.DataFrame(list_of_lists[1:], columns=headers)
        
        # Cari kolom nilai tagihan secara fleksibel
        target = ""
        if "Nilai Tagihan" in df.columns: target = "Nilai Tagihan"
        elif "NOMINAL TAGIHAN" in df.columns: target = "NOMINAL TAGIHAN"
        
        if target:
            df[target] = to_numeric_clean(df[target])
            df["NOMINAL TAGIHAN"] = df[target]
            
        return df
    except:
        return pd.DataFrame()

def save_data_to_google(data_row):
    client = get_gspread_client()
    if client is None: return False
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        sheet.append_row(data_row)
        return True
    except:
        return False

# --- 5. AI MONTANA ---
def get_montana_chat_response(user_query):
    try:
        genai.configure(api_key="AIzaSyCjDPCw62gKc8kLa7rWp767AiUp7FMV5zQ")
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        file_id = "1jX-yVKyMmIuOOdx7Z-qpEtTYzn_RhNu1" 
        url = f'https://drive.google.com/uc?id={file_id}&export=download'
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        text_knowledge = ""
        if resp.status_code == 200:
            pdf_file = BytesIO(resp.content)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text_knowledge += page.extract_text() or ""
        
        prompt = f"Anda Montana AI. Jawablah berdasarkan data ini: {text_knowledge[:10000]}\n\nUser: {user_query}"
        ai_resp = model.generate_content(prompt)
        return ai_resp.text
    except Exception as e:
        return f"Sistem sedang pemeliharaan teknis. (Pesan: {str(e)})"