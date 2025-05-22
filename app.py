import streamlit as st
from datetime import datetime
from PIL import Image

import gspread
from google.oauth2.service_account import Credentials

import smtplib
from email.mime.text import MIMEText
# Load your credentials from the secrets
import os
import json



# Page config
st.set_page_config(page_title="Emjay 2025 Wedding", layout="centered")

# Hide default Streamlit elements
hide_style = """
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 1. 📸 Landing Page
st.markdown("<h1 style='text-align: center;'>You're Invited!</h1>", unsafe_allow_html=True)
image = Image.open("assets/invite.jpg")
st.image(image, use_column_width=True)

# Divider
st.markdown("---")

# 2. 💌 RSVP Form
# This assumes you have your credentials JSON stored in Streamlit secrets as a JSON string
creds_json = st.secrets["google"]["creds"]

st.write("creds_json:", repr(creds_json))


st.text("DEBUG creds_json:")
st.text(creds_json)

creds_dict = json.loads(creds_json)

# Define scope and create credentials object
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)

# Connect to Google Sheets
gc = gspread.authorize(credentials)
sheet = gc.open("Wedding RSVPs").sheet1  

# Email credentials from secrets
EMAIL_ADDRESS = st.secrets["EMAIL_ADDRESS"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]

def send_confirmation_email(to_email, guest_name):
    subject = "Your RSVP Confirmation"
    body = f"Hi {guest_name},\n\nThank you for your RSVP! We look forward to seeing you at the event.\n\nBest regards,\nThe Wedding Team"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    # Gmail SMTP server
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())


# Streamlit form 
st.title("RSVP Form")
with st.form("rsvp_form"):
    name = st.text_input("Your Full Name")
    email = st.text_input("Your Email Address")
    attendance = st.selectbox("Will you attend?", ["Yes", "No", "Maybe"])
    Relation = st.selectbox("Are you acquainted with the bride or groom?", ["Bride", "Groom"])
    Group = st.selectbox("Which group do you belong to?", ["Tiny tots alumni", "VCM Alumni", "AUN Alumni", "SMC Alumni", "BSUTH staff", "Committee of friends Jay"]) 
    guests = st.number_input("How many guests will you bring (excluding yourself)?", min_value=0, max_value=2, step=1)
    message = st.text_area("Leave a message for the couple", placeholder="Optional...")
    
    submit = st.form_submit_button("Submit")

if submit:
    # Append a new row to the sheet
    sheet.append_row([name, email, attendance, Relation, Group, guests, message])
    send_confirmation_email(email, name)
    st.success("Thank you for your RSVP! A confirmation email has been sent.")

# Divider
st.markdown("---")

# 3. ⏳ Countdown Timer
st.subheader("Countdown to the Big Day 🎉")

wedding_date = datetime(2025, 4, 12)  # Set your wedding date here
now = datetime.now()
days_left = (wedding_date - now).days

if days_left > 0:
    st.markdown(f"### ⏳ {days_left} days to go!")
else:
    st.markdown("### 🎊 The wedding day has arrived or passed!")


