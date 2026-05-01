# 📥 Policy PDF Download Guide

**Purpose:** Populate the RAG pipeline with real government policy documents  
**Target Folder:** `data/raw/` (this folder)  
**Deadline:** ASAP - Needed for `setup_rag.py` to work

---

## ✅ 5 Required PDFs - Download Instructions

### PDF #1: Washington RCW 82.08.809
**Topic:** EV Sales Tax Exemption Law  
**Link:** https://app.leg.wa.gov/rcw/default.aspx?cite=82.08.809  
**Steps:**
1. Click link above
2. Press Ctrl+P (print)
3. Choose "Save as PDF"
4. **Save as:** `wa_rcw_82_08_809_tax_exemption.pdf`

**Expected Size:** 4-6 pages  
**Content:** Official Washington tax exemption for EVs, CAFV eligibility details

---

### PDF #2: AFDC Washington Incentives Summary
**Topic:** Complete WA State EV Incentives & Laws Database  
**Link:** https://afdc.energy.gov/laws/state_summary?state=WA  
**Steps:**
1. Click link above
2. Press Ctrl+P
3. Choose "Save as PDF"
4. **Save as:** `afdc_washington_state_ev_incentives_guide.pdf`

**Expected Size:** 8-12 pages  
**Content:** 73+ state and utility incentives, subsidies, grants, requirements

---

### PDF #3: IRA Clean Vehicle Tax Credits
**Topic:** Federal EV Tax Credit Information  
**Link:** Search on energy.gov OR https://www.energy.gov/eere/vehicles  
**Steps:**
1. Visit energy.gov
2. Search for "clean vehicle credit fact sheet" OR "inflation reduction act"
3. Look for PDF fact sheet
4. Download or print to PDF
5. **Save as:** `federal_ira_clean_vehicle_tax_credits.pdf`

**Expected Size:** 2-4 pages  
**Content:** Federal tax credits (up to $7,500 new, $4,000 used), eligibility

---

### PDF #4: NEVI Formula Program Guidance
**Topic:** National EV Infrastructure Funding Program  
**Link:** https://highways.dot.gov/iija/guidance-regulations  
**Steps:**
1. Click link above
2. Search page for "NEVI" or "Electric Vehicle"
3. Find implementation guidance PDF
4. Download or print to PDF
5. **Save as:** `federal_nevi_formula_program_guidance.pdf`

**Expected Size:** 10-20 pages  
**Content:** Federal funding for EV charging infrastructure nationwide

---

### PDF #5: Washington ZEV Mandate (ACC II)
**Topic:** Zero Emission Vehicle Requirements & 2035 Mandate  
**Link:** https://ecology.wa.gov/ (search for "ACC II" or "ZEV")  
**Alternative Search:** "Washington state Advanced Clean Cars II PDF"  
**Steps:**
1. Search for the document
2. Download or print to PDF
3. **Save as:** `washington_zev_mandate_2035_acc_ii.pdf`

**Expected Size:** 5-10 pages  
**Content:** Washington adopts California ZEV standards, 100% zero-emission by 2035

---

## 📂 File Organization After Download

```
data/raw/
├── DOWNLOAD_GUIDE.md                           (this file)
├── wa_rcw_82_08_809_tax_exemption.pdf          ← DOWNLOAD #1
├── afdc_washington_state_ev_incentives_guide.pdf ← DOWNLOAD #2
├── federal_ira_clean_vehicle_tax_credits.pdf   ← DOWNLOAD #3
├── federal_nevi_formula_program_guidance.pdf   ← DOWNLOAD #4
└── washington_zev_mandate_2035_acc_ii.pdf      ← DOWNLOAD #5
```

---

## 🚀 Next Steps After Downloading

Once all 5 PDFs are in `data/raw/`:

### 1. Run RAG Pipeline Setup
```bash
cd c:\Users\nisar\OneDrive\Documents\SEM 2\AI for engineers\EV_project
python scripts/setup_rag.py
```

**Expected Output:**
```
Loading markdown policy files...
  Loaded federal_ira_tax_credits.md: X chunks
  Loaded nevi_wa_infrastructure_plan.md: X chunks
  ...

Loading raw PDF files...
  Loaded wa_rcw_82_08_809_tax_exemption.pdf: X chunks
  Loaded afdc_washington_state_ev_incentives_guide.pdf: X chunks
  Loaded federal_ira_clean_vehicle_tax_credits.pdf: X chunks
  Loaded federal_nevi_formula_program_guidance.pdf: X chunks
  Loaded washington_zev_mandate_2035_acc_ii.pdf: X chunks

Total chunks to embed: 200+
Embedding and upserting to Pinecone...
```

### 2. Verify Pinecone Index
```bash
python -c "
import os
from pinecone import Pinecone
from dotenv import load_dotenv
load_dotenv()
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('ev-policy-docs')
stats = index.describe_index_stats()
print(f'Total vectors in index: {stats[\"total_vector_count\"]}')
"
```

Should show: **200+ vectors**

### 3. Test RAG Query
```bash
python -c "
from scripts.rag_query import query_policy_docs
results = query_policy_docs('What is the Washington state EV tax exemption amount?', top_k=3)
for r in results:
    print(f\"Source: {r['source']}\")
    print(f\"Score: {r['score']}\")
    print(f\"Text: {r['text'][:200]}...\")
    print('---')
"
```

Should return **relevant policy chunks** from downloaded PDFs

---

## ⚠️ Important Notes

### All documents are PUBLIC DOMAIN
- ✅ From U.S. Government (.gov) sites
- ✅ No copyright restrictions
- ✅ Legal to download and use for education/research
- ✅ No license agreements needed

### Documents are Current (as of May 2026)
- ✅ Washington RCW 82.08.809 - Active
- ✅ AFDC updated August 2025
- ✅ IRA credits valid until Sept 30, 2025
- ✅ NEVI program active (IIJA through Sept 2026)
- ✅ Washington ZEV mandate (2035 target)

### Alternative: If Downloads Fail
If any link doesn't work:
1. Go to the main government website
2. Use site search (e.g., `site:energy.gov "clean vehicle credit"`)
3. Or contact the agency directly

---

## 📞 Support Contacts

If you can't find a document:

| Document | Contact |
|----------|---------|
| WA RCW 82.08.809 | Washington State Legislature: 1-800-562-6000 |
| AFDC Incentives | DOE Technical Response: (800) 254-6735 |
| IRA Tax Credits | IRS: (800) 829-1040 |
| NEVI Program | FHWA: https://highways.dot.gov/contact |
| ZEV Mandate | WA Ecology: (360) 407-6000 |

---

**Status:** Ready to download  
**Last Updated:** May 1, 2026
