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
            'netflix_red': '#E50914',
            'netflix_black': '#141414',
            'netflix_dark_gray': '#2F2F2F',
            'netflix_gray': '#808080',
            'medical_blue': '#2E86AB',
            'medical_green': '#28A745',
            'medical_orange': '#FD7E14',
            'medical_purple': '#6F42C1',
            'success_green': '#00D4AA',
            'warning_orange': '#FF8A00',
            'danger_red': '#FF3366',
            'background_dark': '#0F0F0F',
            'card_dark': '#1A1A1A',
            'text_primary': '#FFFFFF',
            'text_secondary': '#B3B3B3'
        }
    
    def display_welcome_screen(self):
        """
        Display Netflix-style welcome screen with instructions
        """
        st.markdown("""
        <div class="netflix-card" style="text-align: center; padding: 3rem;">
            <h1 style="color: var(--text-primary); margin-bottom: 2rem;">🏥 Welcome to AI Medical Diagnostic Assistant</h1>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0;">
                <div class="netflix-card" style="padding: 2rem;">
                    <h3 style="color: var(--medical-blue); margin-bottom: 1rem;">📋 Upload Patient Data</h3>
                    <p style="color: var(--text-secondary);">Support for CSV, JSON, TXT, and PDF files containing comprehensive patient information</p>
                </div>
                
                <div class="netflix-card" style="padding: 2rem;">
                    <h3 style="color: var(--medical-green); margin-bottom: 1rem;">🧠 AI Analysis</h3>
                    <p style="color: var(--text-secondary);">Advanced AI-powered diagnostic insights with confidence scoring and risk stratification</p>
                </div>
                
                <div class="netflix-card" style="padding: 2rem;">
                    <h3 style="color: var(--medical-purple); margin-bottom: 1rem;">📊 Clinical Reports</h3>
                    <p style="color: var(--text-secondary);">Comprehensive diagnostic reports with evidence-based recommendations</p>
                </div>
            </div>
            
            <div style="background: rgba(229, 9, 20, 0.1); padding: 2rem; border-radius: 15px; border: 1px solid var(--netflix-red); margin: 2rem 0;">
                <h3 style="color: var(--netflix-red); margin-bottom: 1rem;">⚠️ Important Medical Disclaimer</h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.6;">
                    This tool is designed for <strong>educational and clinical decision support purposes only</strong>.
                    All diagnostic recommendations should be <strong>validated by qualified healthcare professionals</strong>.
                    This system <strong>does not replace clinical judgment</strong> or direct patient care.
                    <strong>Always consult with appropriate medical specialists</strong> for definitive diagnosis and treatment.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display supported data types
        with st.expander("📋 Supported Data Types", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Clinical Data:**
                - Demographics (Age, Gender, Race/Ethnicity)
                - Vital Signs (Temperature, BP, HR, RR, O2 Sat)
                - Symptoms (Chief complaint, History, Duration)
                - Medical History (PMH, Surgical, Family, Allergies)
                """)
            
            with col2:
                st.markdown("""
                **Diagnostic Data:**
                - Laboratory Results (Blood work, Urinalysis, Cultures)
                - Imaging (X-rays, CT, MRI, Radiology reports)
                - Medications (Current, Dosages, Drug allergies)
                - Clinical Notes (Provider notes, Physical exam)
                """)
            
            # Sample data format
            st.subheader("Sample Data Format (CSV)")
            sample_data = {
                'patient_id': ['001', '002', '003'],
                'age': [45, 67, 32],
                'gender': ['Female', 'Male', 'Female'],
                'chief_complaint': ['Chest pain', 'Shortness of breath', 'Abdominal pain'],
                'temperature': [98.6, 100.2, 99.1],
                'blood_pressure': ['120/80', '150/95', '110/70'],
                'heart_rate': [72, 88, 95],
                'symptoms': [
                    'Sharp chest pain, radiating to left arm', 
                    'Difficulty breathing, swollen ankles',
                    'Nausea, vomiting, lower right quadrant pain'
                ],
                'medical_history': ['Hypertension', 'Diabetes, CAD', 'None significant']
            }
            
            sample_df = pd.DataFrame(sample_data)
            st.dataframe(sample_df, use_container_width=True)
    
    def display_diagnosis_card(self, diagnosis: Dict[str, Any], rank: int):
        """
        Display a Netflix-style diagnosis card with comprehensive information
        """
        confidence = diagnosis.get('confidence_score', 0)
        risk_level = diagnosis.get('risk_level', 'Medium')
        condition = diagnosis.get('condition', 'Unknown Condition')
        
        # Determine confidence and risk styling
        confidence_class = "high" if confidence >= 0.8 else "medium" if confidence >= 0.5 else "low"
        risk_class = risk_level.lower()
        
        st.markdown(f"""
        <div class="diagnosis-card" style="border-left: 4px solid var(--medical-{'blue' if confidence >= 0.8 else 'orange' if confidence >= 0.5 else 'red'});">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="margin: 0; color: var(--text-primary);">#{rank} {condition}</h3>
                <div style="display: flex; gap: 1rem; align-items: center;">
                    <span class="confidence-{confidence_class}" style="font-weight: 600;">{confidence:.1%}</span>
                    <span class="risk-{risk_class}">{risk_level} Risk</span>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                <div>
                    <strong style="color: var(--text-secondary);">Specialty:</strong>
                    <span style="color: var(--text-primary);"> {diagnosis.get('specialty', 'General Medicine')}</span>
                </div>
                <div>
                    <strong style="color: var(--text-secondary);">ICD-10:</strong>
                    <span style="color: var(--text-primary);"> {diagnosis.get('icd_10_code', 'Not specified')}</span>
                </div>
            </div>
            
            <div style="margin-bottom: 1rem;">
                <strong style="color: var(--text-secondary);">Clinical Reasoning:</strong>
                <p style="color: var(--text-primary); margin: 0.5rem 0;">{diagnosis.get('clinical_reasoning', 'No reasoning provided')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable sections for detailed information
        with st.expander(f"📋 Detailed Analysis - {condition}", expanded=False):
            if diagnosis.get('supporting_evidence'):
                st.markdown("**Supporting Evidence:**")
                for evidence in diagnosis['supporting_evidence']:
                    st.markdown(f"• {evidence}")
            
            st.markdown("**Recommended Next Steps:**")
            st.markdown(diagnosis.get('next_steps', 'Consult healthcare provider for further evaluation'))
    
    def create_confidence_chart(self, diagnoses: List[Dict[str, Any]]):
        """
        Create Netflix-style confidence score visualization
        """
        if not diagnoses:
            st.warning("No diagnostic data available for visualization")
            return
        
        # Prepare data
        conditions = []
        confidence_scores = []
        colors = []
        
        for d in diagnoses:
            condition = d.get('condition', 'Unknown')
            # Truncate long condition names
            display_name = condition[:40] + '...' if len(condition) > 40 else condition
            conditions.append(display_name)
            
            confidence = d.get('confidence_score', 0)
            confidence_scores.append(confidence)
            
            # Color based on confidence level
            if confidence >= 0.8:
                colors.append(self.colors['success_green'])
            elif confidence >= 0.5:
                colors.append(self.colors['warning_orange'])
            else:
                colors.append(self.colors['danger_red'])
        
        # Create horizontal bar chart with Netflix styling
        fig = go.Figure(data=[
            go.Bar(
                y=conditions,
                x=confidence_scores,
                orientation='h',
                marker=dict(
                    color=colors,
                    line=dict(color='rgba(255,255,255,0.1)', width=1)
                ),
                text=[f"{score:.1%}" for score in confidence_scores],
                textposition='inside',
                textfont=dict(color='white', size=12, family='Inter')
            )
        ])
        
        fig.update_layout(
            title={
                'text': "Diagnostic Confidence Scores",
                'x': 0.5,
                'font': {'size': 20, 'color': self.colors['text_primary'], 'family': 'Inter'}
            },
            xaxis_title="Confidence Score",
            yaxis_title="Differential Diagnoses",
            height=max(400, len(diagnoses) * 60),
            showlegend=False,
            plot_bgcolor=self.colors['background_dark'],
            paper_bgcolor=self.colors['background_dark'],
            font=dict(color=self.colors['text_primary'], family='Inter')
        )
        
        fig.update_xaxes(
            range=[0, 1], 
            tickformat='.0%',
            gridcolor='rgba(255,255,255,0.1)',
            title_font=dict(color=self.colors['text_secondary'])
        )
        
        fig.update_yaxes(
            categoryorder='total ascending',
            gridcolor='rgba(255,255,255,0.1)',
            title_font=dict(color=self.colors['text_secondary'])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_risk_stratification_chart(self, diagnoses: List[Dict[str, Any]]):
        """
        Create Netflix-style risk stratification visualization
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
        
        # Create donut chart with Netflix styling
        labels = list(risk_counts.keys())
        values = list(risk_counts.values())
        colors = [self.colors['danger_red'], self.colors['warning_orange'], self.colors['success_green']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(
                colors=colors,
                line=dict(color=self.colors['background_dark'], width=2)
            ),
            textinfo='label+percent+value',
            textfont=dict(size=14, color='white', family='Inter'),
            hole=0.5
        )])
        
        fig.update_layout(
            title={
                'text': "Risk Stratification Distribution",
                'x': 0.5,
                'font': {'size': 20, 'color': self.colors['text_primary'], 'family': 'Inter'}
            },
            showlegend=True,
            legend=dict(
                font=dict(color=self.colors['text_primary'], family='Inter'),
                bgcolor='rgba(0,0,0,0)'
            ),
            height=400,
            plot_bgcolor=self.colors['background_dark'],
            paper_bgcolor=self.colors['background_dark']
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk level metrics with Netflix styling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="netflix-card" style="text-align: center; border-left: 4px solid var(--danger-red);">
                <h2 style="color: var(--danger-red); margin: 0;">🔴 {risk_counts['High']}</h2>
                <p style="color: var(--text-secondary); margin: 0;">High Risk</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="netflix-card" style="text-align: center; border-left: 4px solid var(--warning-orange);">
                <h2 style="color: var(--warning-orange); margin: 0;">🟡 {risk_counts['Medium']}</h2>
                <p style="color: var(--text-secondary); margin: 0;">Medium Risk</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="netflix-card" style="text-align: center; border-left: 4px solid var(--success-green);">
                <h2 style="color: var(--success-green); margin: 0;">🟢 {risk_counts['Low']}</h2>
                <p style="color: var(--text-secondary); margin: 0;">Low Risk</p>
            </div>
            """, unsafe_allow_html=True)
    
    def display_evidence_summary(self, diagnostic_results: Dict[str, Any]):
        """
        Display Netflix-style evidence summary and validation metrics
        """
        if not diagnostic_results:
            st.warning("No diagnostic results available")
            return
        
        st.markdown("""
        <div class="netflix-card">
            <h2 style="color: var(--text-primary); margin-bottom: 1rem;">📊 Evidence-Based Analysis Summary</h2>
        </div>
        """, unsafe_allow_html=True)
        
        validation = diagnostic_results.get('validation', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Analysis Quality Metrics:**")
            
            overall_confidence = validation.get('overall_confidence', 0)
            st.markdown(f"""
            <div class="netflix-card" style="padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--text-secondary);">Overall Confidence</span>
                    <span style="color: var(--text-primary); font-weight: 600;">{overall_confidence:.1%}</span>
                </div>
                <div style="background: var(--netflix-dark-gray); border-radius: 10px; height: 8px; margin-top: 0.5rem;">
                    <div style="background: linear-gradient(90deg, var(--netflix-red), var(--medical-blue)); 
                                width: {overall_confidence:.0%}; height: 100%; border-radius: 10px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            evidence_strength = validation.get('evidence_strength', 'Unknown')
            strength_color = {
                'Strong': self.colors['success_green'],
                'Moderate': self.colors['warning_orange'],
                'Weak': self.colors['danger_red']
            }.get(evidence_strength, self.colors['text_primary'])
            
            st.markdown(f"""
            <div class="netflix-card" style="padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--text-secondary);">Evidence Strength</span>
                    <span style="color: {strength_color}; font-weight: 600;">{evidence_strength}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Diagnostic Distribution:**")
            
            if diagnostic_results.get('diagnoses'):
                # Specialty distribution
                specialties = {}
                for diagnosis in diagnostic_results['diagnoses']:
                    specialty = diagnosis.get('specialty', 'General Medicine')
                    specialties[specialty] = specialties.get(specialty, 0) + 1
                
                for specialty, count in specialties.items():
                    st.markdown(f"""
                    <div class="netflix-card" style="padding: 0.5rem 1rem; margin-bottom: 0.5rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: var(--text-primary);">{specialty}</span>
                            <span style="color: var(--medical-blue); font-weight: 600;">{count}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Analysis limitations and recommendations
        if validation.get('limitations'):
            st.markdown(f"""
            <div class="netflix-card" style="border-left: 4px solid var(--warning-orange); margin-top: 1rem;">
                <h4 style="color: var(--warning-orange); margin-bottom: 0.5rem;">⚠️ Analysis Limitations</h4>
                <p style="color: var(--text-secondary); margin: 0;">{validation['limitations']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # AI reasoning summary
        if diagnostic_results.get('reasoning'):
            with st.expander("🧠 AI Diagnostic Reasoning Process", expanded=False):
                st.markdown(f"""
                <div class="netflix-card">
                    <p style="color: var(--text-primary); line-height: 1.6;">{diagnostic_results['reasoning']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    def display_loading_state(self, message: str = "Processing..."):
        """Display Netflix-style loading state"""
        st.markdown(f"""
        <div class="netflix-card" style="text-align: center; padding: 3rem;">
            <div class="loading-spinner" style="margin: 0 auto 1rem;"></div>
            <h3 style="color: var(--text-primary); margin: 0;">{message}</h3>
            <p style="color: var(--text-secondary); margin-top: 0.5rem;">Please wait while we analyze your data...</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_error_state(self, error_message: str):
        """Display Netflix-style error state"""
        st.markdown(f"""
        <div class="netflix-card" style="border-left: 4px solid var(--danger-red); text-align: center; padding: 2rem;">
            <h3 style="color: var(--danger-red); margin-bottom: 1rem;">❌ Error</h3>
            <p style="color: var(--text-secondary); margin: 0;">{error_message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_success_state(self, message: str):
        """Display Netflix-style success state"""
        st.markdown(f"""
        <div class="netflix-card" style="border-left: 4px solid var(--success-green); text-align: center; padding: 2rem;">
            <h3 style="color: var(--success-green); margin-bottom: 1rem;">✅ Success</h3>
            <p style="color: var(--text-secondary); margin: 0;">{message}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _get_confidence_color(self, score: float) -> str:
        """Get color based on confidence score"""
        if score >= 0.8:
            return self.colors['success_green']
        elif score >= 0.5:
            return self.colors['warning_orange']
        else:
            return self.colors['danger_red']
