# Part B4 — Predictions Before Execution

**Student:** ENGETI SANDEEP  
**Roll Number:** 23BCS081  
**Course:** Data Engineering

## Proposed CRM Change

- Customer ID: CUST-02
- Customer: Arjun
- Email: arjun.k@yahoo.in
- New tier: Gold
- Effective from: 2026-08-15

## Predictions

| Quantity | My Prediction | Actual After Run |
|---|---|---|
| Rows for CUST-02 in dim.customers_scd2 | 2 | Not executed yet |
| Tier used for ORD-1002 | Gold | Not executed yet |
| Loyalty points for ORD-1002 | 70 | Not executed yet |
| Total loyalty points in Gold | 161 | Not executed yet |
| Number of Gold rows whose published_at changed | 1 | Not executed yet |

## Reasoning

**1. Customer history:** Arjun's original Silver record will remain in the SCD Type 2 table, ending on 2026-08-14. A new Gold record will begin on 2026-08-15, producing two historical records.

**2. ORD-1002 tier:** Since ORD-1002 was placed on 2026-09-01, after Arjun's Gold tier became effective, the order should use the Gold tier.

**3. Loyalty points:** ORD-1002 has an amount of USD 42.50 and an exchange rate of 83.20 INR per USD. Its INR value is ₹3,536.00. Using the Gold multiplier of 2, the order should earn FLOOR(3536 / 100) × 2 = 70 points.

**4. Total loyalty points:** The existing Gold total is 126 points, including 35 points for Arjun's order. Replacing those 35 points with 70 produces 126 − 35 + 70 = 161 total loyalty points.

**5. Published timestamp:** I predict that one Gold record will receive an updated published_at timestamp. The MERGE statement compares row_hash values, and only ORD-1002 should have changed calculated values because of the new customer tier.

## Execution Status

These predictions were prepared before adding the new CRM event and rerunning the FreshCart pipeline. Actual results will be recorded separately after execution.