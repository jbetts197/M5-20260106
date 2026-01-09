# Library Data Cleansing & Enrichment

### M5-20260106

This project provides an automated solution for **cleaning, filtering, enriching, and analysing library book data**.  
It focuses on data quality, transparency of dropped records, and reproducible execution using Docker and Streamlit.

---

## Table of Contents
- [Brief](#brief)
- [User Story](#user-story)
- [Repository Structure](#repository-structure)
- [Execution Instructions for Dockerized App](#execution-instructions-for-dockerized-app)
  - [Prerequisites](#prerequisites)
  - [Execution Steps](#execution-steps)
- [Outputs](#outputs)
- [Notes](#notes)

---

## Brief

A library wants to improve their current **data quality analysis**.  
They are looking for an automated way of **cleaning, filtering, and enriching** their dataset while ensuring that dropped records are tracked and explained.

### Objectives
- Define a clear user story
- Explore and validate cleansing rules
- Implement a repeatable cleansing pipeline
- Enrich data using AI-generated book descriptions
- Provide visibility into data quality metrics

---

## User Story

- A customer borrows a book
- A customer returns a book
- A customer has an allocated amount of time to borrow a book
- The library wants to analyse borrowing behaviour using clean and reliable data

---

## Repository Structure

```text
.
├── diagrams
│   └── Architecture diagrams, data flow diagrams, and Kanban boards
│
├── helpers
│   ├── class_testing
│   │   └── Experiments and examples related to Python class design and testing
│   │
│   ├── docker_learning
│   │   └── data
│   │       └── Sample data used while learning and testing Docker concepts
│   │
│   ├── hugging_face
│   │   └── Notebooks and scripts related to AI-based enrichment using Hugging Face
│   │
│   ├── juypter_notebooks
│   │   └── Exploratory notebooks used to design and validate cleansing rules
│   │
│   └── scripts_learning
│       └── Learning scripts and experiments (includes Python cache files)
│
└── main_app
    ├── data
    │   └── Reference and intermediate datasets used by the application
    │
    ├── raw_data
    │   └── Original, unmodified input data before cleansing
    │
    ├── output_cleansed_data
    │   └── Final cleansed and enriched datasets produced by the pipeline
    │
    └── streamlit
        └── Streamlit application for visualising data quality metrics
```

---

## Execution Instructions for Dockerized App

### Prerequisites

- Docker and Docker Compose installed
- Hugging Face API token:
    - Go to https://huggingface.co/settings/tokens
    - Create a Read token
- Env at `/main_app.env` must be set using the Hugging Face API key (example `/main_app/.sample.env`)

The pipeline includes an AI enrichment step to generate book descriptions.

---

### Execution Steps

Long method:
1. `cd main_app`
2. `docker compose build library_cleanser`
3. `docker compose run --rm library_cleanser`
4. `docker compose build sqlite_web`
5. `docker compose run --rm --service-ports sqlite_web`
6. `docker compose build streamlit`
7. `docker compose run --rm --service-ports streamlit`
8. You can view sqllite data at `localhost:8080` and you can view dashboard at `localhost:8502`

Quick method:
1. `cd main_app`
2. `docker compose up -d`
3. You can view sqllite data at `localhost:8080` and you can view dashboard at `localhost:8502`

---

## Outputs
- Cleansed and enriched datasets in `main_app/output_cleansed_data`
- Dropped-record metrics with reasons
- SQLite database with web UI
- Streamlit dashboard for visual analytics

---

## Notes

- Dropped records are never silently removed
- The pipeline is repeatable and extensible
- Suitable for assessment and real-world use
