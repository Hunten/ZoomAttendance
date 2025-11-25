import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import plotly.express as px
import base64

# --- CONFIGURATION & AUTHENTICATION ---
ST_PASSWORD = "admin"  # Change this to your desired login password

# Page Config
st.set_page_config(
    page_title="Zoom Attendance Tracker",
    page_icon="📊",
    layout="wide"
)

# --- ZOOM API FUNCTIONS ---

def get_zoom_access_token(account_id, client_id, client_secret):
    """Exchanges credentials for a temporary access token."""
    url = "https://zoom.us/oauth/token"
    auth_string = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "grant_type": "account_credentials",
        "account_id": account_id
    }
    
    try:
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        st.error(f"Authentication Failed: {str(e)}")
        return None

def get_past_meeting_participants(token, meeting_id):
    """Fetches participants from a finished meeting (Reports API)."""
    # This endpoint returns the most accurate 'duration' data for past meetings
    url = f"https://api.zoom.us/v2/report/meetings/{meeting_id}/participants"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page_size": 300} # Max page size
    
    all_participants = []
    
    while True:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            return None, res.text
            
        data = res.json()
        all_participants.extend(data.get('participants', []))
        
        if 'next_page_token' in data and data['next_page_token']:
            params['next_page_token'] = data['next_page_token']
        else:
            break
            
    return all_participants, None

def get_live_meeting_metrics(token, meeting_id):
    """Fetches real-time participants (Dashboard API)."""
    # Note: Requires Business/Education plan usually
    url = f"https://api.zoom.us/v2/metrics/meetings/{meeting_id}/participants"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"type": "live", "page_size": 300}
    
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json().get('participants', []), None
    else:
        return None, res.text

# --- UI HELPERS ---

def check_password():
    """Simple security check."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        st.markdown("### 🔒 Secure Access")
        pwd = st.text_input("Enter Access Password", type="password")
        if st.button("Login"):
            if pwd == ST_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
        return False
    return True

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- MAIN APPLICATION ---

def main():
    if not check_password():
        return

    # Sidebar: Credentials
    st.sidebar.header("⚙️ Zoom Settings")
    
    # Use secrets if available, otherwise inputs
    account_id = st.sidebar.text_input("Account ID", type="password", help="From Zoom App Marketplace")
    client_id = st.sidebar.text_input("Client ID", type="password")
    client_secret = st.sidebar.text_input("Client Secret", type="password")
    
    if not (account_id and client_id and client_secret):
        st.info("👈 Please enter your Zoom App Credentials in the sidebar to start.")
        st.markdown("""
        ### How to get credentials:
        1. Go to [Zoom App Marketplace](https://marketplace.zoom.us/)
        2. Create a **Server-to-Server OAuth** app.
        3. Copy Account ID, Client ID, and Client Secret.
        4. Add Scopes: `report:read:admin`, `dashboard:read:admin`.
        """)
        return

    # Authenticate
    if "zoom_token" not in st.session_state:
        if st.sidebar.button("Connect to Zoom"):
            token = get_zoom_access_token(account_id, client_id, client_secret)
            if token:
                st.session_state.zoom_token = token
                st.sidebar.success("Connected!")
                time.sleep(1)
                st.rerun()
    
    if "zoom_token" in st.session_state:
        st.sidebar.success("✅ Zoom Connected")
        if st.sidebar.button("Disconnect"):
            del st.session_state.zoom_token
            st.rerun()

        token = st.session_state.zoom_token

        # Tabs
        tab1, tab2 = st.tabs(["📊 Comprehensive Reports (Past)", "🔴 Real-time Dashboard (Live)"])

        # --- TAB 1: PAST REPORTS ---
        with tab1:
            st.markdown("### Session Tracking & Reports")
            st.markdown("Analyze attendance for finished sessions.")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                meeting_id_input = st.text_input("Enter Meeting ID (Past Session)", placeholder="e.g., 123456789")
            with col2:
                st.write("") # spacer
                st.write("")
                fetch_btn = st.button("Generate Report", type="primary")

            if fetch_btn and meeting_id_input:
                with st.spinner("Fetching attendance data from Zoom..."):
                    participants, error = get_past_meeting_participants(token, meeting_id_input)
                    
                    if error:
                        st.error(f"Error fetching data: {error}")
                    elif not participants:
                        st.warning("No participants found or meeting ID invalid.")
                    else:
                        # Process Data
                        df = pd.DataFrame(participants)
                        
                        # Clean and Calculate
                        if 'duration' in df.columns:
                            # Group by user_email to handle re-joins (sum duration)
                            summary_df = df.groupby(['user_email', 'name']).agg({
                                'duration': 'sum',
                                'join_time': 'min',
                                'leave_time': 'max'
                            }).reset_index()
                            
                            summary_df['duration_minutes'] = (summary_df['duration'] / 60).round(1)
                            summary_df = summary_df.sort_values('duration_minutes', ascending=False)

                            # Metrics
                            st.markdown("---")
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Total Participants", len(summary_df))
                            m2.metric("Avg. Duration", f"{summary_df['duration_minutes'].mean():.1f} min")
                            m3.metric("Top Attendee", summary_df.iloc[0]['name'])

                            # Chart
                            st.subheader("Engagement Overview")
                            fig = px.bar(summary_df.head(10), x='name', y='duration_minutes', 
                                        title="Top 10 Participants by Duration",
                                        labels={'duration_minutes': 'Minutes Attended', 'name': 'Participant'})
                            st.plotly_chart(fig, use_container_width=True)

                            # Data Table
                            st.subheader("Detailed Attendance Log")
                            st.dataframe(summary_df, use_container_width=True)

                            # Export
                            csv = convert_df_to_csv(summary_df)
                            st.download_button(
                                label="📥 Export to CSV",
                                data=csv,
                                file_name=f"attendance_report_{meeting_id_input}.csv",
                                mime="text/csv"
                            )
                        else:
                            st.warning("Duration data not available in this report type.")

        # --- TAB 2: LIVE DASHBOARD ---
        with tab2:
            st.markdown("### 🔴 Real-time Monitoring")
            st.markdown("Monitor active sessions currently in progress.")
            
            live_id_input = st.text_input("Enter Live Meeting ID", placeholder="e.g., 987654321")
            
            if st.button("Sync Live Data"):
                with st.spinner("Syncing with Zoom..."):
                    live_participants, error = get_live_meeting_metrics(token, live_id_input)
                    
                    if error:
                        st.error(f"Could not fetch live metrics. Note: Requires Zoom Business/Edu plan. Error: {error}")
                    elif not live_participants:
                        st.info("Meeting is not currently live or has no participants.")
                    else:
                        live_df = pd.DataFrame(live_participants)
                        
                        # Live Metrics
                        st.success(f"Sync Successful: {datetime.now().strftime('%H:%M:%S')}")
                        
                        k1, k2, k3 = st.columns(3)
                        k1.metric("Current Participants", len(live_df))
                        # Assuming 'device' or 'ip_address' fields exist in live metrics
                        if 'device' in live_df.columns:
                            mobile_users = live_df[live_df['device'].str.contains('Phone|Android|iOS', case=False, na=False)].shape[0]
                            k2.metric("Mobile Users", mobile_users)
                        
                        st.dataframe(live_df, use_container_width=True)

if __name__ == "__main__":
    main()
