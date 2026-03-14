import streamlit as st

st.set_page_config(
    page_title="Sentistrat Analytics",
    page_icon="🔬",
    layout="centered",
)

APP_NAME = "Sentistrat Analytics"
APP_DESCRIPTION = (
    "Strategies and tools designed to help you build long-term wealth through disciplined, "
    "risk-aware investing."
)


def login_page() -> None:
    st.title(APP_NAME)
    st.write(APP_DESCRIPTION)
    st.write(
        "Try our in-house research platform designed to bring institutional-grade investment "
        "analysis to retail investors."
    )

    with st.container(border=True):
        st.subheader("Member Login")
        st.write("Login with your WordPress account to access the app.")

        if getattr(st.user, "is_logged_in", False):
            st.success("You are logged in.")
            st.switch_page("pages/Home.py")
        else:
            if st.button("Login via WordPress", use_container_width=True):
                st.login("wordpress")

            st.subheader("No membership yet?")
            st.page_link("https://sentistrat.com/subscription", label="Go to subscription page", icon="↗️")


def main() -> None:
    login_page()


if __name__ == "__main__":
    main()
