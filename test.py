import streamlit as st

st.set_page_config(page_title="SentiStrat")

if not st.user.is_logged_in:
    st.title("Sentistrat Analytics")
    if st.button("Login with Sentistrat", type="primary"):
        st.login("wordpress")
    st.stop()

st.success("Logged in successfully.")
st.write("User info:")
st.json(dict(st.user))

if st.button("Logout"):
    st.logout()