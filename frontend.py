from datetime import date, datetime

import requests
import streamlit as st

BASE_URL = "https://realestate-crm-kugs.onrender.com"
STATUS_FLOW = ["new", "contacted", "closed"]


def get_auth_headers():
    token = st.session_state.get("token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def is_unauthorized(response: requests.Response) -> bool:
    return response.status_code in (401, 403)


def login_user(email: str, password: str):
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email.strip(), "password": password},
        timeout=10,
    )
    return response


def signup_user(email: str, password: str):
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json={"email": email.strip(), "password": password},
        timeout=10,
    )
    return response


def fetch_leads():
    response = requests.get(f"{BASE_URL}/leads", headers=get_auth_headers(), timeout=10)
    if is_unauthorized(response):
        raise PermissionError("Session expired or unauthorized. Please login again.")
    response.raise_for_status()
    return response.json()


def next_status(current_status: str) -> str:
    current = (current_status or "new").lower()
    if current in STATUS_FLOW:
        idx = STATUS_FLOW.index(current)
        return STATUS_FLOW[(idx + 1) % len(STATUS_FLOW)]
    return "new"


def format_follow_up(raw_value):
    if not raw_value:
        return "—"
    try:
        return datetime.fromisoformat(str(raw_value).replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return str(raw_value)


def update_lead_status(lead_id: int, status: str):
    endpoints = [
        ("patch", f"{BASE_URL}/leads/{lead_id}/status", {"status": status}),
        ("put", f"{BASE_URL}/leads/{lead_id}", {"status": status}),
    ]

    last_error = ""
    for method, url, payload in endpoints:
        try:
            response = requests.request(
                method,
                url,
                json=payload,
                headers=get_auth_headers(),
                timeout=10,
            )
            if response.status_code in (200, 201):
                return True, ""
            if is_unauthorized(response):
                return False, "Unauthorized. Please login again."
            last_error = response.text
        except requests.RequestException as exc:
            last_error = str(exc)
    return False, last_error


def render_auth():
    st.title("🔐 LeadNest")
    st.caption("Login or signup to access your CRM dashboard.")

    auth_mode = st.radio("Choose action", ["Login", "Signup"], horizontal=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if auth_mode == "Signup":
        if st.button("Signup", type="primary", use_container_width=True):
            if not email.strip() or not password:
                st.warning("Please enter both email and password.")
                return
            try:
                response = signup_user(email=email, password=password)
                if response.status_code in (200, 201):
                    st.success("Signup successful. You can now login.")
                else:
                    st.error(f"Signup failed: {response.text}")
            except requests.RequestException as exc:
                st.error(f"Error connecting to backend: {exc}")
    else:
        if st.button("Login", type="primary", use_container_width=True):
            if not email.strip() or not password:
                st.warning("Please enter both email and password.")
                return
            try:
                response = login_user(email=email, password=password)
                if response.status_code == 200:
                    payload = response.json()
                    token = payload.get("access_token")
                    if not token:
                        st.error("Login succeeded but token was missing in response.")
                        return
                    st.session_state["token"] = token
                    st.success("Login successful.")
                    st.rerun()
                elif is_unauthorized(response):
                    st.error("Invalid email or password.")
                else:
                    st.error(f"Login failed: {response.text}")
            except requests.RequestException as exc:
                st.error(f"Error connecting to backend: {exc}")


def logout():
    st.session_state.pop("token", None)
    st.success("Logged out successfully.")
    st.rerun()


def render_dashboard():
    st.title("🏠 LeadNest Dashboard")

    left_head, mid_head, right_head = st.columns([3, 1, 1])
    with left_head:
        st.caption("Manage leads, follow-ups, and quick status updates.")
    with mid_head:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with right_head:
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    st.markdown("---")
    st.subheader("➕ Add Lead")

    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Name")
    with col2:
        phone = st.text_input("Phone")
    with col3:
        follow_up = st.date_input("Follow-up Date", value=None)

    if st.button("Add Lead", type="primary"):
        if not name.strip() or not phone.strip():
            st.warning("Please enter both name and phone.")
        else:
            payload = {"name": name.strip(), "phone": phone.strip()}
            if follow_up:
                payload["follow_up_date"] = f"{follow_up.isoformat()}T09:00:00"
            try:
                response = requests.post(
                    f"{BASE_URL}/leads",
                    json=payload,
                    headers=get_auth_headers(),
                    timeout=10,
                )
                if response.status_code in (200, 201):
                    st.success("Lead added successfully.")
                    st.rerun()
                elif is_unauthorized(response):
                    st.warning("Unauthorized. Please login again.")
                else:
                    st.error(f"Failed to add lead: {response.text}")
            except requests.RequestException as exc:
                st.error(f"Error connecting to backend: {exc}")

    st.markdown("---")
    st.subheader("📋 All Leads")

    try:
        leads = fetch_leads()

        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            statuses = sorted({(lead.get("status") or "new").lower() for lead in leads})
            status_filter = st.selectbox("Filter by status", ["all"] + statuses)
        with filter_col2:
            only_today = st.checkbox("Only today's follow-ups")

        filtered_leads = leads
        if status_filter != "all":
            filtered_leads = [
                lead for lead in filtered_leads if (lead.get("status") or "new").lower() == status_filter
            ]

        if only_today:
            today_str = date.today().isoformat()
            filtered_leads = [
                lead
                for lead in filtered_leads
                if format_follow_up(lead.get("follow_up_date")) == today_str
            ]

        if filtered_leads:
            table_rows = [
                {
                    "Name": lead.get("name", ""),
                    "Phone": lead.get("phone", ""),
                    "Status": (lead.get("status") or "new").title(),
                    "Follow-up Date": format_follow_up(lead.get("follow_up_date")),
                }
                for lead in filtered_leads
            ]
            st.table(table_rows)

            st.markdown("#### 🔁 Quick Status Update")
            for lead in filtered_leads:
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                current_status = (lead.get("status") or "new").lower()
                target_status = next_status(current_status)

                with c1:
                    st.write(lead.get("name", "Unknown"))
                with c2:
                    st.write(current_status.title())
                with c3:
                    st.write(f"→ {target_status.title()}")
                with c4:
                    if st.button(
                        f"Update #{lead.get('id')}",
                        key=f"status_{lead.get('id')}",
                        use_container_width=True,
                    ):
                        ok, error = update_lead_status(lead.get("id"), target_status)
                        if ok:
                            st.success(f"Updated {lead.get('name')} to {target_status}.")
                            st.rerun()
                        else:
                            st.warning(f"Status update failed: {error}")
        else:
            st.info("No leads match the current filters.")

    except PermissionError as exc:
        st.warning(str(exc))
    except requests.RequestException as exc:
        st.error(f"Error connecting to backend: {exc}")

    st.markdown("---")
    st.subheader("📅 Today Follow-ups")

    try:
        followups_response = requests.get(
            f"{BASE_URL}/leads/today-followups",
            headers=get_auth_headers(),
            timeout=10,
        )
        if followups_response.status_code == 200:
            followups = followups_response.json()
            if followups:
                st.table(
                    [
                        {
                            "Name": lead.get("name", ""),
                            "Phone": lead.get("phone", ""),
                            "Status": (lead.get("status") or "new").title(),
                            "Follow-up Date": format_follow_up(lead.get("follow_up_date")),
                        }
                        for lead in followups
                    ]
                )
            else:
                st.info("No follow-ups for today.")
        elif is_unauthorized(followups_response):
            st.warning("Unauthorized. Please login again.")
        else:
            st.error(f"Failed to fetch today follow-ups: {followups_response.text}")
    except requests.RequestException as exc:
        st.error(f"Error connecting to backend: {exc}")


if "token" not in st.session_state:
    st.session_state["token"] = None

if st.session_state.get("token"):
    render_dashboard()
else:
    render_auth()
