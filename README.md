# 🔍 PrivacyLens — Privacy Policy Risk Analyzer

> **Know what you're agreeing to.**  
> Paste any privacy policy URL and get an instant AI-powered risk analysis — red flags, risk score, and worst-case scenarios in seconds.

---

## 📸 Overview

PrivacyLens is a full-stack AI tool that fetches, parses, and analyzes privacy policies from any URL. It uses **Groq's LLaMA 3.3 70B** model to evaluate policy text and return:

- 🔢 A **risk score** from 1–10
- 🚩 Top **red flags** found in the policy
- ⚠️ A **worst-case scenario** summary

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, Vanilla JavaScript |
| Backend | Python, FastAPI |
| AI Model | LLaMA 3.3 70B via Groq API |
| Scraping | `requests` + `BeautifulSoup4` |
| Environment | `python-dotenv` |

---

## 📁 Project Structure

```
privacy-analyzer/
├── backend/
│   ├── main.py            # FastAPI app & /analyze endpoint
│   ├── policy_fetcher.py  # Fetches & parses policy HTML
│   ├── text_chunker.py    # Splits text into chunks
│   ├── llm_analyzer.py    # Groq LLM analysis logic
│   └── risk_utils.py      # Combines chunk results into final score
├── frontend/
│   └── index.html         # Single-page UI
├── .env                   # 🔒 Local secrets (never commit this)
├── .gitignore
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/privacy-analyzer.git
cd privacy-analyzer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

> Get your free Groq API key at [console.groq.com](https://console.groq.com/keys)

### 4. Run the backend

```bash
cd backend
python -m uvicorn main:app --reload
```

The API will be live at `http://127.0.0.1:8000`

### 5. Open the frontend

Open `frontend/index.html` directly in your browser — no build step needed.

---

## 🚀 Usage

1. Start the backend server (Step 4 above)
2. Open `frontend/index.html` in your browser
3. Paste any privacy policy URL (e.g. `https://policies.google.com/privacy`)
4. Click **Analyze →** or press `Enter`
5. View the risk score, red flags, and worst-case scenario

### Example URLs to test

```
https://policies.google.com/privacy
https://www.reddit.com/policies/privacy-policy
https://twitter.com/en/privacy
```

---

## 🔌 API Reference

### `POST /analyze`

Analyzes a privacy policy from a given URL.

**Request Body:**
```json
{
  "url": "https://example.com/privacy-policy"
}
```

**Response:**
```json
{
  "final_risk_score": 7.3,
  "top_red_flags": [
    "Data shared with third-party advertisers",
    "Broad data retention with no clear deletion policy",
    "Location data collected even when app is closed"
  ],
  "worst_case": "Your personal data, location, and usage patterns could be sold to advertisers or handed to authorities without your direct consent."
}
```

**Risk Score Guide:**

| Score | Level |
|---|---|
| 1 – 3 | 🟢 Low Risk |
| 4 – 6 | 🟡 Moderate Risk |
| 7 – 8 | 🔴 High Risk |
| 9 – 10 | ⛔ Critical Risk |

---

## 🔐 Security

This project uses environment variables to keep API keys safe.

- **Never commit your `.env` file** — it is listed in `.gitignore`
- Store production secrets in **GitHub → Settings → Secrets and variables → Actions**
- If you accidentally expose a key, rotate it immediately at [console.groq.com/keys](https://console.groq.com/keys)

---

## 📦 Requirements

```
fastapi
uvicorn
requests
beautifulsoup4
groq
python-dotenv
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🛣️ Roadmap

- [ ] Support for direct text input (paste policy manually)
- [ ] PDF privacy policy upload support
- [ ] Side-by-side policy comparison
- [ ] Browser extension integration
- [ ] Scoring history & saved results

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## ⚠️ Disclaimer

PrivacyLens is for **informational purposes only**. Results are AI-generated and may not be legally accurate. Always consult a legal professional for formal privacy policy evaluation.

---

*Built with ❤️ using FastAPI + Groq + LLaMA 3.3*
