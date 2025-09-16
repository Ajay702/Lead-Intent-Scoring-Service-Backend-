# Lead Intent Scoring Service

A comprehensive Flask-based REST API service that scores B2B lead intent using a dual-layer approach: rule-based scoring and AI-powered classification with Google's Gemini API. The system processes CSV lead data, applies intelligent scoring algorithms, and provides results via JSON and CSV exports.

## 🚀 Project Setup

### Prerequisites
- Git
- Docker (recommended) or Python 3.11+
- Google Gemini API key (optional - fallback available)

### Clone Repository & Setup

```bash
# Clone the repository
git clone https://github.com/Ajay702/Lead-Intent-Scoring-Service-Backend-.git
cd lead-intent-scoring-service

# Copy environment configuration
cp .env.example .env

# Edit .env file and add your Gemini API key (optional)
# GEMINI_API_KEY=your_api_key_here
```

### Option 1: Docker Setup (Recommended)

```bash
# Build the Docker image
docker build -t lead-intent-scoring .

# Create instance directory for database persistence
mkdir instance

# Run the container
docker run -d \
  -p 5000:8000 \
  -v "${PWD}/instance:/app/instance" \
  --env-file .env \
  --name lead-scoring \
  lead-intent-scoring

# Verify the service is running
curl http://localhost:5000/health
```

### Option 2: Local Python Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set Flask app
export FLASK_APP=app  # On Windows: set FLASK_APP=app

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Run the application
flask run --host=0.0.0.0 --port=5000
```

## 📡 API Usage Examples

### Base URL
```
http://localhost:5000
```

### 1. Health Check
**GET /health**
```bash
curl -X GET http://localhost:5000/health
```
**Response:**
```json
{
  "status": "ok"
}
```

### 2. Create Product Offer
**POST /offer**
```bash
curl -X POST http://localhost:5000/offer \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Enterprise CRM Platform",
    "value_props": "Advanced analytics, automation, seamless integrations",
    "ideal_use_cases": "Large enterprises, sales teams 50+, complex sales cycles"
  }'
```
**Response:**
```json
{
  "id": 1
}
```

### 3. Upload Leads CSV
**POST /leads/upload**

First, create a CSV file with the required format:
```csv
name,role,company,industry,location,linkedin_bio
John Smith,CEO,TechCorp,saas,San Francisco,Scaling SaaS platforms for Fortune 500
Sarah Johnson,VP Marketing,DataTech,technology,Seattle,Growth marketing leader
Mike Chen,HR Manager,RetailCorp,retail,Chicago,Human resources professional
```

```bash
curl -X POST http://localhost:5000/leads/upload \
  -F "file=@leads.csv"
```
**Response:**
```json
{
  "inserted": 3
}
```

### 4. Score All Leads
**POST /score**
```bash
curl -X POST http://localhost:5000/score \
  -H "Content-Type: application/json" \
  -d '{}'
```
**Response:**
```json
{
  "processed": 3
}
```

### 5. Get Results (JSON)
**GET /results**
```bash
curl -X GET http://localhost:5000/results
```
**Response:**
```json
[
  {
    "lead_id": 1,
    "name": "John Smith",
    "company": "TechCorp",
    "role": "CEO",
    "industry": "saas",
    "score": 95,
    "intent": "High",
    "reasoning": "High intent: CEO role at SaaS company strongly aligns with enterprise CRM platform target market."
  },
  {
    "lead_id": 2,
    "name": "Sarah Johnson",
    "company": "DataTech", 
    "role": "VP Marketing",
    "industry": "technology",
    "score": 67,
    "intent": "Medium",
    "reasoning": "Medium intent: VP Marketing at tech company shows interest but not primary decision maker."
  },
  {
    "lead_id": 3,
    "name": "Mike Chen",
    "company": "RetailCorp",
    "role": "HR Manager",
    "industry": "retail",
    "score": 25,
    "intent": "Low",
    "reasoning": "Low intent: HR role at retail company has limited alignment with CRM platform needs."
  }
]
```

### 6. Export Results (CSV)
**GET /results/export**
```bash
curl -X GET http://localhost:5000/results/export \
  -H "Accept: text/csv" \
  -o "lead_scores.csv"
```
**Response:** Downloads CSV file with columns:
```
lead_id,name,company,role,industry,score,intent,reasoning
```

## 🧠 Rule Logic & AI Prompts

### Scoring System Architecture

The system uses a **dual-layer scoring approach** with a maximum of 100 points:

#### Layer 1: Rule-Based Scoring (50 points maximum)

**1. Role Relevance (20 points max)**
```python
# Decision Makers: +20 points
decision_makers = ["ceo", "founder", "owner", "cto", "cfo", "coo", "chief"]

