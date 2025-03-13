import streamlit as st
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
import time

WABILI_ICON = str(Path(fr"C:\Users\James\Documents\codingProjects\wabalanalytics\data\wabiliIcon.png"))
st.set_page_config(
    page_title="Suggestions 📧",
    page_icon=WABILI_ICON,
    layout="wide")
st.title("Suggestions 📧")

st.write("""I've loved making this app for you but I need to hear how you want to improve
         Wabilanalytics! Even if it's just changing the font color! I love you!!
          - James
        """)
st.write("""
         """)


# Taking inputs
email_sender = st.text_input('From', help="""
                             Google requires you to use an email with 2 factor authentication so you'll need to follow some steps
                             to get a password just for this app. You can find the steps [here](https://support.google.com/accounts/answer/185833?hl=en).
        """)
suggestion = st.text_area('Suggestion')
password = st.text_input('Password', type="password", 
                         help="""Go to you google account. \n On the left navigation panel, click on Security.
                        Under Signing in to Google, select App Passwords. You might need to sign in again.
                        At the bottom, choose the app and device you want the app password for, then select Generate and use this password""") 

if st.button("Send Email"):
    try:
        msg = MIMEText('Wabalanalytics Suggestion \n' + suggestion)
        msg['From'] = email_sender
        msg['To'] = 'jamesmarsh99@berkeley.edu'
        msg['Subject'] = 'James is the best boyfriend in the world'

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_sender, password)
        server.sendmail(email_sender, 'jamesmarsh99@berkeley.edu', msg.as_string())
        server.quit()
        with st.spinner("🚮 Please wait while we send your suggestion to the trash..."):
            time.sleep(7)
        st.success('Email sent successfully! Please wait while James needs to dig through the trash to find your '
                   ' suggestion 🚀')
    except Exception as e:
        st.error(f"Error sending email: {e}")
