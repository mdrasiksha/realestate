from datetime import date, datetime

import requests
import streamlit as st

BASE_URL = "https://realestate-crm-kugs.onrender.com"
STATUS_OPTIONS = ["new", "contacted", "closed"]
STATUS_LABELS = {"new": "New", "contacted": "Contacted", "closed": "Closed"}


st.set_page_config(page_title="LeadNest CRM", page_icon="🏢", layout="wide")


def get_auth_headers():
    token = st.session_state.get("token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def is_unauthorized(response: requests.Response) -> bool:
    return response.status_code in (401, 403)


def login_user(email: str, password: str):
    return requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email.strip(), "password": password},
        timeout=10,
    )


def signup_user(email: str, password: str):
    return requests.post(
        f"{BASE_URL}/auth/signup",
        json={"email": email.strip(), "password": password},
        timeout=10,
    )


def fetch_leads():
    response = requests.get(f"{BASE_URL}/leads", headers=get_auth_headers(), timeout=10)
    if is_unauthorized(response):
        raise PermissionError("Session expired or unauthorized. Please login again.")
    response.raise_for_status()
    return response.json()


def fetch_today_followups():
    response = requests.get(
        f"{BASE_URL}/leads/today-followups",
        headers=get_auth_headers(),
        timeout=10,
    )
    if is_unauthorized(response):
        raise PermissionError("Session expired or unauthorized. Please login again.")
    response.raise_for_status()
    return response.json()


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


def add_lead(name: str, phone: str, follow_up):
    payload = {"name": name.strip(), "phone": phone.strip(), "status": "new"}
    if follow_up:
        payload["follow_up_date"] = f"{follow_up.isoformat()}T09:00:00"

    response = requests.post(
        f"{BASE_URL}/leads",
        json=payload,
        headers=get_auth_headers(),
        timeout=10,
    )
    return response


def logout():
    st.session_state.pop("token", None)
    st.success("Logged out successfully.")
    st.rerun()


def normalize_rows(leads):
    return [
        {
            "Name": lead.get("name", ""),
            "Phone": lead.get("phone", ""),
            "Status": STATUS_LABELS.get((lead.get("status") or "new").lower(), "New"),
            "Follow-up date": format_follow_up(lead.get("follow_up_date")),
        }
        for lead in leads
    ]


def render_auth():
    st.title("🔐 LeadNest")
    st.caption("Enterprise-ready lead management, follow-ups, and deal tracking.")

    auth_mode = st.radio("Choose action", ["Login", "Signup"], horizontal=True)
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input("Email")
    with col2:
        password = st.text_input("Password", type="password")

    if auth_mode == "Signup":
        if st.button("Create account", type="primary", use_container_width=True):
            if not email.strip() or not password:
                st.warning("Please enter both email and password.")
                return
            try:
                response = signup_user(email=email, password=password)
                if response.status_code == 200:
                    st.success("Signup successful! Please login.")
                else:
                    try:
                        payload = response.json()
                        message = payload.get("detail") or payload.get("message") or response.text
                    except ValueError:
                        message = response.text or "Signup failed."
                    st.error(message)
            except requests.RequestException as exc:
                st.error(f"Could not reach the server: {exc}")
    else:
        if st.button("Login", type="primary", use_container_width=True):
            if not email.strip() or not password:
                st.warning("Please enter both email and password.")
                return
            try:
                response = login_user(email=email, password=password)
                if response.status_code == 200:
                    token = response.json().get("access_token")
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


def render_dashboard_page(leads, today_followups):
    st.title("📊 Dashboard")
    st.caption("Quick snapshot of your sales pipeline.")

    total_leads = len(leads)
    total_today_followups = len(today_followups)
    total_closed_deals = sum(1 for lead in leads if (lead.get("status") or "").lower() == "closed")

    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Total Leads", total_leads)
    c2.metric("📅 Today Follow-ups", total_today_followups)
    c3.metric("🤝 Closed Deals", total_closed_deals)

    st.markdown("### 🧾 Pipeline Preview")
    st.dataframe(normalize_rows(leads[:10]), use_container_width=True, hide_index=True)


