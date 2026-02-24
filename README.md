# EKA-AI Platform

This repository contains the backend for the EKA-AI platform, a production-grade, governed automobile intelligence system.

## Overview

EKA-AI consists of five core models:
1.  **EKA Chat**: A governed intelligence layer for diagnostics and troubleshooting.
2.  **EKA Job Flow**: An operational engine for orchestrating service jobs.
3.  **EKA-MG**: A deterministic engine for calculating maintenance guarantees.
4.  **EKA Operator**: An action agent for translating natural language commands into tool calls.
5.  **EKA Dashboard**: An insight layer for BI and trend analysis.

For a detailed explanation of the architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Getting Started

### Prerequisites

- Python 3.9+
- Docker
- An account with access to the Gemini API.

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/eka-ai-platform.git
    cd eka-ai-platform
    ```
2.  Create a virtual environment and install the dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3.  Set up your environment variables by copying `.env.example` to `.env` and filling in the required values.
    ```bash
    cp .env.example .env
    ```
4.  Run the database migrations:
    ```bash
    alembic upgrade head
    ```
5.  Run the application:
    ```bash
    uvicorn app.main:app --reload
    ```

## Running with Docker

To run the application using Docker, use the following command:

```bash
docker-compose up -d
```
