# AI Medical Diagnostic Assistant

## Overview

The AI Medical Diagnostic Assistant is a comprehensive Streamlit-based web application that leverages Google's Gemini AI to analyze patient medical data and provide evidence-based diagnostic insights. The system processes various medical data formats (CSV, JSON, TXT, PDF) and delivers structured diagnostic recommendations with confidence scoring, risk stratification, and clinical decision support. It features a Netflix-inspired dark theme UI with secure user authentication and comprehensive patient data management capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application with custom Netflix-inspired CSS styling
- **Theme**: Dark theme with custom CSS variables for consistent branding (Netflix red, dark grays, medical blues)
- **Layout**: Wide layout with expandable sidebar navigation
- **Visualization**: Plotly integration for interactive medical charts and diagnostic visualizations
- **UI Components**: Modular component system with specialized medical interface elements including patient cards, alert systems (urgent, warning, success), and dashboard grids

### Backend Architecture
- **Core Components**: Modular Python architecture with six main modules:
  - `DiagnosticEngine`: AI-powered medical analysis using Google Gemini 1.5 Flash
  - `DataProcessor`: Medical data ingestion, parsing, and field mapping
  - `UIComponents`: Reusable interface components and visualization tools
  - `AuthManager`: User authentication and session management
  - `UserDashboard`: Patient history and diagnostic record management
  - `DatabaseManager`: SQLite database operations and user management

### Authentication System
- **User Management**: Complete user registration, login, and session management
- **Password Security**: bcrypt hashing for secure password storage
- **Session Handling**: Token-based session management with expiration
- **Role-based Access**: User role system with configurable permissions

### Data Processing Pipeline
- **Multi-format Support**: CSV, JSON, TXT, and PDF file processing with pdfplumber integration
- **Smart Field Mapping**: Automatic detection and standardization of medical fields including demographics, vital signs, symptoms, medical history, medications, allergies, and clinical notes
- **Data Standardization**: Converts disparate medical data formats into unified patient data structures for AI analysis

### Diagnostic Engine
- **AI Model**: Google Gemini 1.5 Flash with structured JSON response generation
- **Temperature Settings**: Low temperature (0.2) for consistent, reliable medical outputs
- **Prompt Engineering**: Comprehensive medical system prompts with ICD-10 code support
- **Output Structure**: Structured responses including differential diagnoses, confidence scores, risk levels, red flag conditions, clinical reasoning, and next steps
- **Configurable Analysis**: Adjustable confidence thresholds and diagnosis limits

### Database Architecture
- **Database**: SQLite for local data persistence
- **Schema**: Four main tables - users, user_sessions, patient_records, and diagnostic_results
- **Data Relationships**: Foreign key relationships between users, sessions, and patient records
- **Session Management**: Secure session token system with expiration handling

## External Dependencies

### AI Services
- **Google Generative AI**: Primary AI service using Gemini 1.5 Flash model for medical diagnostic analysis
- **API Configuration**: Requires GEMINI_API_KEY environment variable

### Python Libraries
- **Streamlit**: Web application framework (v1.49.1+)
- **Pandas**: Data manipulation and medical dataset analysis (v2.3.2+)
- **Plotly**: Interactive medical data visualization (v6.3.0+)
- **bcrypt**: Password hashing and authentication security (v4.3.0+)
- **pdfplumber**: PDF medical document processing (v0.11.7+)
- **python-dotenv**: Environment variable management

### File Processing
- **PDF Processing**: pdfplumber for medical document text extraction
- **Data Formats**: Native support for CSV, JSON, and text file medical records

### Environment Configuration
- **Environment Variables**: GEMINI_API_KEY for AI service authentication, SESSION_SECRET for secure sessions
- **Database**: SQLite local database with automatic initialization