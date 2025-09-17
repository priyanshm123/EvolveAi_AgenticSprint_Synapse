import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any
import json
from datetime import datetime

class UIComponents:
    def __init__(self):
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#28A745',
            'warning': '#FFC107',
            'danger': '#DC3545',
            'background': '#F8F9FA',
            'text': '#212529'
        }
    
    def display_welcome_screen(self):
        """
        Display welcome screen with instructions
        """
        st.markdown("""
        ## 🏥 Welcome to the AI Medical Diagnostic Assistant
        
        This advanced diagnostic tool uses artificial intelligence to analyze patient data and provide evidence-based diagnostic insights.
        
        ### 📋 Getting Started:
        1. **Upload Patient Data**: Use the sidebar to upload CSV, JSON, or text files containing patient information
        2. **Configure Parameters**: Adjust diagnostic parameters and filters as needed
        3. **Review Analysis**: Examine AI-generated differential diagnoses with confidence scores
        4. **Export Results**: Generate clinical reports and export data for further use
        
        ### 📊 Supported Data Types:
        - **Demographics**: Age, gender, race/ethnicity
        - **Vital Signs**: Temperature, blood pressure, heart rate, respiratory rate, oxygen saturation
        - **Symptoms**: Chief complaint, symptom history, duration
        - **Medical History**: Past medical history, surgical history, family history, allergies
        - **Medications**: Current medications, dosages, drug allergies
        - **Laboratory Results**: Blood work, urinalysis, cultures, biomarkers
        - **Imaging**: X-rays, CT scans, MRI results, radiology reports
        - **Clinical Notes**: Provider notes, physical examination findings
        - **PDF Documents**: Medical reports, lab results, discharge summaries, clinical documentation
        
        ### ⚠️ Important Disclaimers:
        - This tool is designed for **educational and clinical decision support purposes only**
        - All diagnostic recommendations should be **validated by qualified healthcare professionals**
        - This system **does not replace clinical judgment** or direct patient care
        - **Always consult with appropriate medical specialists** for definitive diagnosis and treatment
        
        ### 🔒 Privacy & Security:
        - Patient data is processed securely and not stored permanently
        - All analysis occurs in a secure, encrypted environment
        - Follow your institution's data privacy guidelines when using patient information
        
        ---
        
        **Ready to begin?** Upload your patient data files (CSV, JSON, TXT, or PDF) using the sidebar to start the diagnostic analysis.
        """)
        
        # Display sample data format
        with st.expander("📋 Sample Data Format", expanded=False):
            st.subheader("CSV Format Example:")
            sample_csv = pd.DataFrame({
                'age': [45, 67, 32],
                'gender': ['Female', 'Male', 'Female'],
                'chief_complaint': ['Chest pain', 'Shortness of breath', 'Abdominal pain'],
                'temperature': [98.6, 100.2, 99.1],
                'blood_pressure': ['120/80', '150/95', '110/70'],
                'heart_rate': [72, 88, 95],
                'symptoms': ['Sharp chest pain, radiating to left arm', 
                           'Difficulty breathing, swollen ankles',
                           'Nausea, vomiting, lower right quadrant pain'],
                'medical_history': ['Hypertension', 'Diabetes, CAD', 'None significant']
            })
            st.dataframe(sample_csv)
            
            st.subheader("JSON Format Example:")
            sample_json = {
                "patient_id": "001",
                "age": 45,
                "gender": "Female",
                "chief_complaint": "Chest pain",
                "vital_signs": {
                    "temperature": 98.6,
                    "blood_pressure": "120/80",
                    "heart_rate": 72,
                    "respiratory_rate": 16
                },
                "symptoms": ["Sharp chest pain", "Radiating to left arm", "Started 2 hours ago"],
                "medical_history": ["Hypertension", "Family history of CAD"],
                "medications": ["Lisinopril 10mg daily", "Aspirin 81mg daily"],
                "lab_results": {
                    "troponin": "0.02",
                    "creatinine": "1.1",
                    "glucose": "95"
                }
            }
            st.json(sample_json)
    
    def display_diagnosis_card(self, diagnosis: Dict[str, Any], rank: int):
        """
        Display a diagnosis card with all relevant information
        """
        confidence = diagnosis.get('confidence_score', 0)
        risk_level = diagnosis.get('risk_level', 'Medium')
        
        # Determine confidence color class
        if confidence >= 0.8:
            conf_class = "confidence-high"
        elif confidence >= 0.5:
            conf_class = "confidence-medium"
        else:
            conf_class = "confidence-low"
        
        # Create the diagnosis card
        st.markdown(f"""
        <div class="diagnosis-card">
            <h3>#{rank} {diagnosis.get('condition', 'Unknown Condition')}</h3>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <span class="{conf_class}">Confidence: {confidence:.1%}</span>
                <span class="risk-{risk_level.lower()}">Risk: {risk_level}</span>
            </div>
            <p><strong>Specialty:</strong> {diagnosis.get('specialty', 'General Medicine')}</p>
            <p><strong>ICD-10:</strong> {diagnosis.get('icd_10_code', 'Not specified')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable sections for detailed information
        with st.expander(f"📋 Clinical Reasoning - {diagnosis.get('condition')}", expanded=False):
            st.write("**Clinical Reasoning:**")
            st.write(diagnosis.get('clinical_reasoning', 'No reasoning provided'))
            
            if diagnosis.get('supporting_evidence'):
                st.write("**Supporting Evidence:**")
                for evidence in diagnosis['supporting_evidence']:
                    st.write(f"• {evidence}")
            
            st.write("**Recommended Next Steps:**")
            st.write(diagnosis.get('next_steps', 'Consult healthcare provider'))
    
    def create_confidence_chart(self, diagnoses: List[Dict[str, Any]]):
        """
        Create a confidence score visualization
        """
        if not diagnoses:
            st.warning("No diagnostic data available for visualization")
            return
        
        # Prepare data for plotting
        conditions = [d.get('condition', 'Unknown')[:30] + '...' if len(d.get('condition', '')) > 30 
                     else d.get('condition', 'Unknown') for d in diagnoses]
        confidence_scores = [d.get('confidence_score', 0) for d in diagnoses]
        colors = [self._get_confidence_color(score) for score in confidence_scores]
        
        # Create horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=conditions,
                x=confidence_scores,
                orientation='h',
                marker=dict(color=colors),
                text=[f"{score:.1%}" for score in confidence_scores],
                textposition='inside',
                textfont=dict(color='white', weight='bold')
            )
        ])
        
        fig.update_layout(
            title="Diagnostic Confidence Scores",
            xaxis_title="Confidence Score",
            yaxis_title="Differential Diagnoses",
            height=max(400, len(diagnoses) * 50),
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        fig.update_layout(
            xaxis=dict(range=[0, 1], tickformat='.0%'),
            yaxis=dict(categoryorder='total ascending')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_risk_stratification_chart(self, diagnoses: List[Dict[str, Any]]):
        """
        Create risk stratification visualization
        """
        if not diagnoses:
            st.warning("No diagnostic data available for risk stratification")
            return
        
        # Count diagnoses by risk level
        risk_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        for diagnosis in diagnoses:
            risk_level = diagnosis.get('risk_level', 'Medium')
            if risk_level in risk_counts:
                risk_counts[risk_level] += 1
        
        # Create pie chart
        labels = list(risk_counts.keys())
        values = list(risk_counts.values())
        colors = [self.colors['danger'], self.colors['warning'], self.colors['success']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            textinfo='label+percent+value',
            textfont=dict(size=14, color='white'),
            hole=0.4
        )])
        
        fig.update_layout(
            title="Risk Stratification Distribution",
            showlegend=True,
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk level summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔴 High Risk", risk_counts['High'])
        with col2:
            st.metric("🟡 Medium Risk", risk_counts['Medium'])
        with col3:
            st.metric("🟢 Low Risk", risk_counts['Low'])
    
    def display_evidence_summary(self, diagnostic_results: Dict[str, Any]):
        """
        Display evidence summary and validation metrics
        """
        if not diagnostic_results:
            st.warning("No diagnostic results available")
            return
        
        st.subheader("📊 Evidence-Based Analysis Summary")
        
        # Overall analysis metrics
        validation = diagnostic_results.get('validation', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Analysis Quality Metrics:**")
            overall_confidence = validation.get('overall_confidence', 0)
            st.progress(overall_confidence, text=f"Overall Confidence: {overall_confidence:.1%}")
            
            evidence_strength = validation.get('evidence_strength', 'Unknown')
            strength_color = {
                'Strong': self.colors['success'],
                'Moderate': self.colors['warning'],
                'Weak': self.colors['danger']
            }.get(evidence_strength, self.colors['text'])
            
            st.markdown(f"**Evidence Strength:** <span style='color: {strength_color}'>{evidence_strength}</span>", 
                       unsafe_allow_html=True)
            
            recommendation_level = validation.get('recommendation_level', 'Not specified')
            st.markdown(f"**Recommendation Level:** {recommendation_level}")
        
        with col2:
            st.markdown("**Diagnostic Distribution:**")
            
            if diagnostic_results.get('diagnoses'):
                # Specialty distribution
                specialties = {}
                for diagnosis in diagnostic_results['diagnoses']:
                    specialty = diagnosis.get('specialty', 'General Medicine')
                    specialties[specialty] = specialties.get(specialty, 0) + 1
                
                specialty_data = [{'Specialty': k, 'Count': v} for k, v in specialties.items()]
                specialty_df = pd.DataFrame(specialty_data)
                st.dataframe(specialty_df, hide_index=True)
        
        # Limitations and recommendations
        if validation.get('limitations'):
            st.markdown("**Analysis Limitations:**")
            st.info(validation['limitations'])
        
        # AI reasoning summary
        if diagnostic_results.get('reasoning'):
            with st.expander("🧠 AI Diagnostic Reasoning Process", expanded=False):
                st.write(diagnostic_results['reasoning'])
    
    def apply_filters(self, diagnoses: List[Dict[str, Any]], urgency_filter: str, 
                     specialty_filter: List[str]) -> List[Dict[str, Any]]:
        """
        Apply filters to the diagnosis list
        """
        filtered_diagnoses = diagnoses.copy()
        
        # Apply urgency filter
        if urgency_filter != "All":
            filtered_diagnoses = [d for d in filtered_diagnoses 
                                if d.get('risk_level', 'Medium') == urgency_filter]
        
        # Apply specialty filter
        if specialty_filter:
            filtered_diagnoses = [d for d in filtered_diagnoses 
                                if d.get('specialty', 'General Medicine') in specialty_filter]
        
        return filtered_diagnoses
    
    def generate_clinical_report(self, diagnostic_results: Dict[str, Any], 
                               patient_data: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive clinical report
        """
        report_lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Report header
        report_lines.extend([
            "=" * 80,
            "AI MEDICAL DIAGNOSTIC ANALYSIS REPORT",
            "=" * 80,
            f"Generated: {timestamp}",
            f"Analysis Engine: AI-Powered Diagnostic Assistant",
            "",
            "IMPORTANT DISCLAIMER:",
            "This report is generated for educational and clinical decision support",
            "purposes only. All recommendations must be validated by qualified",
            "healthcare professionals. This analysis does not replace clinical",
            "judgment or direct patient care.",
            "",
            "=" * 80,
            ""
        ])
        
        # Patient data summary
        report_lines.extend([
            "PATIENT DATA SUMMARY:",
            "-" * 30,
            f"Total Records Analyzed: {len(patient_data)}",
            f"Data Fields Present: {len(patient_data[0].keys()) if patient_data else 0}",
            ""
        ])
        
        # Key patient information (if available)
        if patient_data:
            sample_record = patient_data[0]
            for key, value in sample_record.items():
                if key.lower() in ['age', 'gender', 'chief_complaint', 'symptoms']:
                    report_lines.append(f"{key.title()}: {value}")
            report_lines.append("")
        
        # Red flags section
        if diagnostic_results.get('red_flags'):
            report_lines.extend([
                "🚨 URGENT RED FLAG CONDITIONS:",
                "-" * 40
            ])
            for red_flag in diagnostic_results['red_flags']:
                report_lines.extend([
                    f"CONDITION: {red_flag.get('condition', 'Unknown')}",
                    f"REASONING: {red_flag.get('reasoning', 'Not specified')}",
                    f"ACTION: {red_flag.get('action', 'Consult healthcare provider')}",
                    ""
                ])
        
        # Differential diagnoses
        if diagnostic_results.get('diagnoses'):
            report_lines.extend([
                "RANKED DIFFERENTIAL DIAGNOSES:",
                "-" * 40
            ])
            
            for i, diagnosis in enumerate(diagnostic_results['diagnoses'], 1):
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
                    f"   Recommended Next Steps:",
                    f"   {diagnosis.get('next_steps', 'Consult healthcare provider')}",
                    "",
                    "-" * 60,
                    ""
                ])
        
        # Analysis validation
        validation = diagnostic_results.get('validation', {})
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
        if diagnostic_results.get('reasoning'):
            report_lines.extend([
                "AI DIAGNOSTIC REASONING:",
                "-" * 35,
                diagnostic_results['reasoning'],
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
    
    def prepare_export_data(self, diagnostic_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare diagnostic data for JSON export
        """
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'AI Medical Diagnostic Analysis',
            'version': '1.0',
            'disclaimer': 'This analysis is for educational and clinical decision support purposes only',
            'diagnostic_results': diagnostic_results
        }
        
        return export_data
    
    def display_quality_metrics(self, quality_metrics: Dict[str, Any]):
        """
        Display data quality assessment metrics
        """
        st.subheader("📊 Data Quality Assessment")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            completeness = quality_metrics.get('completeness', 0)
            st.metric("Data Completeness", f"{completeness:.1f}%")
        
        with col2:
            consistency = quality_metrics.get('consistency', 0)
            st.metric("Data Consistency", f"{consistency:.1f}%")
        
        with col3:
            critical_present = quality_metrics.get('critical_fields_present', 0)
            total_critical = quality_metrics.get('total_critical_fields', 0)
            st.metric("Critical Fields", f"{critical_present}/{total_critical}")
        
        with col4:
            quality_score = quality_metrics.get('data_quality_score', 0)
            st.metric("Overall Quality", f"{quality_score:.1f}/100")
        
        # Quality recommendations
        if quality_metrics.get('recommendations'):
            st.subheader("💡 Quality Recommendations")
            for recommendation in quality_metrics['recommendations']:
                st.info(recommendation)
    
    def _get_confidence_color(self, confidence_score: float) -> str:
        """
        Get color based on confidence score
        """
        if confidence_score >= 0.8:
            return self.colors['success']
        elif confidence_score >= 0.5:
            return self.colors['warning']
        else:
            return self.colors['danger']
