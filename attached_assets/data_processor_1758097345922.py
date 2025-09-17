import pandas as pd
import json
import csv
import io
from typing import List, Dict, Any, Union
import streamlit as st
import PyPDF2
import pdfplumber

class DataProcessor:
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'txt', 'pdf']
        self.medical_field_mappings = {
            # Demographics
            'age': ['age', 'patient_age', 'years_old'],
            'gender': ['gender', 'sex', 'patient_gender'],
            'race': ['race', 'ethnicity', 'patient_race'],
            
            # Vital Signs
            'temperature': ['temp', 'temperature', 'body_temp', 'fever'],
            'blood_pressure': ['bp', 'blood_pressure', 'systolic', 'diastolic'],
            'heart_rate': ['hr', 'heart_rate', 'pulse', 'bpm'],
            'respiratory_rate': ['rr', 'resp_rate', 'breathing_rate', 'respiration'],
            'oxygen_saturation': ['o2_sat', 'spo2', 'oxygen_sat', 'sat'],
            
            # Symptoms and History
            'chief_complaint': ['cc', 'chief_complaint', 'main_complaint', 'presenting_complaint'],
            'symptoms': ['symptoms', 'sx', 'complaints', 'presenting_symptoms'],
            'medical_history': ['pmh', 'past_medical_history', 'medical_hx', 'history'],
            'medications': ['meds', 'medications', 'current_meds', 'drugs'],
            
            # Laboratory and Diagnostics
            'lab_results': ['labs', 'lab_results', 'laboratory', 'bloodwork'],
            'imaging': ['imaging', 'radiology', 'scans', 'xray', 'ct', 'mri'],
            'clinical_notes': ['notes', 'clinical_notes', 'provider_notes', 'assessment']
        }
    
    def process_uploaded_files(self, uploaded_files) -> List[Dict[str, Any]]:
        """
        Process uploaded patient data files and return standardized data structure
        """
        all_data = []
        
        for uploaded_file in uploaded_files:
            try:
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension == 'csv':
                    data = self._process_csv_file(uploaded_file)
                elif file_extension == 'json':
                    data = self._process_json_file(uploaded_file)
                elif file_extension == 'txt':
                    data = self._process_text_file(uploaded_file)
                elif file_extension == 'pdf':
                    data = self._process_pdf_file(uploaded_file)
                else:
                    st.warning(f"Unsupported file format: {file_extension}")
                    continue
                
                if data:
                    all_data.extend(data)
                    
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
                continue
        
        # Standardize and clean data
        standardized_data = self._standardize_data(all_data)
        return standardized_data
    
    def _process_csv_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """
        Process CSV files containing patient data
        """
        try:
            # Read CSV data
            content = uploaded_file.getvalue().decode('utf-8')
            df = pd.read_csv(io.StringIO(content))
            
            # Convert to list of dictionaries
            data = df.to_dict('records')
            
            # Clean and process each record
            processed_data = []
            for record in data:
                # Remove NaN values and empty strings
                cleaned_record = {k: v for k, v in record.items() 
                                if pd.notna(v) and str(v).strip() != ''}
                if cleaned_record:
                    processed_data.append(cleaned_record)
            
            return processed_data
            
        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")
            return []
    
    def _process_json_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """
        Process JSON files containing patient data
        """
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            json_data = json.loads(content)
            
            # Handle different JSON structures
            if isinstance(json_data, list):
                return json_data
            elif isinstance(json_data, dict):
                # If single record, wrap in list
                if self._is_patient_record(json_data):
                    return [json_data]
                # If contains patient records under a key
                for key, value in json_data.items():
                    if isinstance(value, list) and value:
                        return value
                # Single nested record
                return [json_data]
            else:
                st.warning("Unexpected JSON structure")
                return []
                
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Error processing JSON file: {str(e)}")
            return []
    
    def _process_text_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """
        Process text files containing clinical notes or patient data
        """
        try:
            content = uploaded_file.getvalue().decode('utf-8')
            
            # Try to parse as structured text or clinical notes
            records = []
            
            # Check if it's a structured format (key-value pairs)
            if ':' in content and '\n' in content:
                record = {}
                for line in content.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        record[key.strip()] = value.strip()
                
                if record:
                    records.append(record)
            else:
                # Treat as clinical notes
                records.append({
                    'clinical_notes': content.strip(),
                    'data_type': 'clinical_text'
                })
            
            return records
            
        except Exception as e:
            st.error(f"Error processing text file: {str(e)}")
            return []
    
    def _process_pdf_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """
        Process PDF files containing medical reports or patient data
        """
        try:
            # Read PDF content
            pdf_content = ""
            
            # First try with pdfplumber for better text extraction
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            pdf_content += page_text + "\n"
            except Exception:
                # Fallback to PyPDF2 if pdfplumber fails
                uploaded_file.seek(0)  # Reset file stream position
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_content += page_text + "\n"
            
            if not pdf_content.strip():
                st.warning("No text content could be extracted from the PDF file")
                return []
            
            # Process extracted text similar to text files
            records = []
            
            # Try to extract structured data from the PDF text
            structured_data = self._extract_structured_data_from_text(pdf_content)
            
            if structured_data:
                records.append(structured_data)
            else:
                # Treat as clinical document
                records.append({
                    'clinical_notes': pdf_content.strip(),
                    'data_type': 'pdf_clinical_document',
                    'document_source': 'pdf_extraction'
                })
            
            return records
            
        except Exception as e:
            st.error(f"Error processing PDF file: {str(e)}")
            return []
    
    def _extract_structured_data_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract structured medical data from PDF text content
        """
        structured_data = {}
        text_lower = text.lower()
        
        # Extract basic demographics
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Map common medical fields
                if any(keyword in key for keyword in ['age', 'years old']):
                    structured_data['age'] = value
                elif any(keyword in key for keyword in ['gender', 'sex']):
                    structured_data['gender'] = value
                elif any(keyword in key for keyword in ['complaint', 'chief complaint']):
                    structured_data['chief_complaint'] = value
                elif any(keyword in key for keyword in ['history', 'medical history']):
                    structured_data['medical_history'] = value
                elif any(keyword in key for keyword in ['medication', 'meds']):
                    structured_data['medications'] = value
                elif any(keyword in key for keyword in ['vital', 'vitals']):
                    structured_data['vital_signs'] = value
                elif any(keyword in key for keyword in ['diagnosis', 'impression']):
                    structured_data['diagnosis'] = value
                elif any(keyword in key for keyword in ['symptom']):
                    structured_data['symptoms'] = value
        
        # Extract vital signs patterns
        import re
        
        # Blood pressure pattern
        bp_pattern = r'(\d{2,3}\/\d{2,3})'
        bp_match = re.search(bp_pattern, text)
        if bp_match:
            structured_data['blood_pressure'] = bp_match.group(1)
        
        # Temperature pattern
        temp_pattern = r'(\d{2,3}\.?\d*)\s*[°]?[CF]'
        temp_match = re.search(temp_pattern, text)
        if temp_match:
            structured_data['temperature'] = temp_match.group(1)
        
        # Heart rate pattern
        hr_pattern = r'(\d{2,3})\s*bpm|heart rate[:\s]*(\d{2,3})'
        hr_match = re.search(hr_pattern, text_lower)
        if hr_match:
            structured_data['heart_rate'] = hr_match.group(1) or hr_match.group(2)
        
        # Add full text as clinical notes regardless
        structured_data['clinical_notes'] = text
        structured_data['data_type'] = 'extracted_pdf_data'
        
        return structured_data if len(structured_data) > 2 else {}
    
    def _is_patient_record(self, data: Dict) -> bool:
        """
        Determine if a dictionary represents a patient record
        """
        medical_indicators = [
            'age', 'patient', 'symptoms', 'diagnosis', 'medical', 'clinical',
            'temperature', 'blood_pressure', 'heart_rate', 'medications',
            'history', 'complaint', 'examination', 'labs', 'vitals'
        ]
        
        data_keys = [str(k).lower() for k in data.keys()]
        return any(indicator in ' '.join(data_keys) for indicator in medical_indicators)
    
    def _standardize_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Standardize field names and data formats
        """
        standardized_data = []
        
        for record in data:
            standardized_record = {}
            
            # Map fields to standard names
            for standard_field, variations in self.medical_field_mappings.items():
                for original_key, value in record.items():
                    original_key_lower = str(original_key).lower()
                    
                    # Check if this key matches any variation
                    for variation in variations:
                        if variation in original_key_lower:
                            standardized_record[standard_field] = value
                            break
            
            # Keep unmapped fields as well
            for key, value in record.items():
                if key not in standardized_record.values():
                    standardized_record[str(key)] = value
            
            if standardized_record:
                standardized_data.append(standardized_record)
        
        return standardized_data
    
    def calculate_completeness(self, data: List[Dict[str, Any]]) -> float:
        """
        Calculate data completeness percentage
        """
        if not data:
            return 0.0
        
        total_fields = 0
        filled_fields = 0
        
        for record in data:
            total_fields += len(record)
            filled_fields += sum(1 for v in record.values() 
                               if v is not None and str(v).strip() != '')
        
        return (filled_fields / total_fields * 100) if total_fields > 0 else 0.0
    
    def assess_data_quality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess the quality and completeness of patient data
        """
        if not data:
            return {
                'completeness': 0.0,
                'consistency': 0.0,
                'critical_fields_present': 0,
                'data_quality_score': 0.0,
                'recommendations': ['No data available for analysis']
            }
        
        # Critical fields for medical diagnosis
        critical_fields = [
            'age', 'gender', 'symptoms', 'chief_complaint',
            'medical_history', 'vital_signs', 'clinical_notes'
        ]
        
        # Count critical fields present
        critical_present = 0
        all_fields = set()
        
        for record in data:
            record_fields = set(str(k).lower() for k in record.keys())
            all_fields.update(record_fields)
            
            for critical_field in critical_fields:
                if any(critical_field in field for field in record_fields):
                    critical_present += 1
                    break
        
        # Calculate metrics
        completeness = self.calculate_completeness(data)
        consistency = self._calculate_consistency(data)
        critical_field_percentage = (critical_present / len(critical_fields)) * 100
        
        # Overall quality score
        quality_score = (completeness * 0.4 + consistency * 0.3 + critical_field_percentage * 0.3)
        
        # Generate recommendations
        recommendations = []
        if completeness < 70:
            recommendations.append("Consider collecting additional patient information")
        if critical_present < len(critical_fields) * 0.5:
            recommendations.append("Key medical fields are missing - this may affect diagnostic accuracy")
        if consistency < 60:
            recommendations.append("Data format inconsistencies detected - standardization recommended")
        if quality_score > 80:
            recommendations.append("Data quality is excellent for AI analysis")
        
        return {
            'completeness': round(completeness, 1),
            'consistency': round(consistency, 1),
            'critical_fields_present': critical_present,
            'total_critical_fields': len(critical_fields),
            'data_quality_score': round(quality_score, 1),
            'recommendations': recommendations,
            'total_records': len(data),
            'unique_fields': len(all_fields)
        }
    
    def _calculate_consistency(self, data: List[Dict[str, Any]]) -> float:
        """
        Calculate data consistency across records
        """
        if len(data) <= 1:
            return 100.0
        
        # Compare field presence across records
        all_field_sets = [set(record.keys()) for record in data]
        
        # Calculate field overlap
        common_fields = set.intersection(*all_field_sets) if all_field_sets else set()
        all_fields = set.union(*all_field_sets) if all_field_sets else set()
        
        consistency = (len(common_fields) / len(all_fields) * 100) if all_fields else 0
        return consistency
    
    def extract_medical_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract medical entities from clinical text
        """
        # Simple keyword-based extraction (could be enhanced with NLP libraries)
        entities = {
            'symptoms': [],
            'medications': [],
            'conditions': [],
            'procedures': [],
            'vital_signs': []
        }
        
        text_lower = text.lower()
        
        # Symptom keywords
        symptom_keywords = ['pain', 'fever', 'nausea', 'vomiting', 'headache', 'fatigue', 
                           'shortness of breath', 'chest pain', 'abdominal pain']
        
        # Medication patterns
        medication_patterns = ['mg', 'tablet', 'capsule', 'injection', 'dose']
        
        # Extract entities based on patterns
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            
            # Look for symptoms
            for symptom in symptom_keywords:
                if symptom in sentence_lower:
                    entities['symptoms'].append(sentence.strip())
                    break
            
            # Look for medications
            for pattern in medication_patterns:
                if pattern in sentence_lower:
                    entities['medications'].append(sentence.strip())
                    break
        
        return entities
