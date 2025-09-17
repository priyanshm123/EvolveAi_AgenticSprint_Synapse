import dotenv
dotenv.load_dotenv()
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from diagnostic_engine import DiagnosticEngine
from data_processor import DataProcessor
from ui_components import UIComponents
from database import DatabaseManager
from auth_pages import AuthPages
from user_dashboard import UserDashboard
import os

# Page configuration
st.set_page_config(
    page_title="AI Medical Diagnostic Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical interface
st.markdown("""
<style>
    .urgent-alert {
        background-color: #DC3545;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
    }
    .warning-alert {
        background-color: #FFC107;
        color: #212529;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
    }
    .success-alert {
        background-color: #28A745;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-weight: bold;
    }
    .diagnosis-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 5px solid #2E86AB;
    }
    .confidence-high {
        color: #28A745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #FFC107;
        font-weight: bold;
    }
    .confidence-low {
        color: #DC3545;
        font-weight: bold;
    }
    .risk-high {
        background-color: #DC3545;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
    }
    .risk-medium {
        background-color: #FFC107;
        color: #212529;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
    }
    .risk-low {
        background-color: #28A745;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize components
    diagnostic_engine = DiagnosticEngine()
    data_processor = DataProcessor()
    ui_components = UIComponents()
    db_manager = DatabaseManager()
    auth_pages = AuthPages(db_manager)
    user_dashboard = UserDashboard(db_manager)
    
    # Check authentication
    if not auth_pages.check_authentication():
        # Show login or registration page
        if st.session_state.get('show_register', False):
            auth_pages.registration_page()
        else:
            auth_pages.login_page()
        return
    
    # Title and header
    st.title("🏥 AI-Powered Medical Diagnostic Assistant")
    st.markdown("Advanced diagnostic analysis using AI to support clinical decision-making")
    
    # --- ENTIRE BLOCK BELOW IS NOW CORRECTLY INDENTED ---
    
    # Check for Google API key
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("⚠️ Google API key not found. Please set the GOOGLE_API_KEY environment variable in your .env file.")
        st.stop()
    
    # User profile in sidebar
    auth_pages.user_profile_sidebar()
    
    # Add navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 New Analysis", "📋 Patient History", "🧠 Analysis History", "⚙️ Settings"])
    
    with tab1:
        # Main analysis interface
        perform_analysis_interface(
            diagnostic_engine, data_processor, ui_components, 
            db_manager, auth_pages, user_dashboard
        )
    
    with tab2:
        user_dashboard.display_patient_history(auth_pages.get_current_user_id())
    
    with tab3:
        user_dashboard.display_diagnostic_history(auth_pages.get_current_user_id())
    
    with tab4:
        user_dashboard.display_user_settings(auth_pages.get_current_user_id())

def perform_analysis_interface(diagnostic_engine, data_processor, ui_components, 
                             db_manager, auth_pages, user_dashboard):
    """Main analysis interface"""
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("📋 Patient Data Configuration")
        
        # File upload section
        st.subheader("Upload Patient Dataset")
        uploaded_files = st.file_uploader(
            "Select patient data files",
            type=['csv', 'json', 'txt', 'pdf'],
            accept_multiple_files=True,
            help="Upload CSV, JSON, text, or PDF files containing patient information"
        )
        
        # Diagnostic parameters
        st.subheader("⚙️ Diagnostic Parameters")
        confidence_threshold = st.slider(
            "Minimum Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Minimum confidence score for diagnosis inclusion"
        )
        
        max_diagnoses = st.number_input(
            "Maximum Diagnoses to Display",
            min_value=3,
            max_value=15,
            value=8,
            help="Maximum number of differential diagnoses to show"
        )
        
        include_red_flags = st.checkbox(
            "Enable Red Flag Detection",
            value=True,
            help="Highlight urgent conditions requiring immediate attention"
        )
        
        # Data filtering options
        st.subheader("🔍 Data Filters")
        filter_by_urgency = st.selectbox(
            "Filter by Urgency Level",
            options=["All", "High", "Medium", "Low"],
            index=0
        )
        
        filter_by_specialty = st.multiselect(
            "Filter by Medical Specialty",
            options=["Cardiology", "Neurology", "Gastroenterology", "Pulmonology", 
                    "Endocrinology", "Infectious Disease", "Emergency Medicine"],
            default=[]
        )
    
    # Main content area
    if not uploaded_files:
        # Display user dashboard and welcome screen
        auth_pages.display_user_dashboard()
        ui_components.display_welcome_screen()
        return
    
    # Process uploaded files
    try:
        with st.spinner("📊 Processing patient data..."):
            patient_data = data_processor.process_uploaded_files(uploaded_files)
            
        # Save patient data to database
        user_id = auth_pages.get_current_user_id()
        patient_record_ids = []
        
        for uploaded_file in uploaded_files:
            file_type = uploaded_file.name.split('.')[-1].lower()
            record_id = db_manager.save_patient_data(
                user_id, patient_data, uploaded_file.name, file_type
            )
            if record_id:
                patient_record_ids.append(record_id)
        
        # Debug information
        st.sidebar.write(f"DEBUG: Files processed: {len(uploaded_files)}")
        st.sidebar.write(f"DEBUG: Records found: {len(patient_data) if patient_data else 0}")
        st.sidebar.write(f"DEBUG: Records saved: {len(patient_record_ids)}")
        
        if not patient_data:
            st.error("❌ No valid patient data found in uploaded files.")
            st.info("💡 Please check that your files contain valid medical data with recognizable field names.")
            return
            
        # Display patient data summary
        st.header("📋 Patient Data Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(patient_data))
        with col2:
            st.metric("Data Fields", len(patient_data[0].keys()) if patient_data else 0)
        with col3:
            completeness = data_processor.calculate_completeness(patient_data)
            st.metric("Data Completeness", f"{completeness:.1f}%")
        with col4:
            st.metric("File Format", uploaded_files[0].type.split('/')[-1].upper())
        
        # Generate diagnostic analysis
        st.header("🔍 AI Diagnostic Analysis")
        
        with st.spinner("🧠 Analyzing patient data with AI..."):
            diagnostic_results = diagnostic_engine.analyze_patient_data(
                patient_data,
                confidence_threshold=confidence_threshold,
                max_diagnoses=max_diagnoses,
                include_red_flags=include_red_flags
            )
        
        # Save diagnostic results to database
        if diagnostic_results and patient_record_ids:
            for record_id in patient_record_ids:
                db_manager.save_diagnostic_results(
                    user_id, record_id, diagnostic_results, 
                    confidence_threshold, max_diagnoses
                )
        
        # Debug diagnostic results
        st.sidebar.write(f"DEBUG: Diagnostic results received: {bool(diagnostic_results)}")
        if diagnostic_results:
            st.sidebar.write(f"DEBUG: Diagnoses count: {len(diagnostic_results.get('diagnoses', []))}")
            st.sidebar.write(f"DEBUG: Results saved to database: {bool(patient_record_ids)}")
        
        if not diagnostic_results:
            st.error("❌ Unable to generate diagnostic analysis. Please check your data and try again.")
            st.info("💡 This could be due to API issues or insufficient data. Try uploading more detailed patient information.")
            return
        
        # Red flag alerts
        if include_red_flags and diagnostic_results.get('red_flags'):
            st.markdown("### 🚨 Urgent Red Flag Conditions")
            for red_flag in diagnostic_results['red_flags']:
                st.markdown(f"""
                <div class="urgent-alert">
                    <strong>⚠️ URGENT:</strong> {red_flag['condition']}<br>
                    <strong>Reasoning:</strong> {red_flag['reasoning']}<br>
                    <strong>Recommended Action:</strong> {red_flag['action']}
                </div>
                """, unsafe_allow_html=True)
        
        # Main diagnostic results
        st.header("🎯 Ranked Differential Diagnoses")
        
        # Apply filters
        filtered_diagnoses = ui_components.apply_filters(
            diagnostic_results['diagnoses'],
            filter_by_urgency,
            filter_by_specialty
        )
        
        if not filtered_diagnoses:
            st.warning("⚠️ No diagnoses match the current filter criteria.")
            return
        
        # Display diagnoses
        for i, diagnosis in enumerate(filtered_diagnoses, 1):
            ui_components.display_diagnosis_card(diagnosis, i)
        
        # Visualization section
        st.header("📊 Diagnostic Visualization")
        
        # Create tabs for different visualizations
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(["Confidence Scores", "Risk Stratification", "Evidence Summary"])
        
        with viz_tab1:
            ui_components.create_confidence_chart(filtered_diagnoses)
        
        with viz_tab2:
            ui_components.create_risk_stratification_chart(filtered_diagnoses)
        
        with viz_tab3:
            ui_components.display_evidence_summary(diagnostic_results)
        
        # Detailed analysis section
        with st.expander("📋 Detailed Clinical Analysis", expanded=False):
            st.subheader("AI Reasoning Process")
            if diagnostic_results.get('reasoning'):
                st.write(diagnostic_results['reasoning'])
            
            st.subheader("Data Quality Assessment")
            quality_metrics = data_processor.assess_data_quality(patient_data)
            ui_components.display_quality_metrics(quality_metrics)
            
            st.subheader("Validation Metrics")
            if diagnostic_results.get('validation'):
                validation_data = diagnostic_results['validation']
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Analysis Confidence", f"{validation_data.get('overall_confidence', 0):.2f}")
                with col2:
                    st.metric("Evidence Strength", validation_data.get('evidence_strength', 'N/A'))
                with col3:
                    st.metric("Recommendation Level", validation_data.get('recommendation_level', 'N/A'))
        
        # Export functionality
        st.header("📤 Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Generate Clinical Report"):
                report = ui_components.generate_clinical_report(diagnostic_results, patient_data)
                st.download_button(
                    label="💾 Download Clinical Report",
                    data=report,
                    file_name=f"diagnostic_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("📊 Export Data"):
                export_data = ui_components.prepare_export_data(diagnostic_results)
                st.download_button(
                    label="💾 Download JSON Data",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"diagnostic_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    except Exception as e:
        st.error(f"❌ An error occurred during analysis: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()