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
        """Display patient records history with Netflix styling"""
        st.markdown("### 📋 Patient Records History")
        
        patient_records = self.db_manager.get_user_patient_records(user_id)
        
        if not patient_records:
            st.markdown("""
            <div class="netflix-card" style="text-align: center; padding: 3rem;">
                <h3 style="color: var(--text-secondary); margin-bottom: 1rem;">📂 No Patient Records</h3>
                <p style="color: var(--text-secondary);">Upload your first patient data to get started with AI diagnostic analysis</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Display records in Netflix-style grid
        st.markdown('<div class="patient-grid">', unsafe_allow_html=True)
        
        cols = None
        for i, record in enumerate(patient_records):
            if i % 3 == 0:
                cols = st.columns(3)
            
            if cols:
                with cols[i % 3]:
                    st.markdown(f"""
                <div class="patient-card">
                    <div class="patient-card-header">
                        <div class="patient-avatar">{record['patient_name'][0].upper() if record['patient_name'] else 'U'}</div>
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: var(--text-primary);">{record['patient_name']}</h4>
                            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">{record['file_name']}</p>
                        </div>
                    </div>
                    <div style="margin-top: 1rem;">
                        <div style="display: flex; justify-content: between; align-items: center;">
                            <span style="color: var(--text-secondary); font-size: 0.8rem;">Type:</span>
                            <span style="color: var(--medical-blue); font-weight: 600; font-size: 0.8rem;">{record['file_type'].upper()}</span>
                        </div>
                        <div style="display: flex; justify-content: between; align-items: center; margin-top: 0.5rem;">
                            <span style="color: var(--text-secondary); font-size: 0.8rem;">Uploaded:</span>
                            <span style="color: var(--text-primary); font-size: 0.8rem;">{record['uploaded_at']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("---")
        if st.button("📥 Export All Records (CSV)", type="secondary"):
            records_df = pd.DataFrame(patient_records)
            records_df['uploaded_at'] = pd.to_datetime(records_df['uploaded_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            csv_data = records_df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV File",
                data=csv_data,
                file_name=f"patient_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def display_diagnostic_history(self, user_id: int):
        """Display diagnostic analysis history with Netflix styling"""
        st.markdown("### 🧠 Diagnostic Analysis History")
        
        diagnostic_history = self.db_manager.get_user_diagnostic_history(user_id)
        
        if not diagnostic_history:
            st.markdown("""
            <div class="netflix-card" style="text-align: center; padding: 3rem;">
                <h3 style="color: var(--text-secondary); margin-bottom: 1rem;">🔍 No Analyses Found</h3>
                <p style="color: var(--text-secondary);">Run your first diagnostic analysis to see results here</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Display analyses in Netflix-style cards
        for i, analysis in enumerate(diagnostic_history, 1):
            created_date = analysis['created_at'].split(' ')[0] if ' ' in analysis['created_at'] else analysis['created_at']
            
            with st.expander(f"🧠 Analysis #{i} - {analysis['patient_name']} ({created_date})", expanded=False):
                # Analysis header with metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="netflix-card" style="text-align: center; padding: 1rem;">
                        <h4 style="color: var(--medical-blue); margin: 0;">{analysis['confidence_threshold']:.1%}</h4>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 0.8rem;">Confidence Threshold</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="netflix-card" style="text-align: center; padding: 1rem;">
                        <h4 style="color: var(--medical-green); margin: 0;">{analysis['max_diagnoses']}</h4>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 0.8rem;">Max Diagnoses</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="netflix-card" style="text-align: center; padding: 1rem;">
                        <h4 style="color: var(--medical-purple); margin: 0;">{created_date}</h4>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 0.8rem;">Analysis Date</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                diagnostic_data = analysis['diagnostic_data']
                
                # Red flags section
                if diagnostic_data.get('red_flags'):
                    st.markdown("#### 🚨 Critical Conditions")
                    for flag in diagnostic_data['red_flags']:
                        st.markdown(f"""
                        <div class="netflix-card" style="border-left: 4px solid var(--danger-red);">
                            <h5 style="color: var(--danger-red); margin-bottom: 0.5rem;">{flag.get('condition', 'Unknown')}</h5>
                            <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">{flag.get('reasoning', 'No reasoning provided')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Diagnoses section
                if diagnostic_data.get('diagnoses'):
                    st.markdown("#### 🎯 Differential Diagnoses")
                    
                    # Create diagnoses table
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
                    
                    # Apply styling to dataframe
                    styled_df = diagnoses_df.style.apply(self._style_dataframe_row, axis=1)
                    st.dataframe(styled_df, hide_index=True, use_container_width=True)
                
                # Validation metrics
                if diagnostic_data.get('validation'):
                    validation = diagnostic_data['validation']
                    st.markdown("#### 📊 Analysis Validation")
                    
                    val_col1, val_col2, val_col3 = st.columns(3)
                    with val_col1:
                        confidence = validation.get('overall_confidence', 0)
                        st.markdown(f"""
                        <div class="netflix-card" style="text-align: center; padding: 1rem;">
                            <h4 style="color: var(--success-green); margin: 0;">{confidence:.1%}</h4>
                            <p style="color: var(--text-secondary); margin: 0; font-size: 0.8rem;">Overall Confidence</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with val_col2:
                        strength = validation.get('evidence_strength', 'Unknown')
                        color = 'var(--success-green)' if strength == 'Strong' else 'var(--warning-orange)' if strength == 'Moderate' else 'var(--danger-red)'
                        st.markdown(f"""
                        <div class="netflix-card" style="text-align: center; padding: 1rem;">
                            <h4 style="color: {color}; margin: 0;">{strength}</h4>
                            <p style="color: var(--text-secondary); margin: 0; font-size: 0.8rem;">Evidence Strength</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with val_col3:
                        recommendation = validation.get('recommendation_level', 'N/A')
                        st.markdown(f"""
                        <div class="netflix-card" style="text-align: center; padding: 1rem;">
                            <h4 style="color: var(--medical-blue); margin: 0;">{recommendation}</h4>
                            <p style="color: var(--text-secondary); margin: 0; font-size: 0.8rem;">Recommendation Level</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Export buttons
                st.markdown("---")
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    if st.button(f"📋 Export Report #{i}", key=f"export_report_{analysis['id']}", type="secondary"):
                        report = self.generate_analysis_report(analysis)
                        st.download_button(
                            label="💾 Download Report",
                            data=report,
                            file_name=f"analysis_report_{analysis['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            key=f"download_report_{analysis['id']}"
                        )
                
                with export_col2:
                    if st.button(f"📊 Export JSON #{i}", key=f"export_json_{analysis['id']}", type="secondary"):
                        json_data = json.dumps(diagnostic_data, indent=2)
                        st.download_button(
                            label="💾 Download JSON",
                            data=json_data,
                            file_name=f"analysis_data_{analysis['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            key=f"download_json_{analysis['id']}"
                        )
    
    def _style_dataframe_row(self, row):
        """Apply Netflix-style styling to dataframe rows"""
        styles = [''] * len(row)
        
        # Color code confidence levels
        confidence_str = row['Confidence']
        if confidence_str.endswith('%'):
            confidence_val = float(confidence_str[:-1]) / 100
            if confidence_val >= 0.8:
                styles[1] = 'color: #00D4AA; font-weight: bold'
            elif confidence_val >= 0.5:
                styles[1] = 'color: #FF8A00; font-weight: bold'
            else:
                styles[1] = 'color: #FF3366; font-weight: bold'
        
        # Color code risk levels
        risk_level = row['Risk Level']
        if risk_level == 'High':
            styles[2] = 'color: #FF3366; font-weight: bold'
        elif risk_level == 'Medium':
            styles[2] = 'color: #FF8A00; font-weight: bold'
        else:
            styles[2] = 'color: #00D4AA; font-weight: bold'
        
        return styles
    
    def generate_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive analysis report"""
        report_lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Report header with Netflix-style branding
        report_lines.extend([
            "=" * 80,
            "🏥 AI MEDICAL DIAGNOSTIC ANALYSIS REPORT",
            "=" * 80,
            f"Generated: {timestamp}",
            f"Patient: {analysis['patient_name']}",
            f"Analysis Date: {analysis['created_at']}",
            f"Analysis ID: {analysis['id']}",
            "",
            "⚠️ IMPORTANT MEDICAL DISCLAIMER:",
            "This report is generated for educational and clinical decision support",
            "purposes only. All recommendations must be validated by qualified",
            "healthcare professionals. This system does not replace clinical",
            "judgment or direct patient care.",
            "",
            "=" * 80,
            ""
        ])
        
        diagnostic_data = analysis['diagnostic_data']
        
        # Analysis parameters
        report_lines.extend([
            "📊 ANALYSIS PARAMETERS:",
            "-" * 30,
            f"Confidence Threshold: {analysis['confidence_threshold']:.1%}",
            f"Maximum Diagnoses: {analysis['max_diagnoses']}",
            f"Red Flag Detection: {'Enabled' if diagnostic_data.get('red_flags') else 'Disabled'}",
            ""
        ])
        
        # Red flags section
        if diagnostic_data.get('red_flags'):
            report_lines.extend([
                "🚨 CRITICAL CONDITIONS DETECTED:",
                "-" * 40
            ])
            for red_flag in diagnostic_data['red_flags']:
                report_lines.extend([
                    f"CONDITION: {red_flag.get('condition', 'Unknown')}",
                    f"CLINICAL REASONING: {red_flag.get('reasoning', 'Not specified')}",
                    f"RECOMMENDED ACTION: {red_flag.get('action', 'Consult healthcare provider immediately')}",
                    f"URGENCY LEVEL: {red_flag.get('urgency', 'HIGH')}",
                    ""
                ])
        
        # Differential diagnoses
        if diagnostic_data.get('diagnoses'):
            report_lines.extend([
                "🎯 RANKED DIFFERENTIAL DIAGNOSES:",
                "-" * 40
            ])
            
            for i, diagnosis in enumerate(diagnostic_data['diagnoses'], 1):
                confidence = diagnosis.get('confidence_score', 0)
                report_lines.extend([
                    f"{i}. {diagnosis.get('condition', 'Unknown Condition')}",
                    f"   Diagnostic Confidence: {confidence:.1%}",
                    f"   Risk Stratification: {diagnosis.get('risk_level', 'Medium')} Risk",
                    f"   Medical Specialty: {diagnosis.get('specialty', 'General Medicine')}",
                    f"   ICD-10 Code: {diagnosis.get('icd_10_code', 'Not specified')}",
                    "",
                    f"   📋 Clinical Reasoning:",
                    f"   {diagnosis.get('clinical_reasoning', 'No detailed reasoning provided')}",
                    "",
                    f"   🔍 Supporting Clinical Evidence:",
                ])
                
                if diagnosis.get('supporting_evidence'):
                    for evidence in diagnosis['supporting_evidence']:
                        report_lines.append(f"   • {evidence}")
                else:
                    report_lines.append("   • No specific supporting evidence documented")
                
                report_lines.extend([
                    "",
                    f"   🏥 Recommended Clinical Actions:",
                    f"   {diagnosis.get('next_steps', 'Consult appropriate healthcare provider for further evaluation')}",
                    "",
                    f"   💊 Treatment Considerations:",
                    f"   {diagnosis.get('treatment_notes', 'Treatment plan should be individualized based on patient factors')}",
                    "",
                    "-" * 60,
                    ""
                ])
        
        # Analysis validation and quality metrics
        validation = diagnostic_data.get('validation', {})
        if validation:
            report_lines.extend([
                "📈 ANALYSIS QUALITY VALIDATION:",
                "-" * 40,
                f"Overall Diagnostic Confidence: {validation.get('overall_confidence', 0):.1%}",
                f"Evidence Strength Assessment: {validation.get('evidence_strength', 'Not assessed')}",
                f"Clinical Recommendation Level: {validation.get('recommendation_level', 'Not specified')}",
                f"Data Quality Score: {validation.get('data_quality', 'Not assessed')}",
                ""
            ])
            
            if validation.get('limitations'):
                report_lines.extend([
                    "⚠️ Analysis Limitations and Considerations:",
                    validation['limitations'],
                    ""
                ])
            
            if validation.get('methodology'):
                report_lines.extend([
                    "🔬 Diagnostic Methodology:",
                    validation['methodology'],
                    ""
                ])
        
        # AI reasoning process
        if diagnostic_data.get('reasoning'):
            report_lines.extend([
                "🧠 AI DIAGNOSTIC REASONING PROCESS:",
                "-" * 45,
                diagnostic_data['reasoning'],
                ""
            ])
        
        # Clinical recommendations summary
        report_lines.extend([
            "📋 CLINICAL RECOMMENDATIONS SUMMARY:",
            "-" * 45,
            "1. All diagnoses require clinical validation by qualified healthcare providers",
            "2. Consider patient-specific factors including comorbidities and contraindications", 
            "3. Follow institutional protocols for diagnostic workup and treatment",
            "4. Document clinical decision-making rationale in patient medical record",
            "5. Arrange appropriate follow-up care and monitoring as indicated",
            ""
        ])
        
        # Report footer
        report_lines.extend([
            "=" * 80,
            "END OF DIAGNOSTIC ANALYSIS REPORT",
            "",
            "This AI-generated report serves as a clinical decision support tool.",
            "Final diagnostic and treatment decisions must always be made by",
            "qualified healthcare professionals with appropriate clinical expertise.",
            "",
            "Report generated by AI Medical Diagnostic Assistant v2.0",
            f"Analysis completed at: {timestamp}",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def display_user_settings(self, user_id: int):
        """Display user settings with Netflix styling"""
        st.markdown("### ⚙️ User Settings & Preferences")
        
        # Get current preferences
        preferences = self.db_manager.get_user_preferences(user_id)
        
        with st.form("user_preferences"):
            st.markdown("#### 🎛️ Default Analysis Parameters")
            
            col1, col2 = st.columns(2)
            with col1:
                default_confidence = st.slider(
                    "Default Confidence Threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=preferences['default_confidence_threshold'],
                    step=0.1,
                    help="Minimum confidence score for diagnosis inclusion"
                )
                
                enable_red_flags = st.checkbox(
                    "Enable Red Flag Detection by Default",
                    value=preferences['enable_red_flags'],
                    help="Automatically highlight urgent conditions requiring immediate attention"
                )
            
            with col2:
                default_max_diagnoses = st.number_input(
                    "Default Maximum Diagnoses",
                    min_value=3,
                    max_value=15,
                    value=preferences['default_max_diagnoses'],
                    help="Maximum number of differential diagnoses to display"
                )
                
                theme_preference = st.selectbox(
                    "Theme Preference",
                    options=['dark', 'light'],
                    index=0 if preferences['theme_preference'] == 'dark' else 1,
                    help="Choose your preferred interface theme"
                )
            
            st.markdown("#### 🔒 Privacy & Security Settings")
            
            data_retention = st.selectbox(
                "Data Retention Policy",
                options=['30_days', '90_days', '1_year', 'indefinite'],
                index=2,
                help="How long to retain patient data and analysis results"
            )
            
            export_format = st.selectbox(
                "Default Export Format",
                options=['pdf', 'txt', 'json', 'csv'],
                index=1,
                help="Preferred format for exporting analysis reports"
            )
            
            if st.form_submit_button("💾 Save Settings", type="primary"):
                updated_preferences = {
                    'default_confidence_threshold': default_confidence,
                    'default_max_diagnoses': default_max_diagnoses,
                    'enable_red_flags': enable_red_flags,
                    'theme_preference': theme_preference
                }
                
                if self.db_manager.update_user_preferences(user_id, updated_preferences):
                    st.success("✅ Settings saved successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to save settings. Please try again.")
        
        # Account information section
        st.markdown("---")
        st.markdown("#### 👤 Account Information")
        
        user_data = st.session_state.get('user', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="netflix-card" style="padding: 1rem;">
                <p style="color: var(--text-secondary); margin: 0;">Username</p>
                <h4 style="color: var(--text-primary); margin: 0;">{user_data.get('username', 'N/A')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="netflix-card" style="padding: 1rem;">
                <p style="color: var(--text-secondary); margin: 0;">Role</p>
                <h4 style="color: var(--medical-blue); margin: 0;">{user_data.get('role', 'User').title()}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="netflix-card" style="padding: 1rem;">
                <p style="color: var(--text-secondary); margin: 0;">Email</p>
                <h4 style="color: var(--text-primary); margin: 0;">{user_data.get('email', 'N/A')}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="netflix-card" style="padding: 1rem;">
                <p style="color: var(--text-secondary); margin: 0;">Full Name</p>
                <h4 style="color: var(--text-primary); margin: 0;">{user_data.get('full_name', 'N/A')}</h4>
            </div>
            """, unsafe_allow_html=True)
        
        # Logout section
        st.markdown("---")
        if st.button("🚪 Logout", type="secondary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