def render_leads_page(leads):
    st.title("🧲 Leads")
    st.caption("Manage leads, update statuses, and create new opportunities.")

    with st.container(border=True):
        st.markdown("#### ➕ Add Lead")
        a1, a2, a3, a4 = st.columns([2, 2, 2, 1])
        with a1:
            name = st.text_input("Name", key="new_lead_name")
        with a2:
            phone = st.text_input("Phone", key="new_lead_phone")
        with a3:
            follow_up = st.date_input("Follow-up date", value=None, key="new_lead_follow_up")
        with a4:
            st.write("")
            st.write("")
            submit = st.button("Add", type="primary", use_container_width=True)

        if submit:
            if not name.strip() or not phone.strip():
                st.warning("Please enter both name and phone.")
            else:
                try:
                    response = add_lead(name, phone, follow_up)
                    if response.status_code in (200, 201):
                        st.success("Lead added successfully.")
                        st.rerun()
                    elif is_unauthorized(response):
                        st.warning("Unauthorized. Please login again.")
                    else:
                        st.error(f"Failed to add lead: {response.text}")
                except requests.RequestException as exc:
                    st.error(f"Error connecting to backend: {exc}")

    st.markdown("#### 📋 Leads Table")
    st.dataframe(normalize_rows(leads), use_container_width=True, hide_index=True)

    st.markdown("#### 🔁 Lead Actions")
    for lead in leads:
        row1, row2, row3, row4 = st.columns([2, 2, 2, 1])
        lead_name = lead.get("name", "Unknown")
        lead_id = lead.get("id")
        current_status = (lead.get("status") or "new").lower()
        if current_status not in STATUS_OPTIONS:
            current_status = "new"

        with row1:
            st.write(f"**{lead_name}**")
        with row2:
            st.caption(f"Current: {STATUS_LABELS[current_status]}")
        with row3:
            selected = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(current_status),
                format_func=lambda x: STATUS_LABELS[x],
                key=f"status_select_{lead_id}",
                label_visibility="collapsed",
            )
        with row4:
            if st.button("Save", key=f"status_save_{lead_id}", use_container_width=True):
                ok, error = update_lead_status(lead_id, selected)
                if ok:
                    st.success(f"Updated {lead_name} to {STATUS_LABELS[selected]}.")
                    st.rerun()
                else:
                    st.warning(f"Status update failed: {error}")


def render_followups_page(today_followups):
    st.title("📞 Follow-ups")
    st.caption("Focus on today's scheduled conversations.")

    if today_followups:
        st.dataframe(normalize_rows(today_followups), use_container_width=True, hide_index=True)
    else:
        st.info("No follow-ups scheduled for today.")


def render_settings_page():
    st.title("⚙️ Settings")
    st.caption("Simple workspace controls.")

    st.info("Profile and workspace settings can be expanded here.")


def render_app():
    try:
        leads = fetch_leads()
        today_followups = fetch_today_followups()
    except PermissionError as exc:
        st.warning(str(exc))
        if st.button("Back to Login"):
            logout()
        return
    except requests.RequestException as exc:
        st.error(f"Error connecting to backend: {exc}")
        return

    st.sidebar.title("🏢 LeadNest")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Leads", "Follow-ups", "Settings"],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    s1, s2 = st.sidebar.columns(2)
    with s1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with s2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()

    if page == "Dashboard":
        render_dashboard_page(leads, today_followups)
    elif page == "Leads":
        render_leads_page(leads)
    elif page == "Follow-ups":
        render_followups_page(today_followups)
    else:
        render_settings_page()


if "token" not in st.session_state:
    st.session_state["token"] = None

if st.session_state.get("token"):
    render_app()
else:
    render_auth()
