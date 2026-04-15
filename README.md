```markdown
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Flask 2.2.3](https://img.shields.io/badge/flask-2.2.3-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/AWS-EC2-orange.svg)](https://aws.amazon.com/)
[![CodeQL](https://github.com/AnarkeyV/flask-portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/AnarkeyV/flask-portfolio/actions)

# Khairul Rizal's DevOps Portfolio

[![CI/CD Pipeline](https://github.com/AnarkeyV/flask-portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/AnarkeyV/flask-portfolio/actions)
[![Security Scan](https://github.com/AnarkeyV/flask-portfolio/actions/workflows/deploy.yml/badge.svg)](https://github.com/AnarkeyV/flask-portfolio/actions)
[![Health Status](https://img.shields.io/website?url=https%3A%2F%2Fkhairulrizal.qzz.io%2Fhealth&label=Production%20Health)](https://khairulrizal.qzz.io/health)

## 🚀 Live Sites

| Environment | URL | Status |
|-------------|-----|--------|
| **Production (AWS)** | [khairulrizal.qzz.io](https://khairulrizal.qzz.io) | [![Health](https://img.shields.io/website?url=https%3A%2F%2Fkhairulrizal.qzz.io%2Fhealth)](https://khairulrizal.qzz.io/health) |
| **Staging (PythonAnywhere)** | [khairulrizal.pythonanywhere.com](https://khairulrizal.pythonanywhere.com) | [![Health](https://img.shields.io/website?url=https%3A%2F%2Fkhairulrizal.pythonanywhere.com%2Fhealth)](https://khairulrizal.pythonanywhere.com/health) |

## 📋 Project Overview

A full-stack Flask web application demonstrating DevOps best practices including CI/CD automation, security hardening, observability, and multi-environment deployment. Built as part of my DevOps/Cloud Support Engineering training.

### Features

- **User Authentication**: Login/logout with password hashing (scrypt)
- **Comments System**: Authenticated users can post comments
- **Contact Form**: EmailJS integration with honeypot protection
- **Admin Features**: Login attempt auditing and monitoring

## 🏗️ Architecture
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Local │────▶│ GitHub │────▶│ Security │
│ Dev │ │ Actions │ │ Scanning │
└─────────────┘ └─────────────┘ │ - Bandit │
│ - Safety │
│ - Trivy │
└─────────────┘
│
┌────────────────────────────┼────────────────────────────┐
│ │ │
▼ ▼ ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Staging │ │ Production │ │ Monitoring │
│ PythonAny │ │ AWS EC2 │ │ - Health │
│ where │ │ Ubuntu │ │ Endpoint │
└─────────────┘ └─────────────┘ │ - Audit │
│ Logs │
└─────────────┘


## 🔒 Security Features

| Feature | Implementation |
|---------|----------------|
| **Security Headers** | Flask-Talisman (CSP, X-Frame-Options, X-XSS-Protection) |
| **Rate Limiting** | 5 attempts/minute on login, 10/minute on comments |
| **Password Hashing** | scrypt algorithm with per-user salts |
| **Login Audit** | All attempts logged with IP and user agent |
| **Bot Protection** | Honeypot field in contact form |
| **CI/CD Scanning** | Bandit, Safety, Trivy in pipeline |

## 📊 Observability

- **Health Endpoint**: `/health` with database connectivity check
- **Login Audit Table**: Track all authentication attempts
- **Structured Logging**: Environment-aware logging configuration

## 🔄 CI/CD Pipeline

### Stages
1. **Security Scan** - Bandit, Safety, Trivy
2. **Test** - Flask app initialization
3. **Deploy to Staging** - PythonAnywhere
4. **Deploy to Production** - AWS EC2

### GitHub Secrets Required
- `PA_API_TOKEN` - PythonAnywhere API token
- `PA_USERNAME` - PythonAnywhere username
- `EC2_SSH_KEY` - AWS EC2 private key
- `EC2_HOST` - EC2 instance hostname

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Flask 2.2.3, Python 3.13 |
| **Database** | SQLite, SQLAlchemy ORM |
| **Security** | Flask-Talisman, Flask-Limiter, scrypt |
| **Deployment** | GitHub Actions, Docker, AWS EC2, PythonAnywhere |
| **Monitoring** | Custom health endpoint, audit logging |
| **Domain** | Cloudflare CDN, Zoho Mail |

## 📈 DevOps Skills Demonstrated

- ✅ Infrastructure as Code (Docker, docker-compose)
- ✅ CI/CD Pipeline Design (GitHub Actions)
- ✅ Multi-environment Deployment (staging/production)
- ✅ Security Hardening (headers, rate limiting, scanning)
- ✅ Observability (health checks, audit logging)
- ✅ Container Orchestration (Docker, Docker Compose)
- ✅ Cloud Deployment (AWS EC2, PythonAnywhere)

## 🐳 Local Development

```bash
# Clone repository
git clone https://github.com/AnarkeyV/flask-portfolio.git
cd flask-portfolio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
flask run

# Or with Docker
docker build -t flask-portfolio .
docker run -p 5000:5000 flask-portfolio

# API Endpoints
Endpoint	Method		Description
/		GET		Portfolio homepage
/health		GET		Health check
/scratchpad	GET/POST	Comments system
/login/		GET/POST	User authentication
/logout/	GET		Logout


