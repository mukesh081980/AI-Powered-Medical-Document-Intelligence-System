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



                if st.session_state.get("forgot_password_mode", False):

                    st.subheader("Reset Your Password")
                    st.write(
                        "Enter your registered email address to generate a "
                        "password-reset token."
                    )

                    with st.form("forgot_password_form"):
                        reset_email = st.text_input(
                            "Registered Email Address",
                            placeholder="Enter your registered email"
                        )

                        reset_submitted = st.form_submit_button(
                            "Generate Reset Token",
                            width="stretch"
                        )

                    if reset_submitted:
                        if not reset_email.strip():
                            st.error("Please enter your email address.")
                        else:
                            try:
                                token = database.create_password_reset_token(
                                    reset_email.strip().lower()
                                )

                                if token:
                                    st.session_state["reset_token"] = token
                                    st.success("Reset token generated successfully.")
                                else:
                                    st.error(
                                        "Unable to process this email address. "
                                        "Check that it belongs to an active account."
                                    )
                            except Exception as error:
                                print(f"Password reset token request failed: {error}")
                                st.error(
                                    "Unable to generate a reset token right now. "
                                    "Please try again later."
                                )

                    # Show the token for the current manual reset flow.
                    # This is suitable for testing; production should email it.
                    if st.session_state.get("reset_token"):
                        st.info(
                            "Copy this reset token. It expires in 15 minutes "
                            "and can be used only once."
                        )
                        st.code(
                            st.session_state["reset_token"],
                            language=None
                        )

                        with st.form("complete_password_reset_form"):
                            entered_token = st.text_input(
                                "Reset Token",
                                placeholder="Paste your reset token"
                            )
                            new_password = st.text_input(
                                "New Password",
                                type="password",
                                placeholder="Enter a new password"
                            )
                            confirm_new_password = st.text_input(
                                "Confirm New Password",
                                type="password",
                                placeholder="Re-enter your new password"
                            )
                            reset_password_submitted = st.form_submit_button(
                                "Update Password",
                                width="stretch"
                            )

                        if reset_password_submitted:
                            if not entered_token.strip():
                                st.error("Please enter the reset token.")
                            elif not new_password or not confirm_new_password:
                                st.error("Please complete both password fields.")
                            elif len(new_password) < 12:
                                st.error(
                                    "Password must contain at least 12 characters."
                                )
                            elif new_password != confirm_new_password:
                                st.error("The passwords do not match.")
                            else:
                                try:
                                    updated = database.reset_user_password(
                                        entered_token.strip(),
                                        new_password
                                    )
                                    if updated:
                                        st.session_state.pop("reset_token", None)
                                        st.success(
                                            "Your password has been updated. "
                                            "You can now sign in with your new password."
                                        )
                                    else:
                                        st.error(
                                            "The reset token is invalid, expired, "
                                            "or has already been used."
                                        )
                                except Exception as error:
                                    print(f"Password update failed: {error}")
                                    st.error(
                                        "Unable to update your password right now. "
                                        "Please try again later."
                                    )

                    if st.button("Back to Sign In", key="back_to_sign_in"):
                        st.session_state["forgot_password_mode"] = False
                        st.session_state.pop("reset_token", None)
                        st.rerun()

                else:

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



                    st.caption("For authorized users only.")



                    if st.button("Forgot Password?", key="forgot_password"):

                        st.session_state["forgot_password_mode"] = True

                        st.rerun()



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
