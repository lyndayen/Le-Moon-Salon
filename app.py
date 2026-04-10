import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import qrcode
import numpy as np
import cv2

# --- CONFIG ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- AUTO-REPAIR FUNCTION ---
def load_sheet(name, cols):
    try:
        df = conn.read(worksheet=name, ttl=0).dropna(how="all")
        if df.empty: return pd.DataFrame(columns=cols)
        return df
    except:
        return pd.DataFrame(columns=cols)

# --- LOAD PACKAGES ---
st.title("🌙 Le Moon Salon System")
settings_df = load_sheet("settings", ["package_name", "points"])
if settings_df.empty:
    st.error("⚠️ Please add packages to the 'settings' tab in Google Sheets first!")
    st.stop()
PACKAGES = dict(zip(settings_df['package_name'], settings_df['points']))

menu = ["ចុះឈ្មោះអតិថិជន (Register)", "កាត់ពិន្ទុ (Deduct Points)"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "ចុះឈ្មោះអតិថិជន (Register)":
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    pkg = st.selectbox("Package", list(PACKAGES.keys()))
    
    if st.button("Submit"):
        c_df = load_sheet("customers", ["id", "name", "phone", "telegram_id"])
        b_df = load_sheet("balances", ["customer_id", "package", "points"])
        
        new_id = len(c_df) + 1
        new_c = pd.DataFrame([{"id": new_id, "name": name, "phone": phone, "telegram_id": ""}])
        new_b = pd.DataFrame([{"customer_id": new_id, "package": pkg, "points": PACKAGES[pkg]}])
        
        conn.update(worksheet="customers", data=pd.concat([c_df, new_c], ignore_index=True))
        conn.update(worksheet="balances", data=pd.concat([b_df, new_b], ignore_index=True))
        
        st.success(f"Registered {name}!")
        st.image(np.array(qrcode.make(str(new_id))), caption=f"QR ID: {new_id}")

elif choice == "កាត់ពិន្ទុ (Deduct Points)":
    img = st.camera_input("Scan QR")
    if img:
        f_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
        scanned_id, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imdecode(f_bytes, 1))
        
        if scanned_id:
            c_df = load_sheet("customers", ["id", "name", "phone", "telegram_id"])
            b_df = load_sheet("balances", ["customer_id", "package", "points"])
            
            user = c_df[c_df['id'].astype(str) == str(scanned_id)]
            if not user.empty:
                c_name = user.iloc[0]['name']
                u_bal = b_df[b_df['customer_id'].astype(str) == str(scanned_id)]
                curr_pts = int(u_bal.iloc[0]['points'])
                
                st.info(f"Customer: {c_name} | Points: {curr_pts}")
                pts_to_cut = st.number_input("Deduct", 1, curr_pts, 1)
                
                if st.button("Confirm"):
                    b_df.loc[b_df['customer_id'].astype(str) == str(scanned_id), 'points'] = curr_pts - pts_to_cut
                    conn.update(worksheet="balances", data=b_df)
                    st.success("Points updated!"); st.balloons()
            else: st.error("User not found!")
