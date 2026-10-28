# ✍️ AI Writing Checker

A web application that analyzes your writing and gives actionable feedback on
**grammar**, **clarity**, **conciseness**, and **tone** — with specific
suggestions that explain *why* each change helps.

It's designed to help you become a better writer, not to rewrite your work for you.

![Stack](https://img.shields.io/badge/React-19-blue) ![Stack](https://img.shields.io/badge/FastAPI-0.110-green)

---

## How it works

- The **frontend** is a React + TypeScript app (built with Vite).
- The **backend** is a Python FastAPI server that holds the API key, validates
  input, calls the AI, and returns clean structured JSON.
- **All AI requests go through the backend.** The API key never touches the browser.


---

## Prerequisites

Before you begin, make sure you have:

- **Node.js** v18 or newer — [nodejs.org](https://nodejs.org)
  (check with `node --version`)
- **Python** 3.10 or newer — [python.org](https://python.org)
  (check with `python --version`)
- **Git** — [git-scm.com](https://git-scm.com)
- A **Purdue GenAI Studio API key**
- Access to the **Purdue network / VPN** (required by the GenAI service)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-writing-checker.git
cd ai-writing-checker

### 2. Set up the backend

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1 # this step is done on Windows powershell - it may be different for other OSs
pip install fastapi "uvicorn[standard]" requests python-dotenv

### 3. Configure your API key

```bash
cp .env.example .env        # (Windows: copy .env.example to .env)
GEMMA_API_KEY=your_real_key_here

### 4. Setup the frontend

```bash
cd ../frontend
npm install

### 5. Access backend

```bash
cd backend
# activate venv (see table above)
uvicorn main:app --reload --port 8001

```local browser 
Enter http://localhost:8001/docs within Search Bar field

### 6. Access frontend

```bash
cd frontend
npm run dev

```local browser 
Enter http://localhost:5173 within Search Bar field