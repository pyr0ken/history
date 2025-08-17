# AgentQL Airflow Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Airflow](https://img.shields.io/badge/Airflow-2.6+-orange.svg)](https://airflow.apache.org/)

A production-ready web scraping solution using AgentQL API with Apache Airflow orchestration.

## 🚀 Features

- **Automated Web Scraping**: Extract structured data from websites using AgentQL's powerful API
- **Airflow Orchestration**: Schedule, monitor, and manage scraping workflows
- **Data Validation**: Ensure data quality with JSON Schema validation
- **Resilient Operations**: Automatic retries, error handling, and recovery mechanisms
- **Multi-Storage Support**: Save data to PostgreSQL and backup to S3
- **Production-Ready**: Dockerized with proper logging, monitoring, and security
- **Scalable Architecture**: Easily extendable with custom operators and hooks

## 📋 Prerequisites

- Docker and Docker Compose
- AgentQL API Key (sign up at [agentql.com](https://agentql.com))
- PostgreSQL Database (optional, included in Docker setup)
