import streamlit as st

def main():
    st.write("On Home Page.")

    if st.button("Log out", use_container_width=False):
        st.logout()

# Only shows when user logs in.       
if getattr(st.user, "is_logged_in", False):
    main()
else:
    st.switch_page("Login.py")

