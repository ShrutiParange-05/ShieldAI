# 🛡️ ShieldAI: Enterprise-Grade Secure Code Reviewer

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Llama 3](https://img.shields.io/badge/AI-Llama_3-0467DF?style=for-the-badge&logo=meta&logoColor=white)
![Security](https://img.shields.io/badge/Cybersecurity-AppSec-00CC96?style=for-the-badge)

ShieldAI is a **Next-Gen Static Application Security Testing (SAST)** tool powered by local LLMs (Llama 3). It acts as an automated security engineer, detecting vulnerabilities (OWASP Top 10), explaining them, and **auto-remediating** insecure code in real-time.

---

## 🚀 Key Features

*   **🔍 AI-Powered Scanning:** Detects logic flaws (e.g., Insecure Deserialization, Broken Access Control) that regex-based scanners miss.
*   **🤖 Interactive Security Tutor:** A built-in "Chat with Code" assistant that explains *why* a line is dangerous.
*   **⚡ Auto-Remediation:** Instantly generates secure, refactored code (e.g., replacing `os.system` with `subprocess`).
*   **🎨 Cyberpunk UI:** A modern, dark-mode dashboard built with Streamlit and Custom CSS.
*   **🔒 Privacy-First:** Runs 100% locally using Ollama. No code ever leaves your machine.

---

## 🛠️ Tech Stack

*   **Core Engine:** Python 3.10+
*   **Frontend:** Streamlit (with Custom CSS/Glassmorphism)
*   **AI Model:** Llama 3 (via Ollama)
*   **Editor Component:** `streamlit-code-editor`
*   **Parsing:** JSON-enforced output for structured reporting

---

## 📸 Screenshots

### 1. The Dashboard
<img width="1811" height="917" alt="image" src="https://github.com/user-attachments/assets/13e2c62e-87f6-4048-8823-41bcb8ce0dd5" />


### 2. The AI Tutor
<img width="880" height="575" alt="image" src="https://github.com/user-attachments/assets/4ad39a83-9fe7-4c12-ad5d-0c1ec87fd3f8" />


---

## 📦 Installation & Setup

### 1. Prerequisites
*   **Python 3.10+**
*   **Ollama** installed and running ([Download Here](https://ollama.com))

### 2. Pull the Model
