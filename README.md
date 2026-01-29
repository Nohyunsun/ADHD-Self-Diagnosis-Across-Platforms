# ADHD Self-Diagnosis Discourse Across Platforms  
**A Comparative Analysis of Expression and Dissemination Patterns**  
*Immediate-Reactive vs. Deep-Archive Platforms*

---

## 📌 Overview

This repository presents a complete research framework, data pipeline, and analytical methodology for a **comparative discourse analysis of ADHD self-diagnosis content across social media platforms**, focusing on how **platform affordances shape emotional expression, information dissemination, and user engagement.**

The study compares:
- **Immediate-Reactive Platforms**: Twitter (X), Instagram  
- **Deep-Archive Platforms**: YouTube, Naver Blog  

The research adopts a **mixed-methods approach**, integrating:
- Keyword Frequency Analysis  
- Composite KPI Modeling  
- Sentiment Analysis (TF-IDF Ensemble)  
- Topic Modeling (LDA)  
- Narrative Discourse Interpretation  

---

## 🎯 Research Objectives

This study aims to empirically examine how ADHD self-diagnosis discourse is expressed, disseminated, and received differently depending on platform type.

### Specific Objectives
1. Compare **keyword frequency patterns** across platform types  
2. Analyze **user engagement and reaction metrics (Composite KPI)**  
3. Compare **emotional expression patterns** across platforms  
4. Compare **topic distributions and discourse structures**

---

## 🧠 Research Design

**Study Type**: Exploratory Comparative Study  
**Methodology**: Mixed-Methods (Concurrent Design)

### Quantitative Components
- Keyword frequency analysis  
- Engagement metrics (Composite KPI)  
- Sentiment classification  
- Topic modeling (LDA)  

### Qualitative Components
- Narrative pattern interpretation  
- Platform-specific discourse analysis  
- Contextual topic labeling  

Both analytical approaches are conducted in parallel and integrated during interpretation.

---

## 🌐 Platform Scope

| Platform     | Type               | Core Characteristics |
|--------------|---------------------|----------------------|
| Twitter (X) | Immediate-Reactive | Short text, real-time interaction, emotional sharing |
| Instagram   | Immediate-Reactive | Visual storytelling, infographics, behavioral guidance |
| YouTube     | Deep-Archive       | Long-form expert explanations, vlog-style narratives |
| Naver Blog  | Deep-Archive       | Long-form self-reflection, diagnostic journeys |

---

## 📅 Data Collection Period

**January 1, 2022 – December 31, 2024**

This timeframe reflects the rapid increase in ADHD-related searches and the expansion of SNS-based self-diagnosis discourse in South Korea.

---

## 🔎 Search Keywords & Inclusion Criteria

### Search Keywords
- `ADHD 자가진단`  
- `ADHD 테스트`

### Search Scope
- Post titles  
- Main text  
- Hashtags  
- Comments  

### Inclusion Criteria
- ADHD self-diagnosis explicitly mentioned in at least one of the above fields

### Exclusion Criteria
- Unrelated mental health posts  
- Professional medical content without self-diagnosis context  
- Memes or humor-based posts  
- Automated or spam-generated content  
- Duplicate posts  

### Duplicate Removal Method
- URL normalization  
- Sentence similarity hashing  

---

## 🛠️ Data Collection Tools

All processes were conducted in **Google Colab (Python)**.

### Core Libraries
- `snscrape`  
- `requests`  
- `BeautifulSoup`  
- `YouTube Data API v3`  
- `pandas`, `numpy`  

### Platform-Specific Collection
- **Twitter (X)**: `snscrape` with `lang:ko`, `since`, `until` filters  
- **Instagram**: Public hashtag scraping via HTML parsing  
- **YouTube**: API-based keyword search with date filters  
- **Naver Blog**: Open API + HTML parsing for full-text extraction  

---

## 🧼 Data Storage & Ethics

### Stored Fields
```
doc_id, platform, created_at, text, hashtags, likes, comments, views, url
```

### Privacy Protection
- User identifiers hashed using **SHA-256**
- Only publicly available content was collected
- Redistribution of raw data is prohibited

### Ethics Approval
- IRB Exemption Approved  
  **ID: KKUIRB-202510-E-137**

---

## ⚙️ Analysis Pipeline

```
Raw Data
  ↓
HTML Parsing / API Collection
  ↓
Cleaning & Deduplication
  ↓
Tokenization (KoNLPy Okt)
  ↓
Keyword Frequency Analysis
  ↓
KPI Normalization & Modeling
  ↓
Sentiment Analysis (TF-IDF Ensemble)
  ↓
Topic Modeling (LDA)
  ↓
Visualization & Narrative Interpretation
```

---

## 🧩 Text Preprocessing

- Tokenization using **KoNLPy (Okt)**  
- POS Filtering:
  - Nouns  
  - Verbs  
  - Adjectives  
- Regex-based cleaning:
  - URLs  
  - Emojis  
  - Special characters  
- Custom stopword dictionary applied

---

## 📊 Keyword Frequency Analysis

Top-20 keywords were extracted per platform using Python’s `collections.Counter`.

### Sample Observations
- **Twitter (X)**: 검사, 성인, 병원, 증상, 의심  
- **Instagram**: 성인, 증상, 아이, 심리, 정보  
- **YouTube**: 성인, 건강, 아이, 정신, 치료  
- **Blog**: 성인, 증상, 주의력, 평가, 전문가  

---

## 📈 Engagement Metrics (Composite KPI)

### Metrics Used
- **Likes**  
- **Comments**

---

### Normalization (Min-Max)

To eliminate scale differences across platforms, all engagement metrics are normalized using Min-Max scaling:

