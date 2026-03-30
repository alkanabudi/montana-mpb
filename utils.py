import streamlit as st
import pandas as pd
import gspread
import base64
import json
import requests
import os
import tempfile
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials

# --- REVISI IMPORT LANGCHAIN ANTI-ERROR 2026 ---
try:
    # Cara baru untuk LangChain v0.3+
    from langchain.chains.question_answering import load_qa_chain
except ImportError:
    try:
        # Alternatif jika folder struktur berbeda
        from langchain.chains import load_qa_chain
    except ImportError:
        # Jika benar-benar mentok
        st.error("Library LangChain belum terpasang sempurna. Silakan Reboot App.")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate

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

# --- 3. AMBIL DATA DARI GOOGLE SHEETS ---
@st.cache_data(ttl=600)
def get_data_from_google():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Daftar Penerimaan TAGIHAN MEMO PERINTAH BAYAR (Jawaban)").get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        if "NOMINAL TAGIHAN" in df.columns:
            df["NOMINAL TAGIHAN"] = to_numeric_clean(df["NOMINAL TAGIHAN"])
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def get_data_mpb_2025():
    client = get_gspread_client()
    if client is None: return pd.DataFrame()
    try:
        sheet = client.open("Memo Perintah Bayar 2025").get_worksheet(0)
        list_of_lists = sheet.get_all_values()
        if not list_of_lists: return pd.DataFrame()
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        if "Nilai Tagihan" in df.columns:
            df["Nilai Tagihan"] = to_numeric_clean(df["Nilai Tagihan"])
            df["NOMINAL TAGIHAN"] = df["Nilai Tagihan"]
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

# --- 4. AI MONTANA (VERSI LANGCHAIN) ---
def get_montana_chat_response(user_query):
    try:
        # Inisialisasi LLM Gemini melalui LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=st.secrets["gemini_api_key"],
            temperature=0.3
        )

        # Ambil PDF dari GDrive
        file_id = "1jX-yVKyMmIuOOdx7Z-qpEtTYzn_RhNu1"
        url = f'https://drive.google.com/uc?id={file_id}&export=download'
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=15)

        if resp.status_code == 200 and b'%PDF' in resp.content[:4]:
            # Simpan sementara ke file lokal agar bisa dibaca PyPDFLoader
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(resp.content)
                tmp_path = tmp_file.name
            
            # Load dan Split dokumen pakai LangChain
            loader = PyPDFLoader(tmp_path)
            pages = loader.load_and_split()
            
            # Hapus file sementara
            os.remove(tmp_path)

            # Buat Prompt Template agar Montana lebih pintar
            template = """Anda adalah Montana, asisten AI PT Petrokimia Gresik yang ahli dalam aturan MPB.
            Gunakan data SOP berikut untuk menjawab pertanyaan:
            {context}
            
            Pertanyaan: {question}
            Jawaban:"""
            
            PROMPT = PromptTemplate(template=template, input_variables=["context", "question"])
            
            # Jalankan Chain Tanya Jawab
            chain = load_qa_chain(llm, chain_type="stuff", prompt=PROMPT)
            response = chain.invoke({"input_documents": pages, "question": user_query})
            
            return response["output_text"]
        else:
            return "Montana gagal mengakses dokumen. Pastikan link GDrive 'Anyone with link'."

    except Exception as e:
        return f"Montana sedang re-sinkronisasi sistem. (Info: {str(e)})"