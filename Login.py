import smtplib
import streamlit as st
from email.message import EmailMessage

st.set_page_config(
    page_title="Sentistrat ANALYTICS",
    page_icon="🔬",
    layout="centered",
)


APP_NAME = "Sentistrat ANALYTICS"
APP_DESCRIPTION = (
    "Toolbox to help you build long-term wealth through disciplined, "
    "risk-aware investing. Our in-house research platform is designed to bring " 
    "institutional-grade investment analysis to retail investors at a marginal cost."
)

STUDENT_REQUEST_EMAIL = "ram@sentistrat.com"


def send_student_request(name: str, email: str, institution: str, message: str) -> None:
    smtp_host = st.secrets["smtp"]["host"]
    smtp_port = int(st.secrets["smtp"]["port"])
    smtp_username = st.secrets["smtp"]["username"]
    smtp_password = st.secrets["smtp"]["password"]
    from_email = st.secrets["smtp"].get("from_email", smtp_username)
    use_starttls = bool(st.secrets["smtp"].get("use_starttls", True))

    body = f"""
        New student access request for Sentistrat Analytics

        Name: {name}
        Email: {email}
        Institution: {institution}

        Message:
        {message}
        """.strip()

    msg = EmailMessage()
    msg["Subject"] = "Student Login Request - Sentistrat Analytics"
    msg["From"] = from_email
    msg["To"] = STUDENT_REQUEST_EMAIL
    msg["Reply-To"] = email
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if use_starttls:
            server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)


def login_page() -> None:
    st.title(APP_NAME, text_alignment="center")
    st.write(APP_DESCRIPTION)
    st.write(
        ""
    )
    st.space()

    col1, col2 = st.columns(2, gap='large')
    with col1:
        with st.container(border=True):
            st.subheader("Member Login")
            st.write("All members with an active Sentistrat subscription (Learner, Strategist, Visionary)")

            if getattr(st.user, "is_logged_in", False):
                st.success("You are logged in.")
                st.switch_page("pages/Home.py")
            else:
                if st.button("Login via WordPress", use_container_width=True):
                    st.login("wordpress")

        with st.container(border=True):
            st.subheader("No membership yet?")
            st.link_button('Purchase Subscription',"https://www.sentistrat.com", use_container_width=True)

    with col2:
        with st.container(border=True):
            st.subheader("Copier/Student Login")
            st.write("To obtain a free subscription, please submit your details for review.")
            
            with st.expander(label="Show Request Form"):
                with st.form("student_login_form", clear_on_submit=True, border=False):
                    name = st.text_input("Full name*", placeholder="Name or eToro username", help="For copiers from eToro please enter the username of the profile that is used to copy @marirs.")
                    email = st.text_input("Email*", placeholder="example@domain.com")
                    institution = st.text_input("Institution*", placeholder="University or eToro")
                    message = st.text_area("Why are you requesting access?", placeholder="Few words on how the tooling will help you.",height=120)
                    submitted = st.form_submit_button("Submit", use_container_width=True)

            if submitted:
                if not name.strip() or not email.strip() or not institution.strip():
                    st.error("Please fill in your name, email, and institution.")
                else:
                    try:
                        send_student_request(name.strip(), email.strip(), institution.strip(), message.strip())
                        st.success("We will reachout to you after reviewing your request.")
                    except Exception:
                        st.error("Unable to submit your request right now. Please try again later.")



def main() -> None:
    login_page()


if __name__ == "__main__":
    main()
