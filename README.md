# Velora Mobitech

Velora Mobitech is a full-stack optimization web application built using a microservice architecture. It allows users to upload input data, process it through a Python-based optimization engine, and view structured results in the browser.

🌐 Live: https://velora-mobitech.vercel.app

## 🧠 What This Project Does

- Uploads input data from the UI
- Sends it to a Node.js backend
- Backend forwards data to a FastAPI optimization service
- Returns optimized results as JSON
- Displays results on the frontend

## 🛠 Tech Stack

- React (Frontend)
- Node + Express (Backend)
- Python (Optimisation)

## 📁 Folder Structure

```
Velora-Mobitech/
│
├── backend/        # Express API
├── frontend/       # React (Vite)
├── python/         # FastAPI Optimization Engine
├── package.json    # Root scripts
└── README.md
```
## ⚙️ Local Setup

### 1️⃣ Clone the repository
```bash
git clone abcd
cd Velora-Mobitech
```
### 2️⃣ Install dependencies
```bash
npm run install-all
```
### 3️⃣ Add environment variables
**Backend (backend/.env)**
```Code
PORT=5000
PYTHON_API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```
**Frontend (frontend/.env)**
```Code
VITE_API_URL=http://localhost:5000
```
### 4️⃣ Run all services
```bash
npm run dev
```
This starts:
- React frontend
- Node backend
- FastAPI Python service

## 🌍 Deployment Notes
- Frontend deployed on *Vercel*
- Backend and Python service deployed on *Render*

