# 📑 Simple Paper Finder

A **simple academic paper search tool** for top AI/ML conferences and journals.
It can scrape official accepted papers pages, search by keywords, fetch abstracts from detail pages, and export results in **Markdown** and **JSON**.

Supports **interactive mode** and **command-line mode**.

---

## ✨ Features

* 🔍 Search papers from major conferences (ICML, NeurIPS, ICLR, AAAI, CVPR, ACL, etc.)
* 📅 Filter by conference year (2020–2025 supported in config)
* 📝 Keyword-based search (`unlearning`, `federated learning`, etc.)
* 📄 Automatically fetch abstracts (from detail pages if missing on list page)
* 📊 Exports results into:

  * `output/*.md` → human-readable report
  * `output/*.json` → structured data
* 🐞 Debug mode: saves raw HTML to `output/debug_*.html` for inspection

---

## 📂 Project Structure

```
.
├── main.py                 # Entry point (interactive + CLI)
├── simple_paper_finder.py  # Core scraper class
├── search_config.yaml      # Config: parsing rules, filters, keywords
├── output/                 # Results (Markdown, JSON, debug HTML)
└── README.md               # Documentation
```

---

## ⚡ Installation

### 1. Clone the repo

```bash
git clone https://github.com/jessecu2024/search_paper.git
cd search_paper
```

### 2. Setup environment (recommended: uv / venv / conda)

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

*(The project mostly uses Python standard library; no heavy deps required.)*

---

## ▶️ Usage

### **Interactive Mode**

Run:

```bash
python simple_paper_finder.py
```

You will be prompted to:

1. Select conferences
2. Select years
3. Enter keywords

Then results will be printed and exported to `output/`.

## 📜 License

MIT License. Free to use and modify.

---

👉 Would you like me to also add a **quickstart section for PyCharm users** (so you can just “Run” inside IDE without CLI), or keep it CLI-oriented?
