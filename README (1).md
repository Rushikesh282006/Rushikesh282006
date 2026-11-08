<!-- ═════════════ HEADER BANNER ═════════════ -->
<div align="center">

<img src="./assets/hero.svg" alt="Rushikesh Jagtap — Python Backend Developer · Machine Learning Engineer · AI Developer" width="100%" />

<br/>

<a href="https://www.linkedin.com/in/rushikesh-jagtap-07b787376/"><img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="https://leetcode.com/u/Rushi_28/"><img src="https://img.shields.io/badge/LeetCode-Rushi__28-FFA116?style=for-the-badge&logo=leetcode&logoColor=black" alt="LeetCode" /></a>
<a href="https://github.com/Rushikesh282006"><img src="https://img.shields.io/github/followers/Rushikesh282006?label=Followers&style=for-the-badge&logo=github&color=181717" alt="GitHub followers" /></a>
<img src="https://komarev.com/ghpvc/?username=Rushikesh282006&label=Profile%20Views&color=6366f1&style=for-the-badge" alt="Profile views" />

<br/><br/>

**✨ Consistent. Curious. Building with Intelligence. ✨**

</div>

<br/>

<!-- ═════════════ AT A GLANCE ═════════════ -->
<div align="center">

| 🎓 Academics | 🧠 Focus | 🏆 Hackathons | 🤝 Open To |
|:---:|:---:|:---:|:---:|
| **9.7 CGPA**<br/>3rd-year IT Engineering | **End-to-end ML pipelines**<br/>& AI-integrated backends | **SIH 2025 & 2026**<br/>Shortlisted · Top-10 Hack & Track | **Open-source collabs**<br/>with reciprocal teamwork |

</div>

<br/>

<!-- ═════════════ ABOUT ═════════════ -->
## 🚀 About Me

```python
class Rushikesh:
    role     = "Python Backend Developer · ML Engineer"
    studying = "B.E. Information Technology (3rd year)"
    building = ["Multi-tenant RAG platforms", "ML pipelines", "Scalable FastAPI services"]
    exploring = ["Graph Neural Networks", "Advanced ML architectures"]
    looking_for = "Impactful open-source projects & authentic teamwork"
```

<br/>

<!-- ═════════════ TECH STACK ═════════════ -->
## 💻 Tech Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=py,java,c,fastapi,tensorflow,sklearn,pandas,numpy&perline=8" alt="Core" />
<br/>
<img src="https://skillicons.dev/icons?i=react,js,html,css,tailwind,mysql,postgres,mongodb&perline=8" alt="Web and DB" />
<br/>
<img src="https://skillicons.dev/icons?i=redis,docker,git,github,postman,vercel&perline=6" alt="Tools" />

</div>

<br/>

<details open>
<summary><b>📚 Full breakdown</b></summary>

<br/>

| Area | Technologies |
|:--|:--|
| **Languages** | `Python` `Java` `C` |
| **Backend** | `FastAPI` `Pydantic` `SQLAlchemy` `Celery` `Redis` |
| **AI / ML / Data** | `TensorFlow` `Scikit-learn` `Pandas` `NumPy` `LLMs` `RAG Architecture` `Vector DBs` |
| **Frontend** | `HTML5` `CSS3` `JavaScript` `React` `Tailwind CSS` |
| **Databases** | `MySQL` `MongoDB` `PostgreSQL (pgvector)` |
| **Tools** | `Git` `GitHub` `Postman` `Power BI` `Docker` `Antigravity` |

</details>

<br/>

<!-- ═════════════ PROJECTS ═════════════ -->
## 🛠️ Featured Projects

### 📄 Multi-Tenant Document RAG Platform

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" /> <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white" /> <img src="https://img.shields.io/badge/pgvector-336791?style=flat-square" /> <img src="https://img.shields.io/badge/Celery-37814A?style=flat-square&logo=celery&logoColor=white" /> <img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white" /> <img src="https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black" /> <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />

> A document question-answering app designed to keep each user's documents and retrieval context **fully isolated**.

<div align="center">
<img src="./assets/rag-pipeline.svg" alt="Architecture of the Multi-Tenant Document RAG Platform" width="100%" />
</div>

- 📥 PDF ingestion and background processing with **Celery + Redis**
- 🔍 **Hybrid retrieval**: pgvector similarity search + PostgreSQL full-text search, fused with **Reciprocal Rank Fusion**
- ⚡ Responses streamed via **Server-Sent Events**, with **source-page citations**
- 🔐 Tenant-scoped data access at both the application and database layer

