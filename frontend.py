import requests
import streamlit as st

BASE_URL = "https://realestate-crm-kugs.onrender.com"

st.title("Real Estate CRM Dashboard")

st.header("Add Lead")
name = st.text_input("Name")
phone = st.text_input("Phone")

if st.button("Add Lead"):
    if not name.strip() or not phone.strip():
        st.write("Please enter both name and phone.")
    else:
        try:
            response = requests.post(
                f"{BASE_URL}/leads",
                json={"name": name.strip(), "phone": phone.strip()},
                timeout=10,
            )
            if response.status_code in (200, 201):
                st.success("Lead added successfully.")
            else:
                st.write(f"Failed to add lead: {response.text}")
        except requests.RequestException as exc:
            st.write(f"Error connecting to backend: {exc}")

st.header("All Leads")
try:
    leads_response = requests.get(f"{BASE_URL}/leads", timeout=10)
    if leads_response.status_code == 200:
        leads = leads_response.json()
        if leads:
            st.table([{"Name": lead.get("name", ""), "Phone": lead.get("phone", "")} for lead in leads])
        else:
            st.write("No leads found.")
    else:
        st.write(f"Failed to fetch leads: {leads_response.text}")
except requests.RequestException as exc:
    st.write(f"Error connecting to backend: {exc}")

st.header("Today Follow-ups")
try:
    followups_response = requests.get(f"{BASE_URL}/leads/today-followups", timeout=10)
    if followups_response.status_code == 200:
        followups = followups_response.json()
        if followups:
            st.table(
                [
                    {"Name": lead.get("name", ""), "Phone": lead.get("phone", "")}
                    for lead in followups
                ]
            )
        else:
            st.write("No follow-ups for today.")
    else:
        st.write(f"Failed to fetch today follow-ups: {followups_response.text}")
except requests.RequestException as exc:
    st.write(f"Error connecting to backend: {exc}")
