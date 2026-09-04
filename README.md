# 📈 Real-Time Stock Market Analytics Platform

A real-time analytics platform that ingests stock market events, processes streaming data using Apache Spark, computes technical indicators and market metrics, and exposes insights through REST APIs and interactive dashboards.

---

## 🚀 Overview

This project demonstrates a modern data engineering architecture for processing real-time stock market data. It combines event streaming, stream processing, backend APIs, and frontend visualization to deliver actionable market insights.

### Key Capabilities

- Real-time stock market data ingestion
- Streaming analytics and aggregations
- Technical indicator calculations
- Price movement alerts
- REST API for analytics queries
- Interactive dashboards
- Historical data analysis

---

## 🏗️ Architecture

```text
Stock API
   │
   ▼
Kafka Producer
   │
   ▼
Kafka Topic(s)
   │
   ▼
Spark Structured Streaming
   │
   ├──────────────┐
   ▼              ▼
PostgreSQL       S3
   │
   ▼
FastAPI
   │
   ▼
React Dashboard
```

### Data Flow

1. **Stock API** provides real-time market data.
2. **Kafka Producer** publishes stock events to Kafka topics.
3. **Kafka Topics** act as the event streaming layer.
4. **Spark Structured Streaming** consumes and processes events in real time.
5. Processed data is stored in:
   - **PostgreSQL** for analytics and API queries
   - **Amazon S3** for historical storage and future data lake capabilities
6. **FastAPI** exposes analytics and market insights through REST endpoints.
7. **React Dashboard** visualizes real-time market activity, trends, and indicators.
```

---

## 🛠️ Technology Stack

### Data Ingestion
- Apache Kafka

### Stream Processing
- Apache Spark Structured Streaming

### Backend
- FastAPI
- Python

### Database
- PostgreSQL

### Frontend
- React (Vite, TypeScript)

### Infrastructure
- Docker & Docker Compose

---

## ⚡ Getting Started: Clone & Run

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/real-time-stock-analytics-platform.git
cd real-time-stock-analytics-platform
```

---

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
FINNHUB_API_KEY=your_finnhub_api_key_here
FINNHUB_EXCHANGE=US
FINNHUB_SYMBOL_LIMIT=25
```

---

### 3. Start Infrastructure (PostgreSQL & Kafka)

Make sure Docker Desktop is running, then start the containers:

```bash
docker compose up -d postgres kafka
```

---

### 4. Setup & Run the Backend API

Open a terminal in the root directory:

```powershell
# 1. Create and activate a Python virtual environment (recommended)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Start the FastAPI backend server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 5. Start Data Ingestion Pipeline (Consumer & Producer)

Open two separate terminals to stream live stock data into Kafka and PostgreSQL:

- **Terminal 1 (Kafka Consumer -> PostgreSQL):**
  ```powershell
  python consumer/main.py
  ```

- **Terminal 2 (Finnhub Producer -> Kafka):**
  ```powershell
  python producer/main.py
  ```

---

### 6. Setup & Run the Frontend Dashboard

Open another terminal in the frontend directory:

```powershell
cd frontend

# 1. Install Node dependencies
npm install

# 2. Start the Vite development server
npm run dev
```

- **Market Pulse Dashboard**: [http://localhost:5173](http://localhost:5173)

---

## ✨ Features

### Real-Time Data Ingestion
Continuously collect stock prices and market events from external APIs.

### Stream Processing
Process incoming events in near real time using Spark Structured Streaming.

### Technical Indicators
Calculate metrics such as:

- Moving Averages (SMA/EMA)
- RSI
- MACD
- Volume Trends

### Alert Generation
Generate notifications when predefined market conditions are met.

### Live Dashboards
Visualize stock activity, trends, and performance metrics.

### Historical Analytics
Query and analyze historical market data for deeper insights.

---

## 📂 Project Structure

```text
real-time-stock-analytics-platform/
│
├── producer/          # Stock data producers
├── kafka/             # Kafka configuration
├── spark/             # Streaming jobs
├── database/          # PostgreSQL scripts
├── api/               # FastAPI services
├── frontend/          # React application
├── docker/            # Docker configuration
└── docs/              # Documentation
```

---

## 🔄 Data Flow

1. Stock market events are collected from external APIs.
2. Events are published to Kafka topics.
3. Spark Structured Streaming consumes and processes events.
4. Calculated metrics are stored in PostgreSQL.
5. FastAPI exposes analytics endpoints.
6. React dashboards display real-time insights