# Senior Roles: +15 points
senior_roles = ["vp", "vice president", "head", "director"]

# Influencers: +10 points  
influencers = ["manager", "lead", "senior", "principal", "architect"]

# Others: 0 points
```

**2. Industry Match (20 points max)**
```python
# Target Industries: +20 points
target_industries = ["saas", "software", "technology", "tech"]

# Adjacent Industries: +12 points
adjacent_industries = ["consulting", "services", "fintech", "healthcare tech", "edtech"]

# Neutral Industries: +5 points
neutral_industries = ["finance", "healthcare", "education", "manufacturing"]

# Other Industries: 0 points
```

**3. Data Completeness (10 points max)**
```python
# All fields present: +10 points
required_fields = ["name", "role", "company", "industry", "linkedin_bio"]
# Missing fields reduce score proportionally
```

#### Layer 2: AI-Powered Scoring (50 points maximum)

**Gemini AI Prompt Template:**
```
You are an expert B2B sales analyst.
Given the following Product/Offer and Prospect details, classify the lead intent as one of: High, Medium, Low, and explain in 1–2 sentences.

Offer:
- Name: {offer[name]}
- Value Props: {offer[value_props]}
- Ideal Use Cases: {offer[ideal_use_cases]}

Prospect:
- Name: {lead[name]}
- Role: {lead[role]}
- Company: {lead[company]}
- Industry: {lead[industry]}
- Location: {lead[location]}
- Bio: {lead[linkedin_bio]}

Respond with a concise sentence that includes the intent label (High/Medium/Low) and justification.
```

**AI Score Mapping:**
- **High Intent**: 45-50 points - Strong purchase readiness indicators
- **Medium Intent**: 15-25 points - Some interest, needs nurturing  
- **Low Intent**: 5 points - Limited current opportunity

**Fallback Heuristics** (when AI unavailable):
- **Decision Maker + Target Industry**: High intent (45 points)
- **Decision Maker OR (Senior + Target Industry)**: Medium intent (25 points)
- **Influencer OR Adjacent Industry**: Medium intent (15 points)
- **Others**: Low intent (5 points)
- Ensures 100% service availability during API outages

### Final Score Calculation
```
Total Score = Rule Layer Points (0-50) + AI Layer Points (0-50)

