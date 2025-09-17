import streamlit as st
import os
from datetime import datetime
import json
import pandas as pd
from database import DatabaseManager
from ui_components import UIComponents
from user_dashboard import UserDashboard
from diagnostic_engine import DiagnosticEngine
from data_processor import DataProcessor
from auth_manager import AuthManager

# Page configuration
st.set_page_config(
    page_title="AI Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Netflix-inspired CSS styling
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Variables */
    :root {
        --netflix-red: #E50914;
        --netflix-black: #141414;
        --netflix-dark-gray: #2F2F2F;
        --netflix-gray: #808080;
        --netflix-light-gray: #B3B3B3;
        --medical-blue: #2E86AB;
        --medical-green: #28A745;
        --medical-orange: #FD7E14;
        --medical-purple: #6F42C1;
        --success-green: #00D4AA;
        --warning-orange: #FF8A00;
        --danger-red: #FF3366;
        --background-dark: #0F0F0F;
        --card-dark: #1A1A1A;
        --text-primary: #FFFFFF;
        --text-secondary: #B3B3B3;
    }
    
    /* Reset and Base Styles */
    .stApp {
        background: linear-gradient(135deg, var(--background-dark) 0%, var(--netflix-black) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, var(--netflix-black) 0%, var(--medical-blue) 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.5;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--text-primary), var(--medical-blue));
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }
    
    /* Netflix-style Cards */
    .netflix-card {
        background: var(--card-dark);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
    }
    
    .netflix-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--netflix-red), var(--medical-blue));
        transform: scaleX(0);
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .netflix-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .netflix-card:hover::before {
        transform: scaleX(1);
    }
    
    /* Patient Record Grid */
    .patient-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .patient-card {
        background: var(--card-dark);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
        cursor: pointer;
    }
    
    .patient-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        border-color: var(--medical-blue);
    }
    
    .patient-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .patient-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--medical-blue), var(--medical-purple));
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    
    /* Diagnostic Cards */
    .diagnosis-card {
        background: var(--card-dark);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid var(--medical-blue);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .diagnosis-card:hover {
        transform: translateX(5px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    
    .confidence-high { 
        color: var(--success-green); 
        font-weight: 600;
    }
    
    .confidence-medium { 
        color: var(--warning-orange); 
        font-weight: 600;
    }
    
    .confidence-low { 
        color: var(--danger-red); 
        font-weight: 600;
    }
    
    .risk-high { 
        color: var(--danger-red); 
        background: rgba(255, 51, 102, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .risk-medium { 
        color: var(--warning-orange); 
        background: rgba(255, 138, 0, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .risk-low { 
        color: var(--success-green); 
        background: rgba(0, 212, 170, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: var(--netflix-dark-gray);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .css-1d391kg .css-1v0mbdj {
        background: var(--netflix-dark-gray);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--netflix-red), #B71C1C);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(229, 9, 20, 0.3);
        background: linear-gradient(135deg, #B71C1C, var(--netflix-red));
    }
    
    /* File Uploader */
    .stFileUploader {
        background: var(--card-dark);
        border: 2px dashed rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: var(--medical-blue);
        background: rgba(46, 134, 171, 0.05);
    }
    
    /* Metrics */
    .css-1xarl3l {
        background: var(--card-dark);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--netflix-red), var(--medical-blue));
        border-radius: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--netflix-dark-gray);
        border-radius: 10px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--netflix-red);
        color: white;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--card-dark);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: var(--netflix-red);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Status Indicators */
    .status-online {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: var(--success-green);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 212, 170, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 212, 170, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 212, 170, 0); }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--netflix-dark-gray);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--netflix-gray);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .patient-grid {
            grid-template-columns: 1fr;
        }
        
        .netflix-card {
            margin: 0.5rem 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_components():
    """Initialize all application components"""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    if 'ui_components' not in st.session_state:
        st.session_state.ui_components = UIComponents()
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager(st.session_state.db_manager)
    if 'diagnostic_engine' not in st.session_state:
        st.session_state.diagnostic_engine = DiagnosticEngine()
    if 'data_processor' not in st.session_state:
        st.session_state.data_processor = DataProcessor()

def display_hero_section():
    """Display Netflix-style hero section"""
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🏥 AI Medical Diagnostic Assistant</div>
        <div class="hero-subtitle">Advanced AI-powered diagnostic insights for healthcare professionals</div>
        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
            <div style="background: rgba(229, 9, 20, 0.1); padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid var(--netflix-red);">
                <span style="color: var(--netflix-red); font-weight: 600;">🚀 Latest AI Technology</span>
            </div>
            <div style="background: rgba(46, 134, 171, 0.1); padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid var(--medical-blue);">
                <span style="color: var(--medical-blue); font-weight: 600;">🔒 HIPAA Compliant</span>
            </div>
            <div style="background: rgba(40, 167, 69, 0.1); padding: 0.5rem 1rem; border-radius: 20px; border: 1px solid var(--medical-green);">
                <span style="color: var(--medical-green); font-weight: 600;">✓ Clinically Validated</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_quick_stats():
    """Display Netflix-style quick statistics"""
    if 'user' in st.session_state and st.session_state.user:
        user_id = st.session_state.user['id']
        patient_records = st.session_state.db_manager.get_user_patient_records(user_id)
        diagnostic_history = st.session_state.db_manager.get_user_diagnostic_history(user_id)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="netflix-card" style="text-align: center;">
                <h3 style="color: var(--medical-blue); margin-bottom: 0.5rem;">📋</h3>
                <h2 style="color: var(--text-primary); margin: 0;">{}</h2>
                <p style="color: var(--text-secondary); margin: 0;">Patient Records</p>
            </div>
            """.format(len(patient_records)), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="netflix-card" style="text-align: center;">
                <h3 style="color: var(--medical-green); margin-bottom: 0.5rem;">🧠</h3>
                <h2 style="color: var(--text-primary); margin: 0;">{}</h2>
                <p style="color: var(--text-secondary); margin: 0;">Analyses Run</p>
            </div>
            """.format(len(diagnostic_history)), unsafe_allow_html=True)
        
        with col3:
            avg_confidence = 0
            if diagnostic_history:
                confidences = []
                for analysis in diagnostic_history:
                    if analysis.get('diagnostic_data', {}).get('validation', {}).get('overall_confidence'):
                        confidences.append(analysis['diagnostic_data']['validation']['overall_confidence'])
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
            
            st.markdown("""
            <div class="netflix-card" style="text-align: center;">
                <h3 style="color: var(--medical-purple); margin-bottom: 0.5rem;">📊</h3>
                <h2 style="color: var(--text-primary); margin: 0;">{:.0%}</h2>
                <p style="color: var(--text-secondary); margin: 0;">Avg Confidence</p>
            </div>
            """.format(avg_confidence), unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="netflix-card" style="text-align: center;">
                <h3 style="color: var(--success-green); margin-bottom: 0.5rem;">🎯</h3>
                <h2 style="color: var(--text-primary); margin: 0;">Active</h2>
                <p style="color: var(--text-secondary); margin: 0;">System Status <span class="status-online"></span></p>
            </div>
            """, unsafe_allow_html=True)

def main():
    """Main application function"""
    load_css()
    initialize_components()
    
    auth_manager = st.session_state.auth_manager
    ui_components = st.session_state.ui_components
    
    # Check authentication
    if 'user' not in st.session_state or not st.session_state.user:
        auth_manager.display_auth_form()
        return
    
    # Display hero section
    display_hero_section()
    
    # Display quick stats
    display_quick_stats()
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "📋 New Analysis", 
        "📊 Patient Records", 
        "🧠 Diagnostic History", 
        "⚙️ Settings"
    ])
    
    with tab1:
        st.markdown("## 🏠 Dashboard Overview")
        display_dashboard()
    
    with tab2:
        st.markdown("## 📋 New Diagnostic Analysis")
        display_new_analysis()
    
    with tab3:
        st.markdown("## 📊 Patient Records")
        display_patient_records()
    
    with tab4:
        st.markdown("## 🧠 Diagnostic History")
        display_diagnostic_history()
    
    with tab5:
        st.markdown("## ⚙️ User Settings")
        display_user_settings()

def display_dashboard():
    """Display main dashboard"""
    user_dashboard = UserDashboard(st.session_state.db_manager)
    user_id = st.session_state.user['id']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Recent Patient Records")
        patient_records = st.session_state.db_manager.get_user_patient_records(user_id)
        
        if patient_records:
            recent_records = patient_records[:3]  # Show last 3 records
            
            for record in recent_records:
                st.markdown(f"""
                <div class="patient-card">
                    <div class="patient-card-header">
                        <div class="patient-avatar">{record['patient_name'][0].upper()}</div>
                        <div>
                            <h4 style="margin: 0; color: var(--text-primary);">{record['patient_name']}</h4>
                            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">{record['file_name']}</p>
                            <p style="margin: 0; color: var(--medical-blue); font-size: 0.8rem;">{record['uploaded_at']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No patient records found. Upload your first patient data to get started!")
    
    with col2:
        st.markdown("### Quick Actions")
        
        if st.button("🆕 New Analysis", key="quick_new_analysis"):
            st.switch_page("📋 New Analysis")
        
        if st.button("📁 Upload Records", key="quick_upload"):
            st.switch_page("📋 New Analysis")
        
        if st.button("📊 View Reports", key="quick_reports"):
            st.switch_page("🧠 Diagnostic History")

def display_new_analysis():
    """Display new analysis interface"""
    st.markdown("### Upload Patient Data")
    
    # File upload section
    st.markdown("""
    <div style="background: var(--card-dark); padding: 2rem; border-radius: 15px; border: 2px dashed rgba(255, 255, 255, 0.2); margin-bottom: 2rem;">
        <div style="text-align: center;">
            <h3 style="color: var(--text-primary); margin-bottom: 1rem;">📁 Drag and Drop Files</h3>
            <p style="color: var(--text-secondary);">Supported formats: CSV, JSON, TXT, PDF</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Choose patient data files",
        accept_multiple_files=True,
        type=['csv', 'json', 'txt', 'pdf']
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    st.dataframe(df)
                elif uploaded_file.name.endswith('.json'):
                    data = json.load(uploaded_file)
                    st.json(data)
                else:
                    content = str(uploaded_file.read(), "utf-8")
                    st.text_area("File Content", content, height=200)
        
        # Analysis parameters
        col1, col2 = st.columns(2)
        
        with col1:
            confidence_threshold = st.slider(
                "Confidence Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.3,
                step=0.1
            )
        
        with col2:
            max_diagnoses = st.number_input(
                "Maximum Diagnoses",
                min_value=3,
                max_value=15,
                value=8
            )
        
        enable_red_flags = st.checkbox("Enable Red Flag Detection", value=True)
        
        if st.button("🧠 Run AI Analysis", type="primary"):
            with st.spinner("Running diagnostic analysis..."):
                # Process files and run analysis
                data_processor = st.session_state.data_processor
                diagnostic_engine = st.session_state.diagnostic_engine
                
                processed_data = []
                for file in uploaded_files:
                    try:
                        file_data = data_processor.process_file(file)
                        processed_data.extend(file_data)
                    except Exception as e:
                        st.error(f"Error processing {file.name}: {str(e)}")
                        continue
                
                if processed_data:
                    # Save patient data
                    user_id = st.session_state.user['id']
                    record_id = st.session_state.db_manager.save_patient_data(
                        user_id, processed_data, 
                        f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}", 
                        "multi"
                    )
                    
                    # Run diagnostic analysis
                    results = diagnostic_engine.analyze_patient_data(
                        processed_data, confidence_threshold, 
                        max_diagnoses, enable_red_flags
                    )
                    
                    # Save results
                    if record_id:
                        st.session_state.db_manager.save_diagnostic_results(
                            user_id, record_id, results, 
                            confidence_threshold, max_diagnoses
                        )
                    
                    # Display results
                    st.success("✅ Analysis completed successfully!")
                    display_analysis_results(results)

def display_analysis_results(results):
    """Display analysis results in Netflix style"""
    if not results:
        st.error("No results to display")
        return
    
    # Red flags
    if results.get('red_flags'):
        st.markdown("### 🚨 Critical Conditions Detected")
        for flag in results['red_flags']:
            st.markdown(f"""
            <div class="netflix-card" style="border-left: 4px solid var(--danger-red);">
                <h4 style="color: var(--danger-red); margin-bottom: 0.5rem;">⚠️ {flag.get('condition', 'Unknown')}</h4>
                <p style="color: var(--text-secondary); margin: 0;">{flag.get('reasoning', 'No reasoning provided')}</p>
                <p style="color: var(--text-primary); margin-top: 0.5rem; font-weight: 600;">Action: {flag.get('action', 'Consult healthcare provider')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Diagnoses
    if results.get('diagnoses'):
        st.markdown("### 🎯 Differential Diagnoses")
        
        for i, diagnosis in enumerate(results['diagnoses'], 1):
            confidence = diagnosis.get('confidence_score', 0)
            risk_level = diagnosis.get('risk_level', 'Medium').lower()
            
            st.markdown(f"""
            <div class="diagnosis-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="margin: 0; color: var(--text-primary);">#{i} {diagnosis.get('condition', 'Unknown')}</h4>
                    <div style="display: flex; gap: 1rem; align-items: center;">
                        <span class="confidence-{'high' if confidence >= 0.8 else 'medium' if confidence >= 0.5 else 'low'}">{confidence:.1%}</span>
                        <span class="risk-{risk_level}">{diagnosis.get('risk_level', 'Medium')} Risk</span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <strong style="color: var(--text-secondary);">Specialty:</strong>
                        <span style="color: var(--text-primary);"> {diagnosis.get('specialty', 'General Medicine')}</span>
                    </div>
                    <div>
                        <strong style="color: var(--text-secondary);">ICD-10:</strong>
                        <span style="color: var(--text-primary);"> {diagnosis.get('icd_10_code', 'Not specified')}</span>
                    </div>
                </div>
                <p style="color: var(--text-secondary); margin: 0;">{diagnosis.get('clinical_reasoning', 'No reasoning provided')}</p>
            </div>
            """, unsafe_allow_html=True)

def display_patient_records():
    """Display patient records"""
    user_dashboard = UserDashboard(st.session_state.db_manager)
    user_id = st.session_state.user['id']
    user_dashboard.display_patient_history(user_id)

def display_diagnostic_history():
    """Display diagnostic history"""
    user_dashboard = UserDashboard(st.session_state.db_manager)
    user_id = st.session_state.user['id']
    user_dashboard.display_diagnostic_history(user_id)

def display_user_settings():
    """Display user settings"""
    user_dashboard = UserDashboard(st.session_state.db_manager)
    user_id = st.session_state.user['id']
    user_dashboard.display_user_settings(user_id)

if __name__ == "__main__":
    main()
