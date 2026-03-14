import base64
import os
from typing import Optional

import streamlit as st

# -------------------------------------------------------
# Sentistrat Analytics - Streamlit Landing + WP Login App
# -------------------------------------------------------
# Notes:
# 1. This version uses Streamlit's native OpenID Connect (OIDC) login flow.
# 2. Your WordPress site acts as the identity provider through its OIDC server plugin.
# 3. The app reads the user's email claim from st.user after login.
# 4. If login fails or the email is not authorized, the app routes the user to the subscription page.
# 5. A PNG/JPG background can be uploaded directly from the login page.
# -------------------------------------------------------

st.set_page_config(
    page_title="Sentistrat Analytics",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------
# Configuration
# -------------------------
APP_NAME = "Sentistrat Analytics"
APP_TAGLINE = "Strategies and tools designed to help you build long-term wealth through disciplined, risk-aware investing."
HERO_TEXT = (
    "Try our in-house research platform designed to bring institutional-grade investment analysis to retail investors. "
    "It provides advanced tools for portfolio optimization, valuation modeling, and data-driven decision making using rigorous quantitative methods. "
    "By integrating years of historical financial data with flexible modeling frameworks such as discounted cash flow analysis, "
    "the platform enables investors to test assumptions, evaluate scenarios, and build research that approaches the depth and discipline "
    "typically reserved for professional asset managers."
)

# Set these as environment variables in deployment, or edit directly.
WORDPRESS_BASE_URL = os.getenv("WORDPRESS_BASE_URL", "https://sentistrat.com")
SUBSCRIPTION_URL = os.getenv("SUBSCRIPTION_URL", f"{WORDPRESS_BASE_URL.rstrip('/')}/subscription")

# Optional authorization guardrails after OIDC login.
# Use one or both depending on how your WordPress/OIDC setup identifies entitled users.
ALLOWED_EMAILS = {
    email.strip().lower()
    for email in os.getenv("ALLOWED_EMAILS", "").split(",")
    if email.strip()
}
ALLOWED_EMAIL_DOMAINS = {
    domain.strip().lower().lstrip("@")
    for domain in os.getenv("ALLOWED_EMAIL_DOMAINS", "").split(",")
    if domain.strip()
}

ORANGE = "#F97316"
DARK_ORANGE = "#C2410C"
SOFT_ORANGE = "#FFF7ED"
WHITE = "#FFFFFF"
TEXT_DARK = "#111827"
MUTED = "#6B7280"
BORDER = "rgba(249, 115, 22, 0.18)"

# -------------------------
# Session state
# -------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "wp_user" not in st.session_state:
    st.session_state.wp_user = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "login_error" not in st.session_state:
    st.session_state.login_error = None
if "login_bg_bytes" not in st.session_state:
    st.session_state.login_bg_bytes = None
if "route_to_subscription" not in st.session_state:
    st.session_state.route_to_subscription = False


# -------------------------
# Helpers
# -------------------------
def _to_base64(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode()


def apply_global_css(background_bytes: Optional[bytes] = None) -> None:
    background_css = ""
    overlay_css = "background: linear-gradient(135deg, rgba(255,255,255,0.92), rgba(255,247,237,0.88));"

    if background_bytes:
        encoded = _to_base64(background_bytes)
        background_css = f"""
        .stApp {{
            background-image:
                linear-gradient(135deg, rgba(255,255,255,0.84), rgba(255,247,237,0.86)),
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        """
    else:
        background_css = f"""
        .stApp {{
            background:
                radial-gradient(circle at top right, rgba(249,115,22,0.10), transparent 25%),
                linear-gradient(180deg, #ffffff 0%, #fffaf5 100%);
        }}
        """

    st.markdown(
        f"""
        <style>
        {background_css}

        html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            color: {TEXT_DARK};
        }}

        [data-testid="stHeader"] {{
            background: rgba(255,255,255,0);
        }}

        [data-testid="stSidebar"] {{
            background: {WHITE};
            border-right: 1px solid {BORDER};
        }}

        .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 2rem;
        }}

        .topbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            padding: 0.25rem 0 1rem 0;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
            font-weight: 800;
            font-size: 1.15rem;
            letter-spacing: 0.2px;
            color: {TEXT_DARK};
        }}

        .brand-badge {{
            width: 42px;
            height: 42px;
            border-radius: 12px;
            background: linear-gradient(135deg, {ORANGE}, {DARK_ORANGE});
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            box-shadow: 0 12px 28px rgba(249, 115, 22, 0.28);
        }}

        .hero-wrap {{
            display: grid;
            grid-template-columns: 1.2fr 0.85fr;
            gap: 1.4rem;
            margin-top: 0.8rem;
            align-items: stretch;
        }}

        .glass-card {{
            border-radius: 28px;
            padding: 2rem;
            border: 1px solid {BORDER};
            background: rgba(255,255,255,0.82);
            backdrop-filter: blur(10px);
            box-shadow: 0 24px 60px rgba(17, 24, 39, 0.08);
        }}

        .login-card {{
            border-radius: 28px;
            padding: 1.5rem;
            border: 1px solid {BORDER};
            {overlay_css}
            box-shadow: 0 24px 60px rgba(17, 24, 39, 0.08);
        }}

        .pill {{
            display: inline-block;
            padding: 0.38rem 0.82rem;
            background: {SOFT_ORANGE};
            border: 1px solid {BORDER};
            border-radius: 999px;
            color: {DARK_ORANGE};
            font-size: 0.84rem;
            font-weight: 700;
            margin-bottom: 0.9rem;
        }}

        .hero-title {{
            font-size: clamp(2.3rem, 4vw, 4.3rem);
            line-height: 1.03;
            font-weight: 900;
            letter-spacing: -0.03em;
            margin: 0 0 1rem 0;
            color: {TEXT_DARK};
        }}

        .hero-subtitle {{
            font-size: 1.08rem;
            line-height: 1.8;
            color: {MUTED};
            margin-bottom: 1.3rem;
        }}

        .metric-row {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 1rem;
        }}

        .metric-card {{
            border-radius: 20px;
            padding: 1rem;
            background: {WHITE};
            border: 1px solid {BORDER};
        }}

        .metric-kpi {{
            font-weight: 900;
            color: {ORANGE};
            font-size: 1.2rem;
            margin-bottom: 0.15rem;
        }}

        .metric-label {{
            font-size: 0.9rem;
            color: {MUTED};
        }}

        .section-title {{
            font-weight: 800;
            font-size: 1.6rem;
            margin: 0.2rem 0 1rem 0;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}

        .feature-card {{
            border-radius: 22px;
            padding: 1.2rem;
            background: rgba(255,255,255,0.9);
            border: 1px solid {BORDER};
            min-height: 180px;
        }}

        .feature-title {{
            font-size: 1.03rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }}

        .feature-text {{
            color: {MUTED};
            line-height: 1.65;
            font-size: 0.95rem;
        }}

        .footer-note {{
            margin-top: 1.2rem;
            color: {MUTED};
            font-size: 0.92rem;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, {ORANGE}, {DARK_ORANGE});
            color: white;
            border: none;
            border-radius: 14px;
            font-weight: 800;
            min-height: 2.9rem;
            padding: 0.65rem 1rem;
            box-shadow: 0 16px 35px rgba(249, 115, 22, 0.24);
        }}

        .stButton > button:hover {{
            filter: brightness(0.98);
        }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stPasswordInput"] input {{
            border-radius: 14px !important;
            border: 1px solid rgba(249, 115, 22, 0.24) !important;
            background: rgba(255,255,255,0.9) !important;
        }}

        .subscribe-box {{
            border-radius: 28px;
            padding: 2rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,247,237,0.96));
            border: 1px solid {BORDER};
            box-shadow: 0 24px 60px rgba(17, 24, 39, 0.08);
        }}

        @media (max-width: 980px) {{
            .hero-wrap, .feature-grid, .metric-row {{
                grid-template-columns: 1fr;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def topbar() -> None:
    st.markdown(
        f"""
        <div class="topbar">
            <div class="brand">
                <div class="brand-badge">SA</div>
                <div>{APP_NAME}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_logged_in_user_email() -> Optional[str]:
    try:
        email = st.user.get("email")
    except Exception:
        email = None
    if email:
        return str(email).strip().lower()
    return None


def get_logged_in_user_name() -> str:
    for key in ["name", "given_name", "preferred_username", "nickname", "email"]:
        try:
            value = st.user.get(key)
        except Exception:
            value = None
        if value:
            return str(value)
    return "Member"


def is_email_authorized(email: Optional[str]) -> bool:
    if not email:
        return False

    email = email.lower()
    domain = email.split("@")[-1] if "@" in email else ""

    # If no restrictions are configured, any valid OIDC login is accepted.
    if not ALLOWED_EMAILS and not ALLOWED_EMAIL_DOMAINS:
        return True

    if email in ALLOWED_EMAILS:
        return True
    if domain and domain in ALLOWED_EMAIL_DOMAINS:
        return True
    return False


def sync_auth_state_from_oidc() -> None:
    is_logged_in = getattr(st.user, "is_logged_in", False)
    if not is_logged_in:
        st.session_state.authenticated = False
        st.session_state.wp_user = None
        st.session_state.user_email = None
        return

    email = get_logged_in_user_email()
    display_name = get_logged_in_user_name()

    if is_email_authorized(email):
        st.session_state.authenticated = True
        st.session_state.wp_user = display_name
        st.session_state.user_email = email
        st.session_state.login_error = None
        st.session_state.route_to_subscription = False
    else:
        st.session_state.authenticated = False
        st.session_state.wp_user = None
        st.session_state.user_email = email
        st.session_state.login_error = (
            "Login succeeded, but this email does not have access to Sentistrat Analytics."
        )
        st.session_state.route_to_subscription = True
def logout() -> None:
    st.session_state.authenticated = False
    st.session_state.wp_user = None
    st.session_state.user_email = None
    st.session_state.login_error = None
    st.session_state.route_to_subscription = False
    st.logout()


def login_page() -> None:
    topbar()
    sync_auth_state_from_oidc()

    uploaded_bg = st.file_uploader(
        "Upload background image for login page (PNG or JPG)",
        type=["png", "jpg", "jpeg"],
        help="Optional. This lets you visually brand the landing/login page without changing the code.",
    )

    if uploaded_bg is not None:
        st.session_state.login_bg_bytes = uploaded_bg.read()
        st.rerun()

    left, right = st.columns([1.45, 0.85], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="pill">Institutional-grade research for retail investors</div>
                <div class="hero-title">Build wealth with discipline, evidence, and risk control.</div>
                <div class="hero-subtitle">
                    <strong>{APP_TAGLINE}</strong><br><br>
                    {HERO_TEXT}
                </div>
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-kpi">Portfolio</div>
                        <div class="metric-label">Optimization with risk-aware allocation logic</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-kpi">Valuation</div>
                        <div class="metric-label">Scenario-based DCF and assumption testing</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-kpi">Research</div>
                        <div class="metric-label">Historical data-driven decision support</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("### Member Login")
        st.caption("Access your Sentistrat Analytics workspace using your WordPress OIDC account.")

        st.markdown(
            "This app uses your WordPress OIDC server for authentication. After login, the app reads your verified identity claims and uses your email to determine access."
        )

        if getattr(st.user, "is_logged_in", False):
            sync_auth_state_from_oidc()
            if st.session_state.authenticated:
                st.success(f"Welcome, {st.session_state.wp_user}.")
                st.rerun()
            else:
                st.rerun()
        else:
            if st.button("Login with WordPress", use_container_width=True):
                st.login()

        if st.session_state.login_error:
            st.error(st.session_state.login_error)

        st.markdown("---")
        st.markdown(
            "**No access yet?** If authentication succeeds but your email is not entitled, the app routes you to the subscription page."
        )
        st.link_button("Go to subscription", SUBSCRIPTION_URL, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Core capabilities</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-title">Quantitative portfolio construction</div>
                <div class="feature-text">
                    Explore risk-adjusted allocations, concentration trade-offs, and long-horizon compounding dynamics using structured optimization workflows.
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-title">Flexible valuation modeling</div>
                <div class="feature-text">
                    Build discounted cash flow cases, alter terminal assumptions, stress margins and growth, and compare base, bull, and bear scenarios systematically.
                </div>
            </div>
            <div class="feature-card">
                <div class="feature-title">Research discipline for retail investors</div>
                <div class="feature-text">
                    Move beyond intuition with process-driven analysis grounded in historical financial datasets, reproducible assumptions, and explicit uncertainty ranges.
                </div>
            </div>
        </div>
        <div class="footer-note">
            Theme is intentionally designed in orange and white for a clean high-contrast financial research aesthetic.
        </div>
        """,
        unsafe_allow_html=True,
    )


def subscription_page() -> None:
    topbar()
    sync_auth_state_from_oidc()
    c1, c2, c3 = st.columns([0.15, 0.7, 0.15])
    with c2:
        st.markdown(
            f"""
            <div class="subscribe-box">
                <div class="pill">Subscription required</div>
                <div class="hero-title" style="font-size: 2.2rem;">Unlock full access to {APP_NAME}</div>
                <div class="hero-subtitle">
                    Your login attempt was unsuccessful, or you do not yet have an active account. Subscribe through your WordPress site to enable access to the full platform.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button("Open subscription page", SUBSCRIPTION_URL, use_container_width=True)
        if st.button("Back to landing page", use_container_width=True):
            st.session_state.route_to_subscription = False
            st.session_state.login_error = None
            st.rerun()


def dashboard_page() -> None:
    sync_auth_state_from_oidc()
    st.title("Dashboard")
    st.write(f"Welcome to {APP_NAME}, {st.session_state.wp_user or 'Member'}.")
    st.info("This is the authenticated dashboard area. Replace this with your live analytics modules.")


def research_page() -> None:
    sync_auth_state_from_oidc()
    st.title("Research Workbench")
    st.write("Use this page for DCF models, scenario testing, and company research workflows.")


def tools_page() -> None:
    sync_auth_state_from_oidc()
    st.title("Portfolio Tools")
    st.write("Use this page for optimization, exposure analytics, and long-term wealth planning tools.")


def account_page() -> None:
    sync_auth_state_from_oidc()
    st.title("Account")
    st.write(f"Logged in as: **{st.session_state.wp_user or 'Unknown user'}**")
    st.write(f"Email: **{st.session_state.user_email or 'Unavailable'}**")
    st.write(f"WordPress base URL: `{WORDPRESS_BASE_URL}`")
    if st.button("Logout"):
        logout()


# -------------------------
# App router
# -------------------------
apply_global_css(st.session_state.login_bg_bytes)
sync_auth_state_from_oidc()

if st.session_state.authenticated:
    pg = st.navigation(
        {
            "Main": [
                st.Page(dashboard_page, title="Dashboard", icon="📊"),
                st.Page(research_page, title="Research", icon="🧠"),
                st.Page(tools_page, title="Tools", icon="🛠️"),
                st.Page(account_page, title="Account", icon="👤"),
            ]
        }
    )
    pg.run()
else:
    if st.session_state.route_to_subscription:
        subscription_page()
    else:
        login_page()


# -------------------------
# Deployment notes (keep/remove as needed)
# -------------------------
with st.sidebar:
    st.markdown("### Setup notes")
    st.markdown(
        """
- Set `WORDPRESS_BASE_URL`
- Set `SUBSCRIPTION_URL`
- Configure Streamlit OIDC secrets in `.streamlit/secrets.toml`
- Point Streamlit to your WordPress OIDC discovery metadata URL
- Ensure the OIDC provider returns an `email` claim
- Optionally set `ALLOWED_EMAILS` or `ALLOWED_EMAIL_DOMAINS`
- Replace placeholder pages with your actual app modules
        """
    )
    st.markdown("### Example `.streamlit/secrets.toml`")
    st.code(
        '''[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-long-random-secret"
client_id = "your-oidc-client-id"
client_secret = "your-oidc-client-secret"
server_metadata_url = "https://yourwordpresssite.com/.well-known/openid-configuration"
''',
        language="toml",
    )
