# ⚖️ Land Risk API

**Instant land-use risk intelligence for climate and investment decisions.**

## 🌍 The One-Line Truth
We help investors and climate companies understand the hidden trade-offs of land use—so they don’t make expensive or embarrassing mistakes.

---

## 🎬 How it Works (A Story-Driven Guide)

Imagine real people making real decisions about the planet.

### Scene 1: The Investor 🧑‍💼
**Who:** A climate fund manager with $50M to invest.  
**The Problem:** They are comparing two projects. Project A plants trees (great for carbon). Project B grows biofuel crops (good for energy). Both say they are "green."  
**The Tool:** They ping the API with the land coordinates.  
**The Insight:**  
- Project A: `[ Carbon: +0.9 | Biodiversity: +0.2 | Food: -0.4 ]`  
- Project B: `[ Carbon: +0.5 | Biodiversity: -0.3 | Food: +0.6 ]`  
**The Result:** The investor realizes Project A hurts the local food supply, while Project B damages wildlife habitat but helps food security. Now they can choose based on their actual fund strategy and defend that decision to their stakeholders.

### Scene 2: The Carbon Startup 🧑‍🔬
**Who:** A company selling carbon credits via reforestation.  
**The Problem:** Big corporate buyers are asking, "Are you harming biodiversity or displacing local farmers?" The startup has no quantified answer.  
**The Tool:** They run their project area through the Land Risk Engine.  
**The Result:** They get a validated report showing their project is "Nature Positive" across all three metrics. They use this to close a $1M deal with a tech giant looking for high-integrity offsets.

### Scene 3: The ESG Analyst 🧑‍💻
**Who:** Works at a global bank evaluating sustainability risk.  
**The Problem:** They review 100+ projects a month. Reports are messy PDFs and inconsistent metrics. It’s chaos.  
**The Tool:** They integrate the Land Risk API into their dashboard.  
**The Result:** Every project is instantly converted into a standard vector: `[ Carbon | Biodiversity | Food ]`. They can compare projects side-by-side in seconds, not weeks.

### Scene 4: The NGO / Standards Body 🧑‍🌾
**Who:** An organization creating the next generation of sustainability frameworks.  
**The Problem:** They need a methodology, not just opinions.  
**The Tool:** They use the API as a reference for quantifying land-use tradeoffs.  
**The Result:** The Land Risk API becomes the "credibility infrastructure" that validates their new standards.

---

## 🧠 The Key Insight (The Zoom Out)

Right now, environmental decisions are fragmented:
`Carbon report` → separate  
`Biodiversity study` → separate  
`Food impact study` → separate  

**We turn it into one vector:**  
`[ +Carbon | -Biodiversity | -Food ]`  

It’s comparable, fast, and decision-ready.

---

## 🔬 The Science (How it works under the hood)

The Land Risk API isn't magic. It's an automation layer built on top of **InVEST** (Integrated Valuation of Ecosystem Services and Tradeoffs), the world-class modeling suite from Stanford's Natural Capital Project.

### 1. Carbon (Sequestration Accounting)
We model the change in carbon stocks (biomass and soil) before and after a land-use change.

### 2. Biodiversity (Habitat Quality)
We estimate habitat degradation based on surrounding human threats (roads, urban edges, agriculture) and habitat sensitivity.

### 3. Food Security (Yield Productivity)
We calculate the loss or gain in caloric and nutritional output when land is converted from crops to other uses.

---

## 🛠️ The API in Action

### Request
```json
POST /v1/score-scenario
{
  "location": "polygon_coords",
  "current_use": "cropland",
  "proposed_use": "reforestation",
  "area_hectares": 1000
}
```

### Response
```json
{
  "tradeoff_vector": {
    "carbon_score": 0.85,
    "biodiversity_score": 0.42,
    "food_security_score": -0.61
  },
  "confidence": 0.78,
  "red_flags": [
    "High food production displacement detected"
  ],
  "recommendation": "Consider agroforestry to mitigate food security loss."
}
```

---

## 🧭 Roadmap
- [ ] Automated Earth Observation data fetching (LULC, Climate).
- [ ] Regional calibration for the Amazon and Cerrado regions.
- [ ] Integration with TNFD and EUDR compliance reporting.
- [ ] Developer SDK (Python/JavaScript).

---
*Powered by InVEST Science. Built for Climate Decision-Makers.*
