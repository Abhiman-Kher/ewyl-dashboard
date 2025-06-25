import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json

st.set_page_config(page_title="EWYL Mentor Login", layout="centered")

st.title("🔐 Login with Google (via Firebase)")

# ----------------------------
# STEP 1: Firebase + Login HTML/JS
# ----------------------------
firebase_login_html = """
<!-- Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/9.6.10/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.6.10/firebase-auth-compat.js"></script>

<script>
  // Firebase config
  const firebaseConfig = {
    apiKey: "AIzaSyA7SltxIng6oSmcUNlhI-lyUP7YujYz2OM",
    authDomain: "ewyl-dashboard.firebaseapp.com",
    projectId: "ewyl-dashboard",
    storageBucket: "ewyl-dashboard.appspot.com",
    messagingSenderId: "277872502542",
    appId: "1:277872502542:web:484a4eab0ff58bb9acd95f",
    measurementId: "G-PDNP0M4KJS"
  };

  // Init Firebase
  firebase.initializeApp(firebaseConfig);

  function googleLogin() {
    const provider = new firebase.auth.GoogleAuthProvider();
    firebase.auth().signInWithPopup(provider).then(result => {
      const user = result.user;
      const loginData = {
        email: user.email,
        name: user.displayName
      };
      window.parent.postMessage(JSON.stringify(loginData), "*");
    }).catch(error => {
      alert("Login failed: " + error.message);
    });
  }
</script>

<div style="text-align:center;">
  <button onclick="googleLogin()" style="padding:10px 20px; font-size:16px;">Login with Google</button>
</div>
"""

components.html(firebase_login_html, height=300)

st.markdown("---")
st.info("Please log in above to continue...")

# ----------------------------
# STEP 2: Capture Firebase Email
# ----------------------------
result = streamlit_js_eval(js_expressions="window.lastLogin", key="firebase_login")

if result and isinstance(result, str):
    try:
        login_data = json.loads(result)
        user_email = login_data.get("email", "").lower()
        user_name = login_data.get("name", "")
        st.success(f"✅ Welcome {user_name} ({user_email})")

        # ----------------------------
        # STEP 3: Load Google Sheets
        # ----------------------------
        SHEET_NAME = "Ewyl Tracker"

        creds = Credentials.from_service_account_file(
            "service_account.json",
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open(SHEET_NAME)

        data_df = pd.DataFrame(sh.worksheet("Sheet1").get_all_records())
        users_df = pd.DataFrame(sh.worksheet("Users").get_all_records())

        # ----------------------------
        # STEP 4: Match Email to Role
        # ----------------------------
        user_row = users_df[users_df["email"].str.lower() == user_email]
        if user_row.empty:
            st.error("❌ Unauthorized email. Please contact admin.")
            st.stop()

        role = user_row["role"].values[0]
        mentor_name = user_row["name"].values[0]

        # ----------------------------
        # STEP 5: Show Role-Based Data
        # ----------------------------
        if role == "admin":
            st.subheader("👑 Admin Dashboard - All Students")
            st.dataframe(data_df, use_container_width=True)

        elif role == "mentor":
            st.subheader(f"📘 {mentor_name}'s Students")
            filtered = data_df[data_df["EWYL Mentor"].str.lower() == mentor_name.lower()]
            st.dataframe(filtered, use_container_width=True)

        else:
            st.warning("⚠️ Unknown role. Please contact support.")

    except Exception as e:
        st.error(f"Error processing login: {e}")
        st.stop()

else:
    st.stop()