Intent Classification:
- High: 80-100 points
- Medium: 50-79 points  
- Low: 0-49 points
```

## 📁 File Structure & Functionality

### Core Application Files

#### `app/__init__.py` - Flask Application Factory
- **Purpose**: Creates and configures Flask application instance
- **Key Functions**: 
  - `create_app()`: Application factory pattern
  - Database initialization with worker-safe locking
  - Blueprint registration for routes
  - SQLite URI normalization for Docker compatibility

#### `app/config.py` - Configuration Management
- **Purpose**: Centralized configuration for different environments
- **Key Features**:
  - Environment variable loading
  - Database URI configuration
  - Gemini API key management
  - Flask secret key generation

#### `app/models.py` - Database Models
- **Purpose**: SQLAlchemy ORM models for data persistence
- **Models**:
  - `Offer`: Product/service offerings (name, value_props, ideal_use_cases)
  - `Lead`: Prospect information (name, role, company, industry, location, bio)
  - `Result`: Scoring results (lead_id, score, intent, reasoning)

#### `app/routes.py` - API Endpoints
- **Purpose**: REST API endpoint definitions
- **Routes**:
  - `GET /health`: Service health check
  - `POST /offer`: Create product offer
  - `POST /leads/upload`: CSV lead upload
  - `POST /score`: Execute scoring pipeline
  - `GET /results`: Retrieve JSON results
  - `GET /results/export`: Download CSV export

#### `app/storage.py` - Database Operations
- **Purpose**: CRUD operations and database helpers
- **Key Functions**:
  - `get_or_create_offer()`: Offer management
  - `insert_leads()`: Bulk lead insertion
  - `get_unscored_leads()`: Query leads needing scoring
  - `save_result()`: Store scoring results

### Business Logic Layer

#### `app/services/scoring.py` - Main Scoring Pipeline
- **Purpose**: Orchestrates the complete scoring process
- **Key Functions**:
  - `run_scoring()`: Main pipeline coordinator
  - Integrates rule engine and AI layer
  - Batch processing of leads
  - Result persistence

#### `app/services/classification_prompt.txt` - AI Prompt Template
- **Purpose**: Structured prompt for Gemini AI classification
- **Content**: Expert B2B sales analyst persona with offer/prospect analysis framework

### Utility Modules

#### `app/utils/rule_layer.py` - Rule-Based Scoring Engine
- **Purpose**: Implements deterministic scoring rules
- **Key Functions**:
  - `score_lead()`: Main rule evaluation
  - `_score_role()`: Role relevance scoring
  - `_score_industry()`: Industry match scoring
  - `_score_completeness()`: Data quality scoring

#### `app/utils/ai_layer.py` - AI Integration
- **Purpose**: Google Gemini API integration with fallback
- **Key Functions**:
  - `call_gemini()`: API request handling
  - `_stub_ai()`: Fallback heuristics
  - Timeout and error handling
  - Response parsing and validation

#### `app/utils/csv_parser.py` - CSV Processing
- **Purpose**: Handles CSV file upload and parsing
- **Key Functions**:
  - `parse_leads_csv()`: CSV validation and parsing
  - Data cleaning and normalization
  - Error handling for malformed data

#### `app/utils/exporter.py` - Data Export
- **Purpose**: Exports results in various formats
- **Key Functions**:
  - `export_results_csv()`: CSV export with proper headers
  - Data formatting and serialization

### Testing & Configuration

#### `app/tests/test_api.py` - API Integration Tests
- **Purpose**: End-to-end API testing
- **Coverage**: All 6 endpoints with various scenarios
- **Validates**: Request/response formats, error handling, data flow

#### `app/tests/test_rules.py` - Unit Tests
- **Purpose**: Rule engine validation
- **Coverage**: Role scoring, industry matching, data completeness
- **Validates**: Scoring logic accuracy and edge cases

#### `pytest.ini` - Test Configuration
- **Purpose**: Pytest configuration and test discovery
- **Settings**: Test paths, markers, output formatting

### Infrastructure Files

#### `Dockerfile` - Container Configuration
- **Purpose**: Production-ready containerization
- **Features**:
  - Python 3.11 slim base image
  - Gunicorn WSGI server with single worker
  - Volume mounting for SQLite persistence
  - Port 8000 exposure

#### `requirements.txt` - Dependencies
- **Purpose**: Python package dependencies
- **Key Packages**:
  - Flask 3.0.3: Web framework
  - SQLAlchemy 3.1.1: ORM and database
  - pandas 2.2.2: CSV processing
  - requests 2.32.3: HTTP client for AI API
  - gunicorn 22.0.0: WSGI server

#### `.env.example` - Environment Template
- **Purpose**: Environment variable template
- **Variables**: Flask config, database URI, Gemini API key, server settings

#### `.gitignore` - Version Control
- **Purpose**: Excludes unwanted files from git
- **Excludes**: Cache files, environments, test data, sensitive files

### Database & Migrations

#### `instance/` - Database Storage
- **Purpose**: SQLite database file location
- **Contents**: `app.db` with persistent lead and scoring data
- **Docker**: Mounted as volume for data persistence

#### `migrations/` - Database Schema
- **Purpose**: Flask-Migrate database versioning
- **Contents**: Migration scripts for schema changes
- **Usage**: Database initialization and updates

---

## 🌐 Live Deployment

### Production Service URL
```
https://lead-intent-scoring-service-production.up.railway.app
```

### Quick Test
```bash
# Health check
curl https://lead-intent-scoring-service-production.up.railway.app/health

# Example API call
curl -X POST https://lead-intent-scoring-service-production.up.railway.app/offer \
  -H "Content-Type: application/json" \
  -d '{"name": "AI Platform", "value_props": "ML automation", "ideal_use_cases": "Tech companies"}'
```

### Score Distribution Examples
Based on real production data:

| Lead Profile | Role Score | Industry Score | Complete | AI Score | **Total** | Intent |
|-------------|------------|----------------|----------|----------|-----------|---------|
| **Founder, AI Startup** | 20 | 20 | 10 | 45 | **95-100** | High |
| **VP Engineering, FinTech** | 15 | 12 | 10 | 45 | **82-87** | High |
| **Director, Consulting** | 15 | 12 | 10 | 25 | **62-67** | Medium |
| **Account Manager, Software** | 10 | 20 | 10 | 25 | **60-65** | Medium |
| **Senior Developer, SaaS** | 10 | 20 | 10 | 5 | **40-45** | Low |
| **Product Manager, Healthcare** | 10 | 5 | 10 | 5 | **25-30** | Low |

**The Lead Intent Scoring Service provides a complete, production-ready solution for B2B lead qualification with intelligent scoring, robust fallback mechanisms, and comprehensive API access.**