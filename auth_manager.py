import streamlit as st
import os
from database import DatabaseManager
from typing import Optional, Dict

class AuthManager:
    def __init__(self, db_manager: DatabaseManager):   # ✅ Fixed constructor
        self.db_manager = db_manager
        self.session_secret = os.getenv("SESSION_SECRET", "default_session_secret")
    
    def display_auth_form(self):
        """Display Netflix-style authentication form"""
        
        # Netflix-style hero section for auth
        st.markdown("""
        <div class="hero-section" style="text-align: center;">
            <div class="hero-title" style="font-size: 2.5rem;">🏥 AI Medical Diagnostic Assistant</div>
            <div class="hero-subtitle">Secure Access Portal for Healthcare Professionals</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Authentication tabs
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Create Account"])
        
        with tab1:
            self._display_login_form()
        
        with tab2:
            self._display_registration_form()
    
    def _display_login_form(self):
        """Display login form with Netflix styling"""
        
        st.markdown("""
        <div class="netflix-card" style="max-width: 400px; margin: 2rem auto; padding: 2rem;">
            <h3 style="color: var(--text-primary); text-align: center; margin-bottom: 2rem;">Welcome Back</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(
                "Username or Email",
                placeholder="Enter your username or email",
                help="Use the username or email you registered with"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Your secure password"
            )
            
            remember_me = st.checkbox("Remember me", value=False)
            
            submit_button = st.form_submit_button("🚀 Sign In", type="primary", use_container_width=True)
            
            if submit_button:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                    return
                
                # Authenticate user
                user_data = self.db_manager.authenticate_user(username, password)
                
                if user_data:
                    session_token = self.db_manager.create_session(user_data['id'])
                    
                    if session_token:
                        st.session_state.user = user_data
                        st.session_state.session_token = session_token
                        
                        st.success(f"✅ Welcome back, {user_data['full_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create session. Please try again.")
                else:
                    st.error("❌ Invalid username or password. Please try again.")
        
        forgot_password = st.button("Forgot Password?", type="secondary", disabled=True, use_container_width=True)

        st.markdown("---")
        st.markdown("""
        <div class="netflix-card" style="background: rgba(46, 134, 171, 0.1); border-left: 4px solid var(--medical-blue);">
            <h4 style="color: var(--medical-blue); margin-bottom: 0.5rem;">👨‍⚕ Demo Access</h4>
            <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">
                New to the platform? Create your account using the "Create Account" tab above.
                All user data is securely encrypted and HIPAA compliant.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def _display_registration_form(self):
        """Display registration form with Netflix styling"""
        
        st.markdown("""
        <div class="netflix-card" style="max-width: 500px; margin: 2rem auto; padding: 2rem;">
            <h3 style="color: var(--text-primary); text-align: center; margin-bottom: 2rem;">Create Your Account</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("registration_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", placeholder="Enter your first name")
                username = st.text_input("Username", placeholder="Choose a unique username",
                                         help="Username must be unique and will be used for login")
            
            with col2:
                last_name = st.text_input("Last Name", placeholder="Enter your last name")
                email = st.text_input("Email Address", placeholder="Enter your email address",
                                      help="We'll use this for account recovery and notifications")
            
            password = st.text_input("Password", type="password", placeholder="Create a secure password",
                                     help="Password should be at least 8 characters long")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            role = st.selectbox(
                "Professional Role",
                options=["Physician", "Nurse Practitioner", "Physician Assistant", "Registered Nurse", 
                        "Medical Student", "Resident", "Fellow", "Other Healthcare Professional"],
                help="Select your professional role in healthcare"
            )
            
            terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy",
                                         help="You must accept the terms to create an account")
            hipaa_acknowledged = st.checkbox("I acknowledge HIPAA compliance requirements",
                                             help="By checking this, you confirm understanding of HIPAA requirements")
            
            submit_button = st.form_submit_button("🎯 Create Account", type="primary", use_container_width=True)
            
            if submit_button:
                validation_errors = []
                
                if not all([first_name, last_name, username, email, password, confirm_password]):
                    validation_errors.append("All fields are required")
                if password != confirm_password:
                    validation_errors.append("Passwords do not match")
                if len(password) < 8:
                    validation_errors.append("Password must be at least 8 characters long")
                if not terms_accepted:
                    validation_errors.append("You must accept the Terms of Service")
                if not hipaa_acknowledged:
                    validation_errors.append("You must acknowledge HIPAA compliance requirements")
                if "@" not in email or "." not in email:
                    validation_errors.append("Please enter a valid email address")
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(f"❌ {error}")
                    return
                
                full_name = f"{first_name.strip()} {last_name.strip()}"
                success = self.db_manager.create_user(
                    username=username.strip(),
                    email=email.strip().lower(),
                    password=password,
                    full_name=full_name
                )
                
                if success:
                    st.success("✅ Account created successfully! Please sign in with your new credentials.")
                    st.balloons()
                    st.info("👈 Switch to the 'Sign In' tab to access your account.")
                else:
                    st.error("❌ Account creation failed. Username or email may already be in use.")
        
        st.markdown("---")
        st.markdown("""
        <div class="netflix-card" style="background: rgba(40, 167, 69, 0.1); border-left: 4px solid var(--medical-green);">
            <h4 style="color: var(--medical-green); margin-bottom: 0.5rem;">🔒 Security & Privacy</h4>
            <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">
                Your account is protected with enterprise-grade security. All patient data is encrypted
                and handled in compliance with HIPAA regulations. We never share your information with third parties.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def check_authentication(self) -> bool:
        """Check if user is authenticated"""
        if 'user' not in st.session_state or not st.session_state.user:
            return False
        if 'session_token' not in st.session_state or not st.session_state.session_token:
            return False
        
        user_data = self.db_manager.validate_session(st.session_state.session_token)
        
        if user_data:
            st.session_state.user = user_data
            return True
        else:
            self.logout()
            return False
    
    def logout(self):
        """Logout current user"""
        if 'session_token' in st.session_state and st.session_state.session_token:
            self.db_manager.logout_user(st.session_state.session_token)
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.rerun()
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current authenticated user"""
        if self.check_authentication():
            return st.session_state.user
        return None
    
    def require_authentication(self):
        """Decorator-style function to require authentication"""
        if not self.check_authentication():
            self.display_auth_form()
            st.stop()
    
    def display_user_info_sidebar(self):
        """Display user info in sidebar"""
        if 'user' in st.session_state and st.session_state.user:
            user = st.session_state.user
            with st.sidebar:
                st.markdown("---")
                st.markdown("""
                <div class="netflix-card" style="text-align: center; padding: 1rem;">
                    <div class="patient-avatar" style="margin: 0 auto 1rem;">{}</div>
                    <h4 style="color: var(--text-primary); margin: 0;">{}</h4>
                    <p style="color: var(--text-secondary); margin: 0; font-size: 0.8rem;">{}</p>
                    <p style="color: var(--medical-blue); margin: 0; font-size: 0.8rem;">{}</p>
                </div>
                """.format(
                    user['full_name'][0].upper(),
                    user['full_name'],
                    user['email'],
                    user['role'].title()
                ), unsafe_allow_html=True)
                
                if st.button("🚪 Logout", type="secondary", use_container_width=True):
                    self.logout()
