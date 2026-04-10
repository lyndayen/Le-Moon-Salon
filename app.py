import pandas as pd 
import streamlit as st
import sqlite3
import qrcode
import os
import requests
import cv2
import numpy as np

# --- SETTINGS ---
BOT_TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"
PACKAGES = {
    "កញ្ចប់សម្រស់ធម្មតា ($153)": 12,
    "កញ្ចប់សម្រស់ពិសេស ($204)": 12,
    "កញ្ចប់កក់សក់ធម្មតា ($54)": 28,
    "កញ្ចប់កក់សក់ពិសេស ($54)": 23
}

def get_connection(): return sqlite3.connect('salon.db')

def send_khmer_receipt(cust_id, pts, left, service):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT telegram_id, name FROM customers WHERE id = ?", (cust_id,))
    res = cur.fetchone(); conn.close()
    if res and res[0]:
        msg = (f"🌙 **Le Moon Salon - វិក្កយបត្រឌីជីថល** 🌙\n\n"
               f"អតិថិជន: **{res[1]}**\n"
               f"សេវាកម្ម: **{service}**\n"
               f"កាត់អស់: **{pts} ពិន្ទុ**\n"
               f"ពិន្ទុនៅសល់សរុប: **{left} ពិន្ទុ**\n\n"
               f"សូមអរគុណដែលបានគាំទ្រ! ❤️")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={"chat_id": res[0], "text": msg, "parse_mode": "Markdown"})

# --- UI ---
st.set_page_config(page_title="Le Moon Salon", layout="centered")
st.title("🌙 ប្រព័ន្ធគ្រប់គ្រងហាង Le Moon")

menu = ["ចុះឈ្មោះអតិថិជន", "ស្កេន QR កាត់ពិន្ទុ", "របាយការណ៍"]
choice = st.sidebar.selectbox("ម៉ឺនុយ", menu)

if choice == "ចុះឈ្មោះអតិថិជន":
    st.subheader("📝 ចុះឈ្មោះកញ្ចប់ថ្មី")
    name = st.text_input("ឈ្មោះអតិថិជន")
    phone = st.text_input("លេខទូរស័ព្ទ")
    pkg = st.selectbox("ជ្រើសរើសកញ្ចប់", list(PACKAGES.keys()))
    if st.button("រក្សាទុក"):
        conn = get_connection(); cur = conn.cursor()
        cur.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
        cid = cur.lastrowid
        cur.execute("INSERT INTO balances (customer_id, package_name, remaining_points, total_points) VALUES (?, ?, ?, ?)", 
                    (cid, pkg, PACKAGES[pkg], PACKAGES[pkg]))
        conn.commit()
        if not os.path.exists("qrcodes"): os.makedirs("qrcodes")
        qrcode.make(str(cid)).save(f"qrcodes/{cid}.png")
        st.success("ចុះឈ្មោះជោគជ័យ!")
        st.image(f"qrcodes/{cid}.png", caption="QR Code សម្រាប់ភ្ញៀវ")
        conn.close()

elif choice == "ស្កេន QR កាត់ពិន្ទុ":
    st.subheader("📷 ស្កេន QR របស់ភ្ញៀវ")
    img = st.camera_input("សូមថតរូប QR")
    if img:
        f_bytes = np.asarray(bytearray(img.read()), dtype=np.uint8)
        scanned_id, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imdecode(f_bytes, 1))
        if scanned_id:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT c.id, c.name, b.remaining_points FROM customers c JOIN balances b ON c.id = b.customer_id WHERE c.id = ?", (scanned_id,))
            res = cur.fetchone()
            if res:
                st.info(f"👤 អតិថិជន: {res[1]} | នៅសល់: {res[2]} ពិន្ទុ")
                svc = st.text_input("ឈ្មោះសេវាកម្ម (ឧទាហរណ៍: កក់សក់)")
                pts = st.number_input("ចំនួនពិន្ទុត្រូវកាត់", 1, res[2], 1)
                if st.button("បញ្ជាក់ការកាត់"):
                    new = res[2] - pts
                    cur.execute("UPDATE balances SET remaining_points = ? WHERE customer_id = ?", (new, res[0]))
                    cur.execute("INSERT INTO history (customer_id, service_type) VALUES (?, ?)", (res[0], f"{svc} ({pts} pts)"))
                    conn.commit()
                    send_khmer_receipt(res[0], pts, new, svc)
                    st.success("រួចរាល់!"); st.balloons()
            else: st.error("រកមិនឃើញអតិថិជន!")
            conn.close()

elif choice == "របាយការណ៍":
    st.subheader("📊 របាយការណ៍សរុប")
    conn = get_connection()
    df = pd.read_sql_query("SELECT c.name as ឈ្មោះ, b.package_name as កញ្ចប់, b.remaining_points as ពិន្ទុនៅសល់ FROM customers c JOIN balances b ON c.id = b.customer_id", conn)
    st.table(df)
    conn.close()