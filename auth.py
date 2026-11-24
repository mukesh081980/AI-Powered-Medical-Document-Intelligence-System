
import re
import streamlit as st
import database


def login_screen():

    # ---------------- PAGE CONFIGURATION ----------------

    st.markdown("""
    <style>

    .stApp {
        background:
            radial-gradient(circle at top left, #DDF7F3 0%, transparent 35%),
            linear-gradient(135deg, #F4F8FC 0%, #EAF2F8 100%);
    }

    .main .block-container {
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Brand header */

    .brand {
        text-align: center;
        font-size: 38px;
        font-weight: 850;
        letter-spacing: -1px;
        color: #102A43;
        margin-bottom: 0;
    }

    .brand span {
        color: #0D9488;
    }

    .tagline {
        text-align: center;
        font-size: 14px;
        color: #64748B;
        margin-top: 5px;
        margin-bottom: 28px;
    }

    /* Login heading */

    .welcome-title {
        color: #102A43;
        font-size: 27px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .welcome-description {
        color: #64748B;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Form labels */

    label {
        font-weight: 600 !important;
        color: #334155 !important;
    }

    /* Input fields */

    div[data-baseweb="input"] {
        border-radius: 9px !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #0D9488 !important;
        box-shadow: 0 0 0 1px #0D9488 !important;
    }

    /* Buttons */

    div.stButton > button,
    div.stFormSubmitButton > button {
        background: linear-gradient(90deg, #0F766E, #0D9488);
        color: white;
        border: none;
        border-radius: 9px;
        min-height: 45px;
        font-weight: 650;
        transition: 0.2s ease;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        background: linear-gradient(90deg, #115E59, #0F766E);
        color: white;
        border: none;
    }

    /* Tabs */

    button[data-baseweb="tab"] {
        font-weight: 650;
        color: #475569;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0F766E;
    }

    /* Footer */

    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 12px;
        margin-top: 25px;
    }

    </style>
    """, unsafe_allow_html=True)

    # ---------------- BRAND HEADER ----------------

    st.markdown(
        '<div class="brand">MediSimplify <span>AI</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tagline">'
        'INTELLIGENT HEALTHCARE PORTAL'
        '</div>',
        unsafe_allow_html=True
    )

    # ---------------- CENTERED LOGIN CARD ----------------

    left, center, right = st.columns([1, 1.45, 1])

    with center:

        with st.container(border=True):

            st.markdown(
                '<div class="welcome-title">Welcome</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="welcome-description">'
                'Access your healthcare account securely.'
                '</div>',
                unsafe_allow_html=True
            )

            sign_in_tab, sign_up_tab = st.tabs(
                ["Sign In", "Create Account"]
            )

            # ==================================================
            # SIGN IN
            # ==================================================

            with sign_in_tab:

                with st.form("login_form"):

                    st.subheader("Sign in to your account")

                    username = st.text_input(
                        "Username",
                        placeholder="Enter your username"
                    )

                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password"
                    )

                    submitted = st.form_submit_button(
                        "Sign In",
                        width="stretch"
                    )

                    if submitted:

                        if not username.strip() or not password:

                            st.error(
                                "Please enter your username and password."
                            )

                        else:

                            user = database.authenticate_user(
                                username.strip(),
                                password
                            )

                            if user:

                                st.session_state["authenticated"] = True
                                st.session_state["user"] = user
                                st.session_state["navigation"] = "🏠 Dashboard"

                                st.success("Login successful!")
                                st.rerun()

                            else:

                                st.error(
                                    "Invalid username or password."
                                )

                st.caption(
                    "For authorized users only."
                )

            # ==================================================
            # PATIENT SIGN UP
            # ==================================================

            with sign_up_tab:

                st.subheader("Create your patient account")

                st.info(
                    "Patient registration is open. "
                    "Doctor and Admin accounts are managed separately."
                )

                with st.form("signup_form"):

                    full_name = st.text_input(
                        "Full Name",
                        placeholder="Enter your full name"
                    )

                    new_username = st.text_input(
                        "Username",
                        placeholder="Choose a username"
                    )

                    email = st.text_input(
                        "Email Address",
                        placeholder="Enter your email"
                    )

                    new_password = st.text_input(
                        "Create Password",
                        type="password",
                        placeholder="Minimum 12 characters"
                    )

                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Re-enter your password"
                    )

                    signup_submitted = st.form_submit_button(
                        "Create Patient Account",
                        width="stretch"
                    )

                    if signup_submitted:

                        if not all([
                            full_name.strip(),
                            new_username.strip(),
                            email.strip(),
                            new_password,
                            confirm_password
                        ]):

                            st.error(
                                "Please complete all fields."
                            )

                        elif not re.fullmatch(
                            r"[^@\s]+@[^@\s]+\.[^@\s]+",
                            email.strip()
                        ):

                            st.error(
                                "Please enter a valid email address."
                            )

                        elif len(new_password) < 12:

                            st.error(
                                "Password must contain at least 12 characters."
                            )

                        elif new_password != confirm_password:

                            st.error(
                                "Passwords do not match."
                            )

                        else:

                            user_id = database.register_patient_account(
                                full_name.strip(),
                                new_username.strip(),
                                email.strip().lower(),
                                new_password
                            )

                            if user_id:

                                user = database.authenticate_user(
                                    new_username.strip(),
                                    new_password
                                )

                                if user:

                                    st.session_state["authenticated"] = True
                                    st.session_state["user"] = user
                                    st.session_state["navigation"] = "🏠 Dashboard"

                                    st.success(
                                        "Your account was created successfully!"
                                    )

                                    st.rerun()

                                else:

                                    st.success(
                                        "Account created. Please sign in."
                                    )

                            else:

                                st.error(
                                    "Account creation failed. "
                                    "Username or email may already exist. "
                                    "Please try different details."
                                )

        # ---------------- FOOTER ----------------

        st.markdown(
            '<div class="footer">'
            'MEDISIMPLIFY AI | SMARTER HEALTHCARE'
            '</div>',
            unsafe_allow_html=True
        )
