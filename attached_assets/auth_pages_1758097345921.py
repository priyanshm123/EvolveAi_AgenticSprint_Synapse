import streamlit as st
from database import DatabaseManager
import re

class AuthPages:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    def login_page(self):
        """Display login page"""
        st.markdown("## 🔐 Login to Medical Diagnostic Assistant")
        st.markdown("Please enter your credentials to access your account.")
        
        with st.form("login_form"):
            username = st.text_input("Username or Email", placeholder="Enter your username or email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("🔓 Login", use_container_width=True)
            with col2:
                register_link = st.form_submit_button("📝 Register New Account", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user_data = self.db_manager.authenticate_user(username, password)
                    
                    if user_data:
                        # Create session
                        session_token = self.db_manager.create_session(user_data['id'])
                        
                        if session_token:
                            # Store session in streamlit state
                            st.session_state.user_id = user_data['id']
                            st.session_state.username = user_data['username']
                            st.session_state.full_name = user_data['full_name']
                            st.session_state.email = user_data['email']
                            st.session_state.role = user_data['role']
                            st.session_state.session_token = session_token
                            st.session_state.authenticated = True
                            
                            st.success(f"Welcome back, {user_data['full_name']}!")
                            st.rerun()
                        else:
                            st.error("Failed to create session. Please try again.")
                    else:
                        st.error("Invalid username or password. Please try again.")
            
            if register_link:
                st.session_state.show_register = True
                st.rerun()
    
    def registration_page(self):
        """Display registration page"""
        st.markdown("## 📝 Create New Account")
        st.markdown("Join the Medical Diagnostic Assistant platform.")
        
        with st.form("registration_form"):
            st.subheader("Personal Information")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*", placeholder="Enter your first name")
                username = st.text_input("Username*", placeholder="Choose a unique username")
            with col2:
                last_name = st.text_input("Last Name*", placeholder="Enter your last name")
                email = st.text_input("Email*", placeholder="Enter your email address")
            
            st.subheader("Security")
            password = st.text_input("Password*", type="password", placeholder="Create a strong password")
            confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Confirm your password")
            
            st.subheader("Terms & Conditions")
            terms_accepted = st.checkbox(
                "I agree to the Terms of Service and Privacy Policy",
                help="By checking this box, you agree to our terms and conditions for using the Medical Diagnostic Assistant."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                register_button = st.form_submit_button("🎯 Create Account", use_container_width=True)
            with col2:
                back_to_login = st.form_submit_button("🔙 Back to Login", use_container_width=True)
            
            if register_button:
                # Validation
                errors = []
                
                if not all([first_name, last_name, username, email, password, confirm_password]):
                    errors.append("All fields marked with * are required")
                
                if username and len(username) < 3:
                    errors.append("Username must be at least 3 characters long")
                
                if email and not self.validate_email(email):
                    errors.append("Please enter a valid email address")
                
                if password != confirm_password:
                    errors.append("Passwords do not match")
                
                if password:
                    is_valid, message = self.validate_password(password)
                    if not is_valid:
                        errors.append(message)
                
                if not terms_accepted:
                    errors.append("You must accept the Terms of Service and Privacy Policy")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Create account
                    full_name = f"{first_name} {last_name}"
                    success = self.db_manager.create_user(username, email, password, full_name)
                    
                    if success:
                        st.success("🎉 Account created successfully! Please log in with your credentials.")
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error("Username or email already exists. Please choose different credentials.")
            
            if back_to_login:
                st.session_state.show_register = False
                st.rerun()
    
    def user_profile_sidebar(self):
        """Display user profile information in sidebar"""
        if hasattr(st.session_state, 'authenticated') and st.session_state.authenticated:
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 User Profile")
                st.write(f"**Name:** {st.session_state.full_name}")
                st.write(f"**Username:** {st.session_state.username}")
                st.write(f"**Email:** {st.session_state.email}")
                
                if st.button("🚪 Logout", use_container_width=True):
                    self.logout_user()
                
                st.markdown("---")
    
    def logout_user(self):
        """Logout current user"""
        if hasattr(st.session_state, 'session_token'):
            self.db_manager.logout_user(st.session_state.session_token)
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.success("You have been logged out successfully.")
        st.rerun()
    
    def check_authentication(self) -> bool:
        """Check if user is authenticated"""
        if hasattr(st.session_state, 'authenticated') and st.session_state.authenticated:
            # Validate session token
            if hasattr(st.session_state, 'session_token'):
                user_data = self.db_manager.validate_session(st.session_state.session_token)
                if user_data:
                    return True
                else:
                    # Session expired, logout
                    self.logout_user()
                    return False
            else:
                return False
        return False
    
    def get_current_user_id(self) -> int:
        """Get current user ID"""
        if hasattr(st.session_state, 'user_id'):
            return st.session_state.user_id
        return 0
    
    def display_user_dashboard(self):
        """Display user dashboard with recent activity"""
        st.markdown("### 📊 Your Dashboard")
        
        user_id = self.get_current_user_id()
        
        # Get user statistics
        patient_records = self.db_manager.get_user_patient_records(user_id)
        diagnostic_history = self.db_manager.get_user_diagnostic_history(user_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Patient Records", len(patient_records))
        
        with col2:
            st.metric("Diagnostic Analyses", len(diagnostic_history))
        
        with col3:
            if diagnostic_history:
                latest_analysis = max([d['created_at'] for d in diagnostic_history])
                st.metric("Last Analysis", latest_analysis.split(' ')[0])
            else:
                st.metric("Last Analysis", "None")
        
        # Recent patient records
        if patient_records:
            st.markdown("#### 📋 Recent Patient Records")
            for record in patient_records[:5]:  # Show last 5 records
                with st.expander(f"📄 {record['patient_name']} - {record['file_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**File Type:** {record['file_type'].upper()}")
                        st.write(f"**Uploaded:** {record['uploaded_at']}")
                    with col2:
                        st.write(f"**Patient:** {record['patient_name']}")
                        st.write(f"**Record ID:** {record['id']}")
        
        # Recent diagnostic results
        if diagnostic_history:
            st.markdown("#### 🔍 Recent Diagnostic Analyses")
            for analysis in diagnostic_history[:3]:  # Show last 3 analyses
                with st.expander(f"🧠 Analysis for {analysis['patient_name']} - {analysis['created_at'].split(' ')[0]}"):
                    diagnostic_data = analysis['diagnostic_data']
                    
                    if diagnostic_data.get('diagnoses'):
                        st.write("**Top Diagnoses:**")
                        for i, diagnosis in enumerate(diagnostic_data['diagnoses'][:3], 1):
                            confidence = diagnosis.get('confidence_score', 0)
                            st.write(f"{i}. {diagnosis.get('condition', 'Unknown')} ({confidence:.1%} confidence)")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Confidence Threshold:** {analysis['confidence_threshold']}")
                    with col2:
                        st.write(f"**Max Diagnoses:** {analysis['max_diagnoses']}")
        
        if not patient_records and not diagnostic_history:
            st.info("👋 Welcome! Upload your first patient data file to get started with AI-powered diagnostic analysis.")