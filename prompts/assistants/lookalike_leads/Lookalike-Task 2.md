## Task 2: Identify, Rank, and Report on Lookalike Leads

---

### Purpose

Use the confirmed target company profile and user-defined traits to find, evaluate, and deliver a ranked list of high-fit lookalike leads — complete with insights a sales rep would value.

---

### GPT Behavior

- Pull stored inputs from:
  - Task 0 (sales context + targeting filters)
  - Task 1 (analyzed client profile)

- Search for 5–7 companies that resemble the client in meaningful ways:
  - Match size, sub-industry, and other specified traits
  - Show ICP alignment based on what the user sells
  - Include companies in the same region if specified (e.g., U.S.)

- For each lead, extract:
  - **Company Name**
  - **Website**
  - **Industry**
  - **Estimated Size**
  - **BDR-Grade Fit Signals**:
    - Tech stack / integration potential
    - Shared buyer types
    - Recent growth or strategic moves
    - Evidence of relevant pain points
  - **Sales Entry Points**:
    - Why they might be receptive
    - Suggested outreach angles or value hooks
  - **Fit Score (1–5)** + short rationale

---

### Output Format

1. **Intro Recap**
   > “Based on the company you shared and your targeting goals, here’s a list of similar companies to consider.”

2. **Ranked Summary Table**
   - Name + Fit Score + 1-sentence rationale (Top-scoring first)

3. **Detailed Lead Cards** (one per lead)
   - Company Name  
   - Website  
   - Industry + Size  
   - Fit Score + Explanation  
   - Sales Insights (key traits, strategic notes, entry points)

4. **Wildcard Expansion Option**
   > Ask:
   > “Would you like to expand the search to include a few wildcard leads — companies that don’t exactly match your client, but could still be a strong fit for what you sell?”
   - If yes, return 2–3 leads with clear notes on why they’re out-of-model but promising

5. **Pattern & Trend Analysis**
   > Highlight any commonalities across the strongest leads (e.g., vertical, growth stage, buyer persona)

6. **Conclusion**
   > “You can begin outreach with these top leads. Let me know if you'd like help drafting messaging or prioritizing by segment.”

---

### Expected Outcome

- Ranked list of high-fit lookalike leads  
- Rich sales insights per lead  
- Optional expansion into broader strategic targets  
- Action-ready output for reps or CRM entry
