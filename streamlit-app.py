import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import json

st.set_page_config(page_title="EWYL Mentor Login", layout="centered")
st.title("🔐 Login with Google (GSI - No Firebase)")

client_id = "580398234002-e3haoistiqj5hqs9p7o6sss7uqiauf22.apps.googleusercontent.com"  # ⬅️ Replace this

google_login_html = f"""
<script src="https://accounts.google.com/gsi/client" async defer></script>
<div id="g_id_onload"
     data-client_id="{client_id}"
     data-context="signin"
     data-ux_mode="popup"
     data-callback="handleCredentialResponse"
     data-auto_prompt="false">
</div>
<div class="g_id_signin"
     data-type="standard"
     data-shape="rectangular"
     data-theme="outline"
     data-text="sign_in_with"
     data-size="large"
     data-logo_alignment="left">
</div>

<script>
  function handleCredentialResponse(response) {{
    const base64Url = response.credential.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {{
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }}).join(''));
    const user = JSON.parse(jsonPayload);
    const userInfo = {{
        email: user.email,
        name: user.name
    }};
    window.parent.postMessage(JSON.stringify(userInfo), "*");
  }}
</script>
"""

components.html(google_login_html, height=400)

result = streamlit_js_eval(js_expressions="window.lastLogin", key="google_login")

if result and isinstance(result, str):
    try:
        login_data = json.loads(result)
        user_email = login_data.get("email", "").lower()
        user_name = login_data.get("name", "")
        st.success(f"✅ Welcome {user_name} ({user_email})")

        # Use user_email in your logic here

    except Exception as e:
        st.error(f"Login error: {e}")
else:
    st.info("Please log in to continue.")