<a href="https://github.com/Rushikesh282006/Document_Rag"><img src="https://img.shields.io/badge/Source_Code-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
<a href="https://document-rag-olive.vercel.app/"><img src="https://img.shields.io/badge/Live_Demo-38BDF8?style=for-the-badge&logo=vercel&logoColor=black" /></a>

<br/>

### 🎭 Emotion Scanner

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/TensorFlow_Lite-FF6F00?style=flat-square&logo=tensorflow&logoColor=white" /> <img src="https://img.shields.io/badge/Bi--GRU-6366f1?style=flat-square" /> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" /> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black" />

> Text-based emotion classification across **six emotion categories**, returning confidence scores.

<div align="center">
<img src="./assets/emotion-scanner.svg" alt="Architecture of Emotion Scanner: Bi-GRU trained, converted to TensorFlow Lite, served via FastAPI" width="100%" />
</div>

- 🧠 Trained a custom **Bidirectional GRU** model for text classification
- 📦 Converted to **TensorFlow Lite** and served behind a FastAPI endpoint
- 💬 Web interface for real-time text predictions

<a href="https://github.com/Rushikesh282006/Emotion_Predictor"><img src="https://img.shields.io/badge/Source_Code-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
<a href="https://emotion-predictor-j013.onrender.com/"><img src="https://img.shields.io/badge/Live_Demo-38BDF8?style=for-the-badge&logo=render&logoColor=black" /></a>

<br/>

### 🏠 House Price Predictor

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" /> <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white" /> <img src="https://img.shields.io/badge/Random_Forest-22c55e?style=flat-square" /> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" /> <img src="https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white" /> <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white" />

> End-to-end regression app for estimating California house values from single inputs or **batch CSV uploads**.

<div align="center">
<img src="./assets/house-price.svg" alt="Architecture of House Price Predictor: Random Forest served via FastAPI and Pydantic in Docker" width="100%" />
</div>

- 🌲 Random Forest model trained on the California Housing dataset (**20,640 records**)
- ✅ Prediction endpoints with Pydantic validation and batch CSV support
- 📈 Performance: **R² ≈ 0.805** · **MAE ≈ $32,800**

<a href="https://github.com/Rushikesh282006/House_Price_Predictor"><img src="https://img.shields.io/badge/Source_Code-181717?style=for-the-badge&logo=github&logoColor=white" /></a>
<a href="https://house-price-predictor-gd9p.onrender.com/"><img src="https://img.shields.io/badge/Live_Demo-38BDF8?style=for-the-badge&logo=render&logoColor=black" /></a>

<br/>

<!-- ═════════════ GOALS ═════════════ -->
## 🎯 Currently Leveling Up

<div align="center">

| 🧩 Algorithmic Thinking | 🏗️ Robust Backends | 🔬 Advanced ML |
|:---:|:---:|:---:|
| Solving DSA patterns to sharpen problem-solving | Building scalable, backend-driven AI/ML systems | Exploring Graph Neural Networks & modern architectures |

</div>

<br/>

<!-- ═════════════ ACHIEVEMENTS ═════════════ -->
## 🏆 Hackathons & Achievements

- 🇮🇳 **Smart India Hackathon** — 2× shortlisted (SIH 2025 & SIH 2026) in the college internal qualifier
- 🥇 **Hack & Track** — Top-10 team, organized by Fr. Agnel College, Vashi
- 🎓 **Academic Excellence** — Ranked **2nd** in the IT branch in both 1st and 2nd year

<br/>

<!-- ═════════════ LIVE DASHBOARD ═════════════ -->
## 📡 Live Dashboard

<div align="center">

<img src="./assets/github-live.svg" alt="Live GitHub activity: contribution heatmap, streaks, repos and top languages" width="100%" />

<br/><br/>

<img src="./assets/leetcode-live.svg" alt="Live LeetCode stats: problems solved, rank and recent submissions" width="100%" />

<br/>

<sub>🔄 Redrawn every 3 hours by a GitHub Action, straight from the GitHub and LeetCode APIs</sub>

</div>

<br/>

<!-- ═════════════ FOOTER ═════════════ -->
<div align="center">

### 💬 Let's build something great together

<a href="https://www.linkedin.com/in/rushikesh-jagtap-07b787376/"><img src="https://img.shields.io/badge/Reach_me_on-LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" /></a>

<sub>Built with curiosity · Mumbai, India 🇮🇳</sub>

</div>