$$
Norm_{i,p} = \frac{X_{i,p} - \min(X_p)}{\max(X_p) - \min(X_p)}
$$

Where:
- `X_{i,p}` = Raw engagement value (likes or comments) of post *i* on platform *p*  
- `min(X_p)` = Minimum engagement value observed on platform *p*  
- `max(X_p)` = Maximum engagement value observed on platform *p*  

This transforms all values into a **0–1 range**, enabling fair cross-platform comparison.

---

### Composite KPI

The composite engagement score for each post is calculated as the mean of normalized likes and comments:

$$
KPI_{i,p} = \frac{NormLike_{i,p} + NormComment_{i,p}}{2}
$$

Where:
- `NormLike_{i,p}` = Normalized likes for post *i* on platform *p*  
- `NormComment_{i,p}` = Normalized comments for post *i* on platform *p*  

This represents the **overall engagement intensity per post**.

---

### Platform-Level Average KPI

The average engagement score per platform is defined as:

$$
\overline{KPI}_p = \frac{1}{N_p} \sum_{i=1}^{N_p} KPI_{i,p}
$$

Where:
- `N_p` = Total number of posts collected from platform *p*  
- `KPI_{i,p}` = Composite KPI score of post *i*  

This value represents the **average engagement efficiency of a platform** rather than raw popularity.

---

## ⚠️ Sample Size Bias Control

Platforms with larger datasets are more likely to contain extreme values (outliers).  
Normalization ensures that engagement scores reflect **relative position within each platform’s distribution**, not raw volume dominance.

Example:
- `N_YouTube = 738`  
- `N_Instagram = 58`  

A high absolute YouTube engagement score may still translate to a lower normalized KPI if interaction is concentrated in only a few viral posts.

---

## 📊 Yearly KPI Trend Formula

$$
\overline{KPI}_{p,y} = \frac{1}{N_{p,y}} \sum_{i=1}^{N_{p,y}} KPI_{i,p,y}
$$

Where:
- `p` = Platform  
- `y` = Year (2022–2024)  
- `N_{p,y}` = Number of posts on platform *p* in year *y*  

This enables **longitudinal comparison of engagement dynamics over time**.

---

## 😊 Sentiment Analysis

### Model Architecture
**Dual-input Ensemble TF-IDF Classifier**
- Character-level TF-IDF (Weight: 0.6)  
- Word-level TF-IDF (Weight: 0.4)  

### Emotion Classes
- Happiness  
- Neutral  
- Sadness  
- Fear  
- Disgust  
- Anger  
- Surprise  

### Final Probability Calculation
$$
p_{i,k} = \alpha \cdot p_{i,k}^{(char)} + (1 - \alpha) \cdot p_{i,k}^{(word)}
$$

$$
\tilde{p}_{i,k} = \frac{s_k \cdot p_{i,k}}{\sum_{j=1}^{K} s_j \cdot p_{i,j}}
$$

Where:
- `α` = Model weight (0.6)  
- `s_k` = Class scaling factor  
- `K` = Number of emotion classes  

### Model Performance
- **Accuracy**: 0.645  
- **Macro F1-score**: 0.643  

---

## 🧠 Topic Modeling (LDA)

### Framework
- `gensim`  
- `pyLDAvis`  
- Coherence Metric: **C_v (NPMI-based)**  

### Topic Configuration

| Platform | Topics (K) | C_v |
|------------|---------------|------|
| Twitter (X) | 3 | 0.320 |
| Instagram | 5 | 0.452 |
| YouTube | 6 | 0.477 |
| Blog | 9 | 0.282 |

### Generative Model
$$
p(w|d) = \sum_{k=1}^{K} P(w|z_k) \cdot P(z_k|d)
$$

### Hyperparameters
- α = 0.1  
- β = 0.01  
- λ = 0.8  

---

## 🔍 Narrative Discourse Findings

### Twitter (X)
- Emotional flow:  
  **Uncertainty → Self-Verification → Social Empathy**  
- ADHD often framed as a potential identity marker

### Instagram
- Action-oriented visual discourse  
- Focus on routines, checklists, and behavioral guidance

### YouTube
- Expert-driven educational narratives  
- Emphasis on long-term management strategies

### Blog
- Deep self-reflective storytelling  
- Diagnosis journeys and emotional processing

---

## 📉 Platform Sentiment Patterns

| Platform | Dominant Emotional Profile |
|------------|-------------------------------|
| Twitter (X) | Sadness / Anger |
| Instagram | Neutral |
| YouTube | Sadness |
| Blog | Neutral / Sadness |

Immediate platforms emphasize **emotional release**,  
Deep-archive platforms emphasize **reflection and structured understanding**.

---

## 🧪 Visualization Tools

- `matplotlib`  
- `seaborn`  
- `wordcloud`  
- `networkx`  
- `pyLDAvis`  

### Output Types
- Keyword word clouds  
- KPI trend line plots  
- Emotion distribution heatmaps  
- Topic distance maps  
- Topic keyword bar charts  

---

## 📌 Key Contributions

- Demonstrates **platform affordance effects** on mental health discourse  
- Proposes a **hybrid emotional-information narrative model**  
- Provides a scalable **SNS health communication analysis pipeline**  
- Supports platform-specific content strategy design

---

## 🏷️ Keywords

`ADHD` · `Self-Diagnosis` · `Sentiment Analysis` · `Topic Modeling` · `KPI Modeling` · `Discourse Analysis` · `Social Media Analytics` · `Mental Health NLP`

---

## 👤 Author

**Yunsun Noh**  
M.S. in Data Science  
Konkuk University Graduate School  

---

## 📜 License

This research is for academic and non-commercial use only.  
Redistribution of raw data is prohibited.
