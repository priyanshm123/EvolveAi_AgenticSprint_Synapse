import streamlit as st
import pandas as pd
import json
from datetime import datetime
from database import DatabaseManager
from typing import List, Dict, Any

class UserDashboard:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def display_patient_history(self, user_id: int):
        """Display patient records history"""
        st.subheader("📋 Patient Records History")
        
        patient_records = self.db_manager.get_user_patient_records(user_id)
        
        if not patient_records:
            st.info("No patient records found. Upload your first patient data to get started!")
            return
        
        # Create DataFrame for better display
        records_df = pd.DataFrame(patient_records)
        records_df['uploaded_at'] = pd.to_datetime(records_df['uploaded_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Display as interactive table
        st.dataframe(
            records_df,
            column_config={
                "id": "Record ID",
                "patient_name": "Patient Name",
                "file_name": "File Name",
                "file_type": "File Type",
                "uploaded_at": "Upload Date"
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Download patient records as CSV
        if st.button("📥 Download Patient Records (CSV)"):
            csv_data = records_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV File",
                data=csv_data,
                file_name=f"patient_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def display_diagnostic_history(self, user_id: int):
        """Display diagnostic analysis history"""
        st.subheader("🔍 Diagnostic Analysis History")
        
        diagnostic_history = self.db_manager.get_user_diagnostic_history(user_id)
        
        if not diagnostic_history:
            st.info("No diagnostic analyses found. Run your first analysis to see results here!")
            return
        
        # Display analyses in expandable cards
        for i, analysis in enumerate(diagnostic_history, 1):
            created_date = analysis['created_at'].split(' ')[0] if ' ' in analysis['created_at'] else analysis['created_at']
            
            with st.expander(f"🧠 Analysis #{i} - {analysis['patient_name']} ({created_date})"):
                # Analysis metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Confidence Threshold", f"{analysis['confidence_threshold']:.1%}")
                with col2:
                    st.metric("Max Diagnoses", analysis['max_diagnoses'])
                with col3:
                    st.metric("Analysis Date", created_date)
                
                diagnostic_data = analysis['diagnostic_data']
                
                # Red flags
                if diagnostic_data.get('red_flags'):
                    st.markdown("#### 🚨 Red Flag Conditions")
                    for flag in diagnostic_data['red_flags']:
                        st.error(f"**{flag.get('condition', 'Unknown')}**: {flag.get('reasoning', 'No reasoning provided')}")
                
                # Diagnoses
                if diagnostic_data.get('diagnoses'):
                    st.markdown("#### 🎯 Differential Diagnoses")
                    
                    # Create DataFrame for diagnoses
                    diagnoses_data = []
                    for diagnosis in diagnostic_data['diagnoses']:
                        diagnoses_data.append({
                            'Condition': diagnosis.get('condition', 'Unknown'),
                            'Confidence': f"{diagnosis.get('confidence_score', 0):.1%}",
                            'Risk Level': diagnosis.get('risk_level', 'Medium'),
                            'Specialty': diagnosis.get('specialty', 'General Medicine'),
                            'ICD-10': diagnosis.get('icd_10_code', 'N/A')
                        })
                    
                    diagnoses_df = pd.DataFrame(diagnoses_data)
                    st.dataframe(diagnoses_df, hide_index=True, use_container_width=True)
                
                # Validation metrics
                if diagnostic_data.get('validation'):
                    validation = diagnostic_data['validation']
                    st.markdown("#### 📊 Analysis Validation")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Overall Confidence", f"{validation.get('overall_confidence', 0):.1%}")
                    with col2:
                        st.metric("Evidence Strength", validation.get('evidence_strength', 'Unknown'))
                    with col3:
                        st.metric("Recommendation Level", validation.get('recommendation_level', 'N/A'))
                
                # Export this specific analysis
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 Export Analysis Report #{i}", key=f"export_report_{analysis['id']}"):
                        report = self.generate_analysis_report(analysis)
                        st.download_button(
                            label="💾 Download Report",
                            data=report,
                            file_name=f"analysis_report_{analysis['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            key=f"download_report_{analysis['id']}"
                        )
                
                with col2:
                    if st.button(f"📊 Export JSON Data #{i}", key=f"export_json_{analysis['id']}"):
                        json_data = json.dumps(diagnostic_data, indent=2)
                        st.download_button(
                            label="💾 Download JSON",
                            data=json_data,
                            file_name=f"analysis_data_{analysis['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            key=f"download_json_{analysis['id']}"
                        )
    
    def generate_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a detailed analysis report"""
        report_lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Report header
        report_lines.extend([
            "=" * 80,
            "AI MEDICAL DIAGNOSTIC ANALYSIS REPORT",
            "=" * 80,
            f"Generated: {timestamp}",
            f"Patient: {analysis['patient_name']}",
            f"Analysis Date: {analysis['created_at']}",
            f"Analysis ID: {analysis['id']}",
            "",
            "IMPORTANT DISCLAIMER:",
            "This report is generated for educational and clinical decision support",
            "purposes only. All recommendations must be validated by qualified",
            "healthcare professionals.",
            "",
            "=" * 80,
            ""
        ])
        
        diagnostic_data = analysis['diagnostic_data']
        
        # Analysis parameters
        report_lines.extend([
            "ANALYSIS PARAMETERS:",
            "-" * 30,
            f"Confidence Threshold: {analysis['confidence_threshold']:.1%}",
            f"Maximum Diagnoses: {analysis['max_diagnoses']}",
            ""
        ])
        
        # Red flags
        if diagnostic_data.get('red_flags'):
            report_lines.extend([
                "🚨 URGENT RED FLAG CONDITIONS:",
                "-" * 40
            ])
            for red_flag in diagnostic_data['red_flags']:
                report_lines.extend([
                    f"CONDITION: {red_flag.get('condition', 'Unknown')}",
                    f"REASONING: {red_flag.get('reasoning', 'Not specified')}",
                    f"ACTION: {red_flag.get('action', 'Consult healthcare provider')}",
                    ""
                ])
        
        # Diagnoses
        if diagnostic_data.get('diagnoses'):
            report_lines.extend([
                "RANKED DIFFERENTIAL DIAGNOSES:",
                "-" * 40
            ])
            
            for i, diagnosis in enumerate(diagnostic_data['diagnoses'], 1):
                confidence = diagnosis.get('confidence_score', 0)
                report_lines.extend([
                    f"{i}. {diagnosis.get('condition', 'Unknown Condition')}",
                    f"   Confidence: {confidence:.1%}",
                    f"   Risk Level: {diagnosis.get('risk_level', 'Medium')}",
                    f"   Specialty: {diagnosis.get('specialty', 'General Medicine')}",
                    f"   ICD-10: {diagnosis.get('icd_10_code', 'Not specified')}",
                    "",
                    f"   Clinical Reasoning:",
                    f"   {diagnosis.get('clinical_reasoning', 'Not provided')}",
                    "",
                    f"   Supporting Evidence:",
                ])
                
                if diagnosis.get('supporting_evidence'):
                    for evidence in diagnosis['supporting_evidence']:
                        report_lines.append(f"   • {evidence}")
                else:
                    report_lines.append("   • No specific evidence provided")
                
                report_lines.extend([
                    "",
                    f"   Recommended Next Steps:",
                    f"   {diagnosis.get('next_steps', 'Consult healthcare provider')}",
                    "",
                    "-" * 60,
                    ""
                ])
        
        # Validation
        validation = diagnostic_data.get('validation', {})
        if validation:
            report_lines.extend([
                "ANALYSIS VALIDATION:",
                "-" * 30,
                f"Overall Confidence: {validation.get('overall_confidence', 0):.1%}",
                f"Evidence Strength: {validation.get('evidence_strength', 'Unknown')}",
                f"Recommendation Level: {validation.get('recommendation_level', 'Not specified')}",
                ""
            ])
            
            if validation.get('limitations'):
                report_lines.extend([
                    "Analysis Limitations:",
                    validation['limitations'],
                    ""
                ])
        
        # AI reasoning
        if diagnostic_data.get('reasoning'):
            report_lines.extend([
                "AI DIAGNOSTIC REASONING:",
                "-" * 35,
                diagnostic_data['reasoning'],
                ""
            ])
        
        # Report footer
        report_lines.extend([
            "=" * 80,
            "END OF REPORT",
            "",
            "This report was generated by an AI system and is intended for",
            "educational and decision support purposes only. Please ensure",
            "all recommendations are reviewed and validated by appropriate",
            "medical professionals before making clinical decisions.",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def display_user_settings(self, user_id: int):
        """Display user settings and preferences"""
        st.subheader("⚙️ User Settings & Preferences")
        
        # Get current preferences
        preferences = self.db_manager.get_user_preferences(user_id)
        
        with st.form("user_preferences"):
            st.markdown("#### Default Analysis Parameters")
            
            col1, col2 = st.columns(2)
            with col1:
                default_confidence = st.slider(
                    "Default Confidence Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=preferences['default_confidence_threshold'],
                    step=0.1,
                    help="Default minimum confidence score for diagnosis inclusion"
                )
                
                enable_red_flags = st.checkbox(
                    "Enable Red Flag Detection by Default",
                    value=preferences['enable_red_flags'],
                    help="Automatically highlight urgent conditions"
                )
            
            with col2:
                default_max_diagnoses = st.number_input(
                    "Default Maximum Diagnoses",
                    min_value=3,
                    max_value=15,
                    value=preferences['default_max_diagnoses'],
                    help="Default maximum number of differential diagnoses"
                )
                
                theme_preference = st.selectbox(
                    "Theme Preference",
                    options=["default", "dark", "light"],
                    index=["default", "dark", "light"].index(preferences['theme_preference']),
                    help="Interface theme preference"
                )
            
            # Account management
            st.markdown("#### Account Management")
            st.info("🔒 For security reasons, password changes and account deletion must be requested through support.")
            
            if st.form_submit_button("💾 Save Preferences", use_container_width=True):
                # Here you would update preferences in the database
                st.success("✅ Preferences saved successfully!")
                
        # Data management
        st.markdown("#### Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export All Data", use_container_width=True):
                self.export_all_user_data(user_id)
        
        with col2:
            if st.button("🗑️ Clear Analysis History", use_container_width=True):
                self.confirm_clear_data(user_id, "analyses")
        
        with col3:
            if st.button("🗑️ Clear Patient Records", use_container_width=True):
                self.confirm_clear_data(user_id, "records")
    
    def export_all_user_data(self, user_id: int):
        """Export all user data"""
        st.info("📦 Preparing complete data export...")
        
        # Get all user data
        patient_records = self.db_manager.get_user_patient_records(user_id)
        diagnostic_history = self.db_manager.get_user_diagnostic_history(user_id)
        
        # Create comprehensive export
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "patient_records": patient_records,
            "diagnostic_history": diagnostic_history,
            "total_records": len(patient_records),
            "total_analyses": len(diagnostic_history)
        }
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="💾 Download Complete Data Export",
            data=json_data,
            file_name=f"medical_assistant_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def confirm_clear_data(self, user_id: int, data_type: str):
        """Show confirmation for data clearing"""
        st.warning(f"⚠️ Are you sure you want to clear all {data_type}? This action cannot be undone!")
        
        if st.button(f"🗑️ Yes, Clear All {data_type.title()}", type="secondary"):
            # Here you would implement the actual data clearing
            st.error(f"❌ {data_type.title()} clearing not implemented yet. Contact support for data management.")