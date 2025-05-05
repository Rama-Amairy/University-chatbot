Here’s a cleaned-up and more professional version of your README file with corrected grammar, consistent formatting, and improved clarity:

---

# University AI Assistant

A **FastAPI-powered AI Assistant** that helps university students with common administrative tasks. It uses **LangGraph** for reasoning and workflows, and a **PDF handbook** as the only knowledge base.

---

## 🚀 Run the Project

### ✅ Requirements

* **Linux OS**
* **Docker**
* **Python 3.13.2**

---

### 📦 Setup Environment

#### 1. Create a Virtual Environment

```bash
python -m venv ENV
```

#### 2. Activate the Environment

```bash
source ENV/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 🔐 Configure Environment Variables

Rename `.env.example` to `.env` and update the values based on your settings.

---

### 🧠 Run the FastAPI Server

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

* Open the API docs in your browser:
  [http://localhost:5000/docs](http://localhost:5000/docs)

---

### 🗂 Access Qdrant Dashboard

* Open Qdrant dashboard in your browser:
  [http://localhost:6333/dashboard#/](http://localhost:6333/dashboard#/)
