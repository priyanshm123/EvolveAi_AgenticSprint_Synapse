import pandas as pd
import json
import pdfplumber
import streamlit as st
from typing import List, Dict, Any, Union
from io import StringIO
import logging

class DataProcessor:
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'txt', 'pdf']
        
        # Common medical field mappings
        self.field_mappings = {
            'patient_id': ['id', 'patient_id', 'patientid', 'patient_number', 'mrn'],
            'patient_name': ['name', 'patient_name', 'patientname', 'full_name', 'fullname'],
            'age': ['age', 'patient_age', 'age_years'],
            'gender': ['gender', 'sex', 'patient_gender', 'patient_sex'],
            'date_of_birth': ['dob', 'date_of_birth', 'birth_date', 'birthdate'],
            'chief_complaint': ['chief_complaint', 'cc', 'complaint', 'presenting_complaint'],
            'symptoms': ['symptoms', 'symptom', 'clinical_symptoms', 'presenting_symptoms'],
            'temperature': ['temperature', 'temp', 'body_temp', 'body_temperature'],
            'blood_pressure': ['blood_pressure', 'bp', 'systolic_diastolic', 'pressure'],
            'heart_rate': ['heart_rate', 'hr', 'pulse', 'pulse_rate', 'bpm'],
            'respiratory_rate': ['respiratory_rate', 'rr', 'breathing_rate', 'resp_rate'],
            'oxygen_saturation': ['oxygen_saturation', 'o2_sat', 'spo2', 'oxygen_sat'],
            'medical_history': ['medical_history', 'pmh', 'past_medical_history', 'history'],
            'medications': ['medications', 'meds', 'current_medications', 'prescriptions'],
            'allergies': ['allergies', 'drug_allergies', 'medication_allergies', 'allergy']
        }

    def process_file(self, uploaded_file) -> List[Dict[str, Any]]:
        """
        Process uploaded file and return structured patient data
        """
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            if file_extension == 'csv':
                return self._process_csv(uploaded_file)
            elif file_extension == 'json':
                return self._process_json(uploaded_file)
            elif file_extension == 'txt':
                return self._process_text(uploaded_file)
            elif file_extension == 'pdf':
                return self._process_pdf(uploaded_file)
            else:
                return []
            
        except Exception as e:
            logging.error(f"Error processing file {uploaded_file.name}: {e}")
            raise Exception(f"Failed to process {uploaded_file.name}: {str(e)}")

    def _process_csv(self, uploaded_file) -> List[Dict[str, Any]]:
        """Process CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            
            # Clean and standardize column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # Convert to list of dictionaries
            records = df.to_dict('records')
            
            # Standardize field names
            standardized_records = []
            for record in records:
                standardized_record = self._standardize_field_names(record)
                standardized_records.append(standardized_record)
            
            return standardized_records
            
        except Exception as e:
            raise Exception(f"Error processing CSV file: {str(e)}")

    def _process_json(self, uploaded_file) -> List[Dict[str, Any]]:
        """Process JSON file"""
        try:
            # Read JSON file
            json_data = json.load(uploaded_file)
            
            # Handle different JSON structures
            if isinstance(json_data, list):
                records = json_data
            elif isinstance(json_data, dict):
                # If single patient record
                if 'patients' in json_data:
                    records = json_data['patients']
                elif 'data' in json_data:
                    records = json_data['data']
                else:
                    records = [json_data]
            else:
                raise ValueError("Invalid JSON structure")
            
            # Standardize field names
            standardized_records = []
            for record in records:
                if isinstance(record, dict):
                    standardized_record = self._standardize_field_names(record)
                    standardized_records.append(standardized_record)
            
            return standardized_records
            
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing JSON file: {str(e)}")

    def _process_text(self, uploaded_file) -> List[Dict[str, Any]]:
        """Process text file"""
        try:
            # Read text content
            content = str(uploaded_file.read(), "utf-8")
            
            # Parse structured text (assuming key: value format)
            record = {}
            lines = content.split('\n')
            
            current_section = 'general'
            sections = {
                'general': record,
                'demographics': {},
                'vitals': {},
                'symptoms': {},
                'history': {},
                'medications': {},
                'labs': {}
            }
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                line_lower = line.lower()
                if any(section in line_lower for section in ['demographic', 'patient info']):
                    current_section = 'demographics'
                    continue
                elif any(section in line_lower for section in ['vital', 'signs']):
                    current_section = 'vitals'
                    continue
                elif any(section in line_lower for section in ['symptom', 'complaint']):
                    current_section = 'symptoms'
                    continue
                elif any(section in line_lower for section in ['history', 'medical history']):
                    current_section = 'history'
                    continue
                elif any(section in line_lower for section in ['medication', 'drugs']):
                    current_section = 'medications'
                    continue
                elif any(section in line_lower for section in ['lab', 'laboratory']):
                    current_section = 'labs'
                    continue
                
                # Parse key-value pairs
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if value:
                        sections[current_section][key] = value
                elif line and current_section in ['symptoms', 'history']:
                    # Handle list-style entries
                    key = f"{current_section}_entry_{len(sections[current_section])}"
                    sections[current_section][key] = line
            
            # Merge all sections
            for section_name, section_data in sections.items():
                if section_name != 'general':
                    record.update(section_data)
            
            # Standardize field names
            standardized_record = self._standardize_field_names(record)
            
            return [standardized_record] if standardized_record else []
            
        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")

    def _process_pdf(self, uploaded_file) -> List[Dict[str, Any]]:
        """Process PDF file"""
        try:
            # Extract text from PDF
            text_content = ""
            
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            if not text_content.strip():
                raise Exception("No text content found in PDF")
            
            # Parse extracted text
            record = self._parse_medical_text(text_content)
            
            # Standardize field names
            standardized_record = self._standardize_field_names(record)
            
            return [standardized_record] if standardized_record else []
            
        except Exception as e:
            raise Exception(f"Error processing PDF file: {str(e)}")

    def _parse_medical_text(self, text: str) -> Dict[str, Any]:
        """Parse unstructured medical text"""
        record = {}
        lines = text.split('\n')
        
        # Keywords for different sections
        keywords = {
            'patient_name': ['patient name', 'name:', 'patient:', 'pt name'],
            'age': ['age:', 'age ', 'years old', 'y/o'],
            'gender': ['gender:', 'sex:', 'male', 'female'],
            'chief_complaint': ['chief complaint', 'cc:', 'presenting complaint', 'reason for visit'],
            'symptoms': ['symptoms:', 'complaints:', 'reports:', 'presents with'],
            'vital_signs': ['vital signs', 'vitals:', 'bp:', 'hr:', 'temp:', 'temperature:'],
            'medical_history': ['history:', 'pmh:', 'past medical history', 'medical history'],
            'medications': ['medications:', 'meds:', 'current medications', 'prescriptions:'],
            'assessment': ['assessment:', 'impression:', 'diagnosis:', 'plan:'],
            'physical_exam': ['physical exam', 'examination:', 'pe:']
        }
        
        current_section = None
        section_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts a new section
            line_lower = line.lower()
            new_section = None
            
            for section, section_keywords in keywords.items():
                if any(keyword in line_lower for keyword in section_keywords):
                    new_section = section
                    break
            
            if new_section:
                # Save previous section content
                if current_section and section_content:
                    record[current_section] = ' '.join(section_content).strip()
                
                # Start new section
                current_section = new_section
                section_content = []
                
                # Extract content from the same line if available
                for keyword in keywords[new_section]:
                    if keyword in line_lower:
                        content_start = line_lower.find(keyword) + len(keyword)
                        remaining_content = line[content_start:].strip().lstrip(':').strip()
                        if remaining_content:
                            section_content.append(remaining_content)
                        break
            else:
                # Continue current section
                if current_section:
                    section_content.append(line)
        
        # Save final section
        if current_section and section_content:
            record[current_section] = ' '.join(section_content).strip()
        
        return record

    def _standardize_field_names(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Standardize field names using predefined mappings"""
        standardized = {}
        
        for standard_field, possible_names in self.field_mappings.items():
            for key, value in record.items():
                key_lower = str(key).lower().strip()
                
                if key_lower in possible_names or any(name in key_lower for name in possible_names):
                    standardized[standard_field] = value
                    break
        
        # Add unmapped fields as-is
        for key, value in record.items():
            key_lower = str(key).lower().strip()
            
            # Check if field was already mapped
            mapped = False
            for possible_names in self.field_mappings.values():
                if key_lower in possible_names or any(name in key_lower for name in possible_names):
                    mapped = True
                    break
            
            if not mapped and key not in standardized:
                # Clean the key name
                clean_key = key_lower.replace(' ', '_').replace('-', '_')
                standardized[clean_key] = value
        
        return standardized

    def validate_patient_data(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate patient data quality and completeness"""
        validation_results = {
            'total_records': len(records),
            'valid_records': 0,
            'warnings': [],
            'errors': [],
            'completeness_score': 0.0,
            'data_quality_issues': []
        }
        
        if not records:
            validation_results['errors'].append("No patient records found")
            return validation_results
        
        essential_fields = ['age', 'gender', 'chief_complaint', 'symptoms']
        important_fields = ['patient_name', 'medical_history', 'medications', 'vital_signs']
        
        valid_count = 0
        total_completeness = 0
        
        for i, record in enumerate(records):
            record_issues = []
            completeness_score = 0
            total_fields = len(essential_fields) + len(important_fields)
            
            # Check essential fields
            missing_essential = []
            for field in essential_fields:
                if field in record and record[field] and str(record[field]).strip():
                    completeness_score += 2  # Essential fields worth more
                else:
                    missing_essential.append(field)
            
            # Check important fields
            missing_important = []
            for field in important_fields:
                if field in record and record[field] and str(record[field]).strip():
                    completeness_score += 1
                else:
                    missing_important.append(field)
            
            # Calculate completeness percentage
            max_score = len(essential_fields) * 2 + len(important_fields) * 1
            record_completeness = (completeness_score / max_score) * 100 if max_score > 0 else 0
            total_completeness += record_completeness
            
            # Record validation
            if not missing_essential:
                valid_count += 1
            else:
                record_issues.append(f"Missing essential fields: {', '.join(missing_essential)}")
            
            if missing_important:
                record_issues.append(f"Missing important fields: {', '.join(missing_important)}")
            
            # Data type validation
            if 'age' in record:
                try:
                    age_value = float(record['age'])
                    if age_value < 0 or age_value > 150:
                        record_issues.append("Age value seems unrealistic")
                except (ValueError, TypeError):
                    record_issues.append("Age is not a valid number")
            
            if record_issues:
                validation_results['data_quality_issues'].append({
                    'record_index': i,
                    'issues': record_issues,
                    'completeness': f"{record_completeness:.1f}%"
                })
        
        validation_results['valid_records'] = valid_count
        validation_results['completeness_score'] = total_completeness / len(records) if records else 0
        
        # Generate warnings and recommendations
        if valid_count < len(records):
            validation_results['warnings'].append(f"{len(records) - valid_count} records have missing essential fields")
        
        if validation_results['completeness_score'] < 70:
            validation_results['warnings'].append("Data completeness is below 70% - consider adding more patient information")
        
        return validation_results

    def get_data_summary(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics of the patient data"""
        if not records:
            return {"error": "No records to summarize"}
        
        summary = {
            'total_records': len(records),
            'fields_present': set(),
            'demographics': {},
            'data_types': {},
            'value_ranges': {},
            'common_values': {}
        }
        
        # Collect all field names and analyze data
        for record in records:
            for field, value in record.items():
                summary['fields_present'].add(field)
                
                # Analyze data types
                if field not in summary['data_types']:
                    summary['data_types'][field] = type(value).__name__
                
                # Collect values for analysis
                if field not in summary['common_values']:
                    summary['common_values'][field] = []
                
                if value is not None and str(value).strip():
                    summary['common_values'][field].append(str(value))
        
        # Convert set to list for JSON serialization
        summary['fields_present'] = list(summary['fields_present'])
        
        # Analyze demographics
        if 'age' in summary['fields_present']:
            ages = []
            for record in records:
                if 'age' in record and record['age']:
                    try:
                        ages.append(float(record['age']))
                    except (ValueError, TypeError):
                        pass
            
            if ages:
                summary['demographics']['age_range'] = {
                    'min': min(ages),
                    'max': max(ages),
                    'mean': sum(ages) / len(ages)
                }
        
        if 'gender' in summary['fields_present']:
            genders = [record.get('gender', '').lower() for record in records if record.get('gender')]
            from collections import Counter
            gender_counts = Counter(genders)
            summary['demographics']['gender_distribution'] = dict(gender_counts)
        
        return summary
