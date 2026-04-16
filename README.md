[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Flask 2.2.3](https://img.shields.io/badge/flask-2.2.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-EC2-orange.svg)](https://aws.amazon.com/)
[![CodeQL](https://github.com/AnarkeyV/flask-portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/AnarkeyV/flask-portfolio/actions)

# 🚀 Khairul Rizal's DevOps Portfolio

[![CI/CD Pipeline](https://github.com/AnarkeyV/flask-portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/AnarkeyV/flask-portfolio/actions)
[![Security Scan](https://github.com/AnarkeyV/flask-portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/AnarkeyV/flask-portfolio/actions)
[![Health Status](https://img.shields.io/website?url=https%3A%2F%2Fkhairulrizal.qzz.io%2Fhealth&label=Production%20Health)](https://khairulrizal.qzz.io/health)

## 📋 Table of Contents

- [Live Sites](#live-sites)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Security Features](#security-features)
- [Observability](#observability)
- [CI/CD Pipeline](#cicd-pipeline)
- [Tech Stack](#tech-stack)
- [DevOps Skills](#devops-skills-demonstrated)
- [Local Development](#local-development)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Contact](#contact)

---

## 🌐 Live Sites

| Environment | URL | Status |
|-------------|-----|--------|
| **🚀 Production (AWS)** | [khairulrizal.qzz.io](https://khairulrizal.qzz.io) | [![Health](https://img.shields.io/website?url=https%3A%2F%2Fkhairulrizal.qzz.io%2Fhealth&label=online)](https://khairulrizal.qzz.io/health) |
| **🧪 Staging (PythonAnywhere)** | [khairulrizal.pythonanywhere.com](https://khairulrizal.pythonanywhere.com) | [![Health](https://img.shields.io/website?url=https%3A%2F%2Fkhairulrizal.pythonanywhere.com%2Fhealth&label=online)](https://khairulrizal.pythonanywhere.com/health) |

> **Note**: The staging environment serves as a testing ground before changes reach production. Both environments are automatically deployed via GitHub Actions.

---

## 📖 Project Overview

A **production-grade full-stack Flask web application** demonstrating DevOps best practices including:

- ✅ CI/CD automation with GitHub Actions
- ✅ Security hardening (headers, rate limiting, vulnerability scanning)
- ✅ Observability (health checks, audit logging)
- ✅ Multi-environment deployment (staging/production)
- ✅ Containerization with Docker

This project was built as part of my **DevOps/Cloud Support Engineering training** to showcase real-world infrastructure and security skills.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| **🔐 User Authentication** | Secure login/logout with scrypt password hashing |
| **💬 Comments System** | Authenticated users can post and view comments |
| **📧 Contact Form** | EmailJS integration with honeypot bot protection |
| **📊 Admin Features** | Login attempt auditing and real-time monitoring |

---

## 🏗️ Architecture

┌─────────────┐ ┌─────────────┐ ┌─────────────────┐
│ Local │────▶│ GitHub │────▶│ Security │
│ Dev │ │ Actions │ │ Scanning │
│ (Docker) │ │ CI/CD │ │ • Bandit │
└─────────────┘ └─────────────┘ │ • Safety │
│ │ • Trivy │
│ └─────────────────┘
│ │
┌─────────────────────┼────────────────────┼─────────────────────┐
│ │ │ │
▼ ▼ ▼ ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Staging │ │ Production │ │ Monitoring │ │ Database │
│ PythonAny │ │ AWS EC2 │ │ • /health │ │ SQLite │
│ where │ │ Ubuntu │ │ • Audit Logs │ │ SQLAlchemy │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘


---

## 🔒 Security Features

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| **Security Headers** | Flask-Talisman (CSP, X-Frame-Options, X-XSS-Protection) | Prevent XSS, clickjacking, and MIME attacks |
| **Rate Limiting** | 5 attempts/minute on login, 10/minute on comments | Prevent brute force and DoS attacks |
| **Password Hashing** | scrypt algorithm with per-user salts | Secure credential storage |
| **Login Audit** | All attempts logged with IP and user agent | Detect suspicious activity |
| **Bot Protection** | Honeypot field in contact form | Filter automated spam |
| **CI/CD Scanning** | Bandit, Safety, Trivy in pipeline | Catch vulnerabilities early |

---

## 📊 Observability

| Component | Purpose | Endpoint/Table |
|-----------|---------|----------------|
| **Health Check** | Monitor application and database status | `GET /health` |
| **Login Audit** | Track all authentication attempts | `login_attempts` table |
| **Application Logging** | Structured logs for debugging | Console + CloudWatch (AWS) |

### Health Check Response Example

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-04-16T10:30:00.123456",
  "version": "1.0.0"
}

🔄 CI/CD Pipeline
---------------------------------------------
Pipeline Stages

1. Security Scan (Bandit, Safety, Trivy)
   ↓
2. Test (Flask app initialization)
   ↓
3. Deploy to Staging (PythonAnywhere)
   ↓
4. Deploy to Production (AWS EC2)


GitHub Secrets Required
---------------------------------------------
Secret	            Purpose
--------------------------------------------------------
PA_API_TOKEN	    PythonAnywhere API authentication
PA_USERNAME	        PythonAnywhere account username
EC2_SSH_KEY	        AWS EC2 private key for SSH access
EC2_HOST	        EC2 instance hostname or IP


Workflow Status
https://github.com/AnarkeyV/flask-portfolio/actions/workflows/deploy.yml/badge.svg


🛠️ Tech Stack
---------------------------------------------
Category	        Technologies
Backend	            Flask 2.2.3, Python 3.13
Database	        SQLite, SQLAlchemy ORM, Alembic
Security	        Flask-Talisman, Flask-Limiter, scrypt
Authentication	    Flask-Login, Werkzeug
Deployment	        GitHub Actions, Docker, AWS EC2, PythonAnywhere
Monitoring	        Custom health endpoint, audit logging
Domain	            Cloudflare CDN, Zoho Mail
Development	        VS Code, Docker Desktop, VMWare Fusion


📈 DevOps Skills Demonstrated
---------------------------------------------
Skill Area	                    Technologies & Practices
Infrastructure as Code	        Docker, docker-compose, Dockerfile
CI/CD Pipeline Design	        GitHub Actions, automated testing, multi-stage deployments
Multi-environment Deployment	Staging (PythonAnywhere) → Production (AWS EC2)
Security Hardening	            Security headers, rate limiting, vulnerability scanning
Observability	                Health checks, audit logging, structured logging
Container Orchestration	        Docker, Docker Compose
Cloud Deployment	            AWS EC2, PythonAnywhere, Cloudflare
Version Control	                Git, GitHub, branch management


🐳 Local Development
---------------------------------------------
Prerequisites
Python 3.13+
Docker (optional)
Git


Setup Instructions
---------------------------------------------
# 1. Clone the repository
git clone https://github.com/AnarkeyV/flask-portfolio.git
cd flask-portfolio

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
flask run

# 5. Open your browser and navigate to
# http://localhost:5000


Docker Development
---------------------------------------------
# Build the Docker image
docker build -t flask-portfolio .

# Run the container
docker run -p 5000:5000 flask-portfolio

# Or use Docker Compose
docker-compose up --build


📡 API Endpoints
---------------------------------------------
Endpoint	    Method	        Authentication	        Description
---------------------------------------------------------------------
/	            GET	            None	                Portfolio homepage
/health	        GET	            None	                Health check endpoint
/scratchpad	    GET	            None	                View all comments
/scratchpad	    POST	        Required	            Post a new comment
/login/	        GET	            None	                Login page
/login/	        POST	        None	                Authenticate user
/logout/	    GET	            Required	            Logout user


📁 Project Structure
---------------------------------------------
flask-portfolio/
├── flask_app.py          # Main application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-container setup
├── .github/
│   └── workflows/
│       └── deploy.yml    # CI/CD pipeline
├── templates/
│   ├── profile.html      # Portfolio homepage
│   ├── main_page.html    # Comments scratchpad
│   └── login_page.html   # Login page
├── static/
│   └── profile.jpg       # Profile photo
└── README.md             # This file


🔮 Future Improvements
---------------------------------------------
- Add Prometheus metrics endpoint
- Deploy to Kubernetes cluster
- Implement Terraform infrastructure as code
- Add automated canary deployments
- Integrate Sentry for error tracking
- Add SSL certificate with Let's Encrypt


📧 Contact
---------------------------------------------
Khairul Rizal Bin Abd Hamid

Platform	        Link
Email	            khairul@khairulrizal.qzz.io
LinkedIn	        khairulrizalsg
GitHub	            AnarkeyV
Production Site	    khairulrizal.qzz.io
Staging Site	    khairulrizal.pythonanywhere.com


📄 License
-----------------------------------------------------------------
This project is open source and available under the MIT License.

-----------------------------------------------------------------
Built with ❤️ as part of DevOps/Cloud Support Engineering training
Last Updated: April 2026

-----------------------------------------------------------------