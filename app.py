import streamlit as st
import requests
import pandas as pd
import base64
import plotly.express as px
from urllib.parse import urlencode

# --- CONFIGURATION ---
st.set_page_config(page_title="Zoom Attendance Manager", page_icon="🎓", layout="wide")

# Load secrets securely
try:
    CLIENT_ID = st.secrets["zoom"]["client_id"]
    CLIENT_SECRET = st.secrets["zoom"]["client_secret"]
    REDIRECT_URI = st.secrets["zoom"]["redirect_uri"]
except FileNotFoundError:
    st.error("❌ Secrets file not found. Please create .streamlit/secrets.toml")
    st.stop()

# Zoom OAuth Endpoints
AUTHORIZE_URL = "https://zoom.us/oauth/authorize"
TOKEN_URL = "https://zoom.us/oauth/token"

# --- AUTHENTICATION FUNCTIONS ---

def get_login_url():
    """Generates the Zoom Login URL."""
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"

def exchange_code_for_token(auth_code):
    """Exchanges the authorization code for an access token."""
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    
    response = requests.post(TOKEN_URL, headers=headers, params=params)
    return response.json()

def get_current_user(token):
    """Fetches the logged-in user's profile."""
    url = "https://api.zoom.us/v2/users/me"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def get_attendance_report(token, meeting_id):
    """Fetches past meeting participants."""
    url = f"https://api.zoom.us/v2/report/meetings/{meeting_id}/participants"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 300}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('participants', []), None
    else:
        return None, response.text

# --- UI & LOGIC ---

def main():
    # 1. Check if we have an auth code in the URL (returned from Zoom)
    if "code" in st.query_params:
        auth_code = st.query_params["code"]
        with st.spinner("Logging you in..."):
            token_data = exchange_code_for_token(auth_code)
            
            if "access_token" in token_data:
                st.session_state["access_token"] = token_data["access_token"]
                # Clear URL parameters to prevent re-submission
                st.query_params.clear()
                st.rerun()
            else:
                st.error("Login failed. Please try again.")
                st.json(token_data)

    # 2. Main Interface
    if "access_token" not in st.session_state:
        # --- LOGIN SCREEN ---
        st.markdown("<div style='text-align: center; padding-top: 50px;'>", unsafe_allow_html=True)
        st.title("🎓 Course Attendance Tracker")
        st.write("Please sign in to access your Zoom reports.")
        
        # Login Button
        login_url = get_login_url()
        st.markdown(f"""
            <a href="{login_url}" target="_self">
                <button style="
                    background-color: #2D8CFF; 
                    color: white; 
                    padding: 12px 24px; 
                    border: none; 
                    border-radius: 8px; 
                    font-size: 16px; 
                    cursor: pointer; 
                    font-weight: bold;">
                    Login with Zoom
                </button>
            </a>
        """, unsafe_allow_html=True)
        
        st.info("🔒 Your credentials are secure. We only access read-only attendance data.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # --- DASHBOARD SCREEN ---
        token = st.session_state["access_token"]
        user_profile = get_current_user(token)
        
        # Sidebar
        with st.sidebar:
            if user_profile:
                # Use 'get' with a default fallback for the profile picture
                pic_url = user_profile.get('pic_url', 'https://via.placeholder.com/150')
                st.image(pic_url, width=50)
                st.write(f"**Logged in as:** {user_profile.get('first_name')} {user_profile.get('last_name')}")
                
            if st.button("Logout"):
                del st.session_state["access_token"]
                st.rerun()

        st.title("📊 Attendance Dashboard")

        # Input for Meeting ID
        st.write("Enter the Meeting ID of a **finished** course session to generate a report.")
        meeting_id = st.text_input("Meeting ID", placeholder="e.g., 8642219000")

        if meeting_id and st.button("Fetch Attendance"):
            with st.spinner("Pulling data from Zoom..."):
                participants, error = get_attendance_report(token, meeting_id)

                if participants:
                    # Process Data
                    df = pd.DataFrame(participants)
                    
                    # Handle duration (summing multiple joins for same email)
                    if 'user_email' in df.columns and 'duration' in df.columns:
                        summary = df.groupby(['user_email', 'name']).agg({
                            'duration': 'sum',
                            'join_time': 'min',
                            'leave_time': 'max'
                        }).reset_index()
                        
                        summary['duration_minutes'] = (summary['duration'] / 60).round(1)
                        summary = summary.sort_values('duration_minutes', ascending=False)

                        # Metrics
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Total Students", len(summary))
                        c1.caption("Unique participants")
                        
                        avg_time = summary['duration_minutes'].mean()
                        c2.metric("Avg. Duration", f"{avg_time:.1f} min")
                        
                        # Charts
                        fig = px.bar(summary.head(10), x='name', y='duration_minutes',
                                     title="Top Attendance Duration",
                                     labels={'duration_minutes': 'Minutes', 'name': 'Student'})
                        st.plotly_chart(fig, use_container_width=True)

                        # Table
                        st.dataframe(summary, use_container_width=True)

                        # CSV Download
                        csv = summary.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "📥 Download CSV Report",
                            csv,
                            f"attendance_{meeting_id}.csv",
                            "text/csv"
                        )
                    else:
                        st.warning("Participant emails or duration data missing. Check your Zoom plan permissions.")
                elif error:
                    st.error(f"Error: {error}")
                else:
                    st.info("No participants found for this ID.")

if __name__ == "__main__":
    main()
