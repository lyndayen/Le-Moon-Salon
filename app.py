import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import qrcode
from io import BytesIO
import requests
import cv2
import numpy as np

# --- CONFIG ---
BOT_TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. LOAD DYNAMIC PACKAGES FROM GOOGLE SHEET
try:
    settings_df = conn.read(worksheet="settings")
    PACKAGES = dict(zip(settings_df['package_name'], settings_df['points']))
except:
    PACKAGES = {"សូមបញ្ចូលកញ្ចប់ក្នុង Settings": 0}

def send_receipt(name, t_id, pts, left, service):
    if t_id and str(t_id).strip():
        msg = (f"🌙 **Le Moon Salon**\n\n"
               f"អតិថិជន: **{name}**\n"
               f"សេវាកម្ម: **{service}**\n"
               f"កាត់អស់: **{pts} ពិន្ទុ**\n"
               f"នៅសល់សរុប: **{left} ពិន្ទុ**")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={"chat_id": t_id, "text": msg, "parse_mode": "Markdown"})

st.set_page_config(page_title="Le Moon Salon", layout="centered")
st.title("🌙 ប្រព័ន្ធគ្រប់គ្រង Le Moon")

menu = ["ចុះឈ្មោះអតិថិជន", "ស្កេន QR កាត់ពិន្ទុ", "របាយការណ៍សរុប"]
choice = st.sidebar.selectbox("ម៉ឺនុយ", menu)

if choice == "ចុះឈ្មោះអតិថិជន":
    st.subheader("📝 ចុះឈ្មោះសមាជិកថ្មី")
    name = st.text_input("ឈ្មោះ")
    phone = st.text_input("លេខទូរស័ព្ទ")
    pkg = st.selectbox("ជ្រើសរើសកញ្ចប់", list(PACKAGES.keys()))
    
    if st.button("រក្សាទុក"):
        cust_df = conn.read(worksheet="customers").dropna(how="all")
        bal_df = conn.read(worksheet="balances").dropna(how="all")
        new_id = len(cust_df) + 1
        
        # Save to Sheets
        new_c = pd.DataFrame([{"id": new_id, "name": name, "phone": phone, "telegram_id": ""}])
        new_b = pd.DataFrame([{"customer_id": new_id, "package": pkg, "points": PACKAGES[pkg]}])
        
        conn.update(worksheet="customers", data=pd.concat([cust_df, new_c], ignore_index=True))
        conn.update(worksheet="balances", data=pd.concat([bal_df, new_b], ignore_index=True))
        
        st.success("ចុះឈ្មោះជោគជ័យ!")
        qr_img = qrcode.make(str(new_id))
        st.image(np.array(qr_img), caption=f"ID: {new_id}")

elif choice == "ស្កេន QR កាត់ពិន្ទុ":
    st.subheader("📷 ស្កេនបាកូដ")
    img = st.camera_input("សូមថតរូប QR")
    
    if img:
        f_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
        scanned_id, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imdecode(f_bytes, 1))
        
        if scanned_id:
            cust_df = conn.read(worksheet="customers").dropna(how="all")
            bal_df = conn.read(worksheet="balances").dropna(how="all")
            
            user = cust_df[cust_df['id'].astype(str) == str(scanned_id)]
            if not user.empty:
                c_name, t_id = user.iloc[0]['name'], user.iloc[0]['telegram_id']
                u_bal = bal_df[bal_df['customer_id'].astype(str) == str(scanned_id)]
                current_pts = int(u_bal.iloc[0]['points'])
                
                st.info(f"👤 {c_name} | នៅសល់: {current_pts} ពិន្ទុ")
                svc = st.text_input("សេវាកម្ម")
                pts_to_use = st.number_input("កាត់ពិន្ទុ", 1, current_pts, 1)
                
                if st.button("បញ្ជាក់"):
                    new_pts = current_pts - pts_to_use
                    bal_df.loc[bal_df['customer_id'].astype(str) == str(scanned_id), 'points'] = new_pts
                    conn.update(worksheet="balances", data=bal_df)
                    
                    send_receipt(c_name, t_id, pts_to_use, new_pts, svc)
                    st.success("រួចរាល់!"); st.balloons()
            else: st.error("រកមិនឃើញ!")

elif choice == "របាយការណ៍សរុប":
    st.subheader("📊 ទិន្នន័យអតិថិជន")
    st.dataframe(conn.read(worksheet="balances"))
