import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import qrcode
import os
import requests
import cv2
import numpy as np

# --- SETTINGS ---
BOT_TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 1. LOAD DYNAMIC PACKAGES FROM GOOGLE SHEET
try:
    settings_df = conn.read(worksheet="settings")
    PACKAGES = dict(zip(settings_df['package_name'], settings_df['points']))
except:
    # Fallback if settings tab is empty
    PACKAGES = {"សូមបញ្ចូលកញ្ចប់ក្នុង Google Sheet": 0}

def send_khmer_receipt(name, telegram_id, pts, left, service):
    if telegram_id and str(telegram_id).strip():
        msg = (f"🌙 **Le Moon Salon - វិក្កយបត្រឌីជីថល** 🌙\n\n"
               f"អតិថិជន: **{name}**\n"
               f"សេវាកម្ម: **{service}**\n"
               f"កាត់អស់: **{pts} ពិន្ទុ**\n"
               f"ពិន្ទុនៅសល់សរុប: **{left} ពិន្ទុ**\n\n"
               f"សូមអរគុណ! ❤️")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={"chat_id": telegram_id, "text": msg, "parse_mode": "Markdown"})

# --- UI ---
st.set_page_config(page_title="Le Moon Salon", layout="centered")
st.title("🌙 ប្រព័ន្ធគ្រប់គ្រង Le Moon")

menu = ["ចុះឈ្មោះអតិថិជន", "ស្កេន QR កាត់ពិន្ទុ", "របាយការណ៍"]
choice = st.sidebar.selectbox("ម៉ឺនុយ", menu)

if choice == "ចុះឈ្មោះអតិថិជន":
    st.subheader("📝 ចុះឈ្មោះកញ្ចប់ថ្មី")
    name = st.text_input("ឈ្មោះអតិថិជន")
    phone = st.text_input("លេខទូរស័ព្ទ")
    pkg = st.selectbox("ជ្រើសរើសកញ្ចប់ (ទាញចេញពី Google Sheet)", list(PACKAGES.keys()))
    
    if st.button("រក្សាទុកទិន្នន័យ"):
        # Load existing
        cust_df = conn.read(worksheet="customers")
        bal_df = conn.read(worksheet="balances")
        
        new_id = len(cust_df) + 1
        
        # Save Customer
        new_c = pd.DataFrame([{"id": new_id, "name": name, "phone": phone, "telegram_id": ""}])
        cust_df = pd.concat([cust_df, new_c], ignore_index=True)
        conn.update(worksheet="customers", data=cust_df)
        
        # Save Balance
        new_b = pd.DataFrame([{"customer_id": new_id, "package": pkg, "points": PACKAGES[pkg]}])
        bal_df = pd.concat([bal_df, new_b], ignore_index=True)
        conn.update(worksheet="balances", data=bal_df)
        
        # Generate QR
        if not os.path.exists("qrcodes"): os.makedirs("qrcodes")
        qrcode.make(str(new_id)).save(f"qrcodes/{new_id}.png")
        
        st.success("ចុះឈ្មោះបានជោគជ័យ!")
        st.image(f"qrcodes/{new_id}.png", caption=f"ID: {new_id}")

elif choice == "ស្កេន QR កាត់ពិន្ទុ":
    st.subheader("📷 ស្កេន QR Code")
    img = st.camera_input("ថតរូប QR")
    
    if img:
        f_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
        scanned_id, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imdecode(f_bytes, 1))
        
        if scanned_id:
            cust_df = conn.read(worksheet="customers")
            bal_df = conn.read(worksheet="balances")
            
            # Find User
            user = cust_df[cust_df['id'].astype(str) == str(scanned_id)]
            if not user.empty:
                c_name = user.iloc[0]['name']
                t_id = user.iloc[0]['telegram_id']
                
                # Find Balance
                u_bal = bal_df[bal_df['customer_id'].astype(str) == str(scanned_id)]
                current_pts = int(u_bal.iloc[0]['points'])
                
                st.info(f"👤 អតិថិជន: {c_name} | នៅសល់: {current_pts} ពិន្ទុ")
                svc = st.text_input("ឈ្មោះសេវាកម្ម")
                pts_to_use = st.number_input("កាត់ពិន្ទុ", 1, current_pts, 1)
                
                if st.button("បញ្ជាក់ការកាត់"):
                    new_pts = current_pts - pts_to_use
                    bal_df.loc[bal_df['customer_id'].astype(str) == str(scanned_id), 'points'] = new_pts
                    conn.update(worksheet="balances", data=bal_df)
                    
                    # Record History
                    hist_df = conn.read(worksheet="history")
                    new_h = pd.DataFrame([{"id": scanned_id, "name": c_name, "service": svc, "pts": pts_to_use}])
                    hist_df = pd.concat([hist_df, new_h], ignore_index=True)
                    conn.update(worksheet="history", data=hist_df)
                    
                    send_khmer_receipt(c_name, t_id, pts_to_use, new_pts, svc)
                    st.success("កាត់ពិន្ទុជោគជ័យ!")
                    st.balloons()
            else:
                st.error("រកមិនឃើញអតិថិជន!")

elif choice == "របាយការណ៍":
    st.subheader("📊 របាយការណ៍ការប្រើប្រាស់")
    hist_data = conn.read(worksheet="history")
    st.dataframe(hist_data)
