import json
import os
import google.generativeai as genai
import streamlit as st
from typing import List, Dict, Any

class DiagnosticEngine:
    def __init__(self):
        try:
            # You must set the GOOGLE_API_KEY environment variable for this to work
            genai.configure(api_key=os.getenv("AIzaSyBACPuxiPqCmWmiTWBjzy6xefDck2IXQy8"))
            # We'll use Gemini 1.5 Flash, which is fast, capable, and has a great free tier
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            # Handle cases where the API key might be missing or invalid
            st.error(f"Error configuring the Google AI client: {e}")
            self.model = None

    def analyze_patient_data(self, patient_data: List[Dict], confidence_threshold: float = 0.3,
                           max_diagnoses: int = 8, include_red_flags: bool = True) -> Dict[str, Any]:
        """
        Analyze patient data and generate diagnostic recommendations using Google Gemini.
        """
        if not self.model:
            st.error("Diagnostic engine is not initialized. Please check your API key.")
            return {}

        try:
            data_summary = self._prepare_data_summary(patient_data)
            diagnostic_prompt = self._create_diagnostic_prompt(
                data_summary, confidence_threshold, max_diagnoses, include_red_flags
            )

            full_prompt = self._get_system_prompt() + "\n\n" + diagnostic_prompt
            
            generation_config = genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.2
            )

            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            response_content = response.text
            if not response_content:
                raise ValueError("No response content received from AI model")

            diagnostic_results = json.loads(response_content)
            return self._post_process_results(diagnostic_results)

        except Exception as e:
            st.error(f"Error in diagnostic analysis: {str(e)}")
            return {}

    def _prepare_data_summary(self, patient_data: List[Dict]) -> str:
        """
        Prepare a comprehensive summary of patient data for analysis
        """
        summary_parts = []
        
        for i, record in enumerate(patient_data):
            record_summary = f"Patient Record {i+1}:\n"
            
            categories = {
                "Demographics": ["age", "gender", "race", "ethnicity"],
                "Vital Signs": ["temperature", "blood_pressure", "heart_rate", "respiratory_rate", "oxygen_saturation"],
                "Symptoms": ["chief_complaint", "symptoms", "present_illness", "symptom_duration"],
                "Medical History": ["past_medical_history", "surgical_history", "family_history", "allergies"],
                "Medications": ["current_medications", "medications", "drug_allergies"],
                "Laboratory Results": ["lab_results", "blood_work", "urinalysis", "cultures"],
                "Imaging": ["imaging_results", "radiology", "ct_scan", "mri", "xray"],
                "Physical Exam": ["physical_examination", "physical_findings", "exam_findings"],
                "Clinical Notes": ["clinical_notes", "provider_notes", "assessment", "plan"]
            }
            
            for category, fields in categories.items():
                category_data = []
                for field in fields:
                    for key, value in record.items():
                        if field.lower() in key.lower() and value:
                            category_data.append(f"{key}: {value}")
                
                if category_data:
                    record_summary += f"\n{category}:\n" + "\n".join(category_data) + "\n"
            
            summary_parts.append(record_summary)
        
        return "\n".join(summary_parts)

    def _create_diagnostic_prompt(self, data_summary: str, confidence_threshold: float,
                                max_diagnoses: int, include_red_flags: bool) -> str:
        """
        Create the diagnostic analysis prompt
        """
        prompt = f"""
        Please analyze the following patient data and provide a comprehensive diagnostic assessment.

        PATIENT DATA:
        {data_summary}

        ANALYSIS REQUIREMENTS:
        - Generate up to {max_diagnoses} differential diagnoses
        - Include confidence scores (0.0-1.0) for each diagnosis
        - Only include diagnoses with confidence >= {confidence_threshold}
        - Provide clinical reasoning and evidence for each diagnosis
        - Assign risk stratification (Low/Medium/High) for each condition
        - Include medical specialty relevance
        """
        
        if include_red_flags:
            prompt += """
        - Identify any urgent red-flag conditions requiring immediate attention
        - Highlight life-threatening or time-sensitive conditions
        """
        
        prompt += """
        
        RESPONSE FORMAT (JSON):
        {{
            "diagnoses": [
                {{
                    "condition": "Diagnosis name",
                    "confidence_score": 0.85,
                    "risk_level": "High/Medium/Low",
                    "specialty": "Relevant medical specialty",
                    "clinical_reasoning": "Detailed reasoning for this diagnosis",
                    "supporting_evidence": ["Evidence point 1", "Evidence point 2"],
                    "icd_10_code": "ICD-10 code if applicable",
                    "next_steps": "Recommended diagnostic or therapeutic steps"
                }}
            ],
            "red_flags": [
                {{
                    "condition": "Urgent condition name",
                    "reasoning": "Why this is urgent",
                    "action": "Immediate recommended action"
                }}
            ],
            "reasoning": "Overall diagnostic reasoning and approach",
            "validation": {{
                "overall_confidence": 0.75,
                "evidence_strength": "Strong/Moderate/Weak",
                "recommendation_level": "Level of recommendation strength",
                "limitations": "Analysis limitations or data gaps"
            }}
        }}
        
        Provide evidence-based medical analysis while noting this is for educational/supportive purposes only and should not replace clinical judgment.
        """
        
        return prompt

    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the AI medical assistant
        """
        return """
        You are an advanced AI medical diagnostic assistant. Your task is to analyze patient data and respond ONLY in the JSON format specified in the user's prompt. 
        Do not add any text, markdown formatting, or explanations before or after the JSON object. Your entire response must be a single, valid JSON object.
        Base all analyses on established medical knowledge. This is for clinical decision support and all recommendations should be validated by a qualified healthcare professional.
        """

    def _post_process_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process and validate the diagnostic results
        """
        if 'diagnoses' not in results:
            results['diagnoses'] = []
        
        if 'red_flags' not in results:
            results['red_flags'] = []
        
        if results['diagnoses']:
            results['diagnoses'] = sorted(
                results['diagnoses'], 
                key=lambda x: x.get('confidence_score', 0), 
                reverse=True
            )
        
        for diagnosis in results['diagnoses']:
            diagnosis.setdefault('confidence_score', 0.0)
            diagnosis.setdefault('risk_level', 'Medium')
            diagnosis.setdefault('specialty', 'General Medicine')
            diagnosis.setdefault('clinical_reasoning', 'Analysis pending')
            diagnosis.setdefault('supporting_evidence', [])
            diagnosis.setdefault('next_steps', 'Consult healthcare provider')
            
            diagnosis['confidence_score'] = max(0.0, min(1.0, diagnosis['confidence_score']))
            
            if diagnosis['risk_level'] not in ['High', 'Medium', 'Low']:
                diagnosis['risk_level'] = 'Medium'
        
        return results

    def get_diagnosis_explanation(self, diagnosis: Dict[str, Any], patient_data: List[Dict]) -> str:
        """
        Get detailed explanation for a specific diagnosis using Google Gemini.
        """
        if not self.model:
            return "Unable to generate detailed explanation: Diagnostic engine not initialized."
            
        try:
            explanation_prompt = f"""
            Provide a detailed clinical explanation for the following diagnosis:
            
            DIAGNOSIS: {diagnosis.get('condition', 'Unknown')}
            CONFIDENCE: {diagnosis.get('confidence_score', 0):.2f}
            RISK LEVEL: {diagnosis.get('risk_level', 'Unknown')}
            
            PATIENT CONTEXT: {self._prepare_data_summary(patient_data)}
            
            Please explain:
            1. Clinical pathophysiology
            2. How patient data supports this diagnosis
            3. Typical presentation and progression
            4. Differential considerations
            5. Recommended diagnostic workup
            6. Treatment considerations
            
            Keep explanation clear and evidence-based.
            """
            
            system_prompt = "You are a medical education specialist providing detailed clinical explanations."
            full_prompt = system_prompt + "\n\n" + explanation_prompt

            response = self.model.generate_content(full_prompt)
            
            response_content = response.text
            if not response_content:
                return "Unable to generate detailed explanation: No response content received"
            return response_content
            
        except Exception as e:
            return f"Unable to generate detailed explanation: {str(e)}"