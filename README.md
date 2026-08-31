# Navigator AI

### Automated Current Affairs Pipeline for Navigator CA Monthly Magazine

Navigator AI is an automation project designed to streamline the creation of the **Navigator Current Affairs (CA) Monthly Magazine**.

The long-term goal is to automate the complete current-affairs workflow — from collecting source material to processing, categorising, summarising, and eventually generating magazine-ready content.

**Version 1 (v1)** focuses on the first and foundational stage of this pipeline:

> **Automatically collecting and downloading Press Information Bureau (PIB) content for a specified date range.**

The downloaded material serves as the source corpus for further processing in future versions.

---

## 🚀 Version 1 — PIB Content Collector

The first version of Navigator AI automates the collection of PIB releases.

Instead of manually visiting the PIB website and downloading releases one by one, the application allows a user to specify a **date range**, after which the system:

1. Accesses the PIB website.
2. Searches for releases published within the specified date range.
3. Identifies the relevant PIB webpages.
4. Downloads the webpages/content.
5. Stores the collected material locally for subsequent processing.

The downloaded content is **not yet transformed into magazine content** in v1. It acts as the raw input dataset for the next stages of the Navigator AI pipeline.

---

## 🎯 Project Vision

Navigator AI is being developed as a multi-stage automation pipeline for producing the Navigator CA Monthly Magazine.

The intended workflow is:

```text
                ┌─────────────────────┐
                │      PIB Website    │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Date Range Input  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   PIB Scraper       │
                │       (v1)          │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Downloaded Source   │
                │      Material       │
                └──────────┬──────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │ Content Processing      │
              │       (Future)          │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │ Topic Classification     │
              │       (Future)           │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │ Current Affairs         │
              │ Extraction & Summaries  │
              │       (Future)           │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │ Magazine-ready Content  │
              │       (Future)           │
              └─────────────────────────┘
```

---

## 📌 Current Scope

### Implemented in v1

* PIB website scraping
* Date-range based collection
* Identification of PIB releases within the selected period
* Downloading of PIB webpages/content
* Local storage of downloaded source material
* Basic project structure for future expansion

### Not yet implemented

The following capabilities are intentionally left for future versions:

* Content cleaning and extraction
* Duplicate detection
* Topic classification
* Subject/category tagging
* Important-news identification
* UPSC relevance analysis
* Current-affairs summarisation
* Fact extraction
* Linking related PIB releases
* AI-assisted content generation
* Magazine article generation
* Automatic formatting of magazine content
* Final PDF/magazine generation

---

## 🧩 Architecture

The project is structured to allow the initial scraper to become the first component of a larger processing pipeline.

```text
Navigator_AI/
│
├── src/
│   └── ...
│
├── tests/
│   └── ...
│
├── config.py
├── main.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

The architecture is intentionally modular so that future processing stages can consume the data produced by the PIB collector without requiring major changes to the collection layer.

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/sree34u/Navigator_AI.git
cd Navigator_AI
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

Run the application using:

```bash
python main.py
```

The application allows the user to provide a date range for which PIB material needs to be collected.

For example:

```text
Start Date: 01-08-2026
End Date:   31-08-2026
```

Navigator AI then collects the available PIB releases published during that period and downloads them for further processing.

---

## 📂 Output

The downloaded PIB material is stored locally and forms the **source corpus** for subsequent stages of the project.

Conceptually:

```text
Input
  │
  ├── Start Date
  └── End Date
          │
          ▼
      PIB Scraper
          │
          ▼
    PIB Webpages
          │
          ▼
   Local Source Corpus
```

The source corpus will eventually become the input for the content-processing and AI components of Navigator AI.

---

## 🛠️ Technology

The current version is built primarily with:

* **Python**
* Web scraping / HTTP-based data collection
* Local file storage
* Python project tooling

Additional technologies will be introduced as the project moves toward AI-powered content processing and magazine generation.

---

## 🗺️ Roadmap

Navigator AI is planned as an incremental project.

### v1 — Data Collection ✅

**PIB Scraper**

* [x] Accept date range
* [x] Scrape PIB releases
* [x] Download source webpages
* [x] Store collected material

### v2 — Content Extraction

* [ ] Extract article text
* [ ] Remove unnecessary webpage elements
* [ ] Standardise article structure
* [ ] Store metadata
* [ ] Detect duplicate releases

### v3 — Current Affairs Processing

* [ ] Classify content by subject
* [ ] Identify important developments
* [ ] Extract key facts
* [ ] Identify government schemes, policies, reports, missions, etc.
* [ ] Determine relevance for competitive examinations

### v4 — AI Processing

* [ ] AI-assisted summarisation
* [ ] Generate structured current-affairs notes
* [ ] Extract important facts and figures
* [ ] Generate exam-oriented explanations
* [ ] Cross-reference related developments

### v5 — Magazine Generation

* [ ] Organise articles into magazine categories
* [ ] Generate magazine-ready articles
* [ ] Create tables, fact boxes and highlights
* [ ] Apply Navigator CA editorial structure
* [ ] Automatically generate the monthly magazine

### Long-Term Vision

```text
PIB
 ↓
Collection
 ↓
Cleaning
 ↓
Classification
 ↓
Relevance Analysis
 ↓
AI Processing
 ↓
Editorial Structuring
 ↓
Magazine Generation
 ↓
Navigator CA Monthly Magazine
```

---

## 💡 Why Navigator AI?

Producing a monthly current-affairs magazine involves a large amount of repetitive work, particularly during the initial research and collection stage.

Navigator AI aims to reduce this manual workload by building an automated pipeline that can systematically collect, process and transform government information into useful current-affairs material.

The project starts with a simple principle:

> **Automate the collection first. Build intelligence on top of reliable source data later.**

Version 1 therefore deliberately focuses on creating a reliable and reproducible **source-data collection layer**.

---

## 🔮 Future Direction

The ultimate objective is not simply to scrape PIB.

Navigator AI is intended to evolve into an **end-to-end current-affairs production system** capable of turning large volumes of government and public information into structured, exam-oriented current-affairs content with minimal manual intervention.

PIB is the first data source and the first building block of that larger system.

---

## 📄 License

License information will be added as the project develops.

---

## 👨‍💻 Project

**Navigator AI**

Automating the creation of the **Navigator Current Affairs Monthly Magazine**.

Repository:
https://github.com/sree34u/Navigator_AI