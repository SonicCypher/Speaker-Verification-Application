# Project Setup Guide

This project is a Streamlit application that connects to a PostgreSQL database. Follow the steps below to set up and run the application locally.

## Prerequisites

* Conda or any Python environment manager
* Docker (for PostgreSQL setup)

---

## Setup Instructions

### 1. Python Environment Setup

Create a Python environment using the specified Python version:

#### Using Conda

```bash
# Create a new conda environment with Python 3.10.16
conda create -n your-env-name python=3.10.16

# Activate the environment
conda activate your-env-name
```

#### Using venv (Alternative)

```bash
# Create a virtual environment (ensure Python 3.10.16 is installed)
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

---

### 2. Install Required Packages

Install all necessary dependencies using the requirements file:

```bash
pip install -r requirements.txt
```

---

### 3. Database Configuration

#### PostgreSQL Setup with Docker

For setting up PostgreSQL with Docker, refer to this guide:
[Get PostgreSQL and pgAdmin 4 up and running with Docker](https://medium.com/@marvinjungre/get-postgresql-and-pgadmin-4-up-and-running-with-docker-4a8d81048aea)

#### Environment Configuration

Create a `.env` file inside the `src` directory with your database configuration:
Add the following to `src/.env`:

```env
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

---

### 4. Running the Application

Run the Streamlit app from the root folder:

```bash
streamlit run src/app.py
```

The app should be accessible in your browser at:
[http://localhost:8501](http://localhost:8501)

---


