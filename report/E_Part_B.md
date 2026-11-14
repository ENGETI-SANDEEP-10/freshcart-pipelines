# Part B — FreshCart ELT on Snowflake

## B1. Baseline Pipeline Execution

The FreshCart pipeline follows **Extract → Load → Transform → Check**. Sample API data is extracted into raw files, loaded into Snowflake Bronze using `PUT` and `COPY INTO`, transformed into Silver and Gold tables, and validated through `quality_checks()`.

The baseline execution produced:

| Metric | Observed result |
|---|---:|
| Bronze raw order rows | 8 |
| Silver clean rows | 6 |
| Quarantined rows | 2 |
| Orders after deduplication | 4 |
| Gold orders | 4 |
| Gold revenue | ₹7,785.00 |
| Total loyalty points | 126 |
| Rejected-row percentage | 25% |

The rejected records were `ORD-1004` and `ORD-1006`. These values describe the initial baseline, before subsequent experiments changed the customer history.

**Evidence:** `B1_FreshCart_Baseline.png`, `B1_Layer_Row_Counts.png`.

## B2. Tracing Orders Through the Pipeline

### ORD-1003 — Web and Mobile Records

`ORD-1003` appears twice in `bronze.orders_raw`:

- **Web copy:** Uses fields such as `order_id`, `cust_email`, `order_date`, `amount`, and `updated_at`. Its amount is missing.
- **Mobile copy:** Uses `orderId`, `customer.email`, `orderDate`, `total.value`, and `updatedAt`. Its amount is ₹2,100, and its update timestamp is later.

The APIs use different naming conventions and nesting structures, so `SQL_10_ORDERS_CLEAN` maps both schemas into common columns in `silver.orders_checked`. It uses expressions including `LOWER(TRIM(...))` for email normalization, `COALESCE(TRY_TO_DATE(...))` for date parsing, `TRY_TO_DECIMAL(REGEXP_REPLACE(...))` for amount conversion, and `TRY_TO_TIMESTAMP_NTZ(...)` for update timestamps.

`SQL_20_ORDERS_DEDUP` retains one record per order using:

```sql
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY order_id
    ORDER BY updated_at DESC, ingest_seq DESC
) = 1
```

The newer mobile record survives, with an amount of ₹2,100.

Gold enrichment calculates:

- `amount_inr = ROUND(2100 × 1, 2) = ₹2,100`
- Customer tier: Platinum; multiplier: 3
- `loyalty_points = FLOOR(2100 / 100) × 3 = 63`

### ORD-1005 — Historical Customer Tier

Priya's tier changes over time, so her order-date tier determines her loyalty points:

| Order | Tier on order date | Amount (INR) | Multiplier | Points |
|---|---|---:|---:|---:|
| `ORD-1001` | Silver | ₹1,250 | 1 | 12 |
| `ORD-1005` | Gold | ₹899 | 2 | 16 |

The responsible table is `dim.customers_scd2`. The point-in-time join in `SQL_40_GOLD` uses:

```sql
ON c.email = o.email
AND o.order_date BETWEEN c.valid_from AND c.valid_to
```

This ensures orders retain the tier that applied when they occurred, rather than applying the customer's current tier to all historical transactions.

## B3. Unsupported-Currency Validation

A new validation condition was added to `SQL_10_ORDERS_CLEAN` inside `ARRAY_CONSTRUCT_COMPACT(...)`, rejecting currencies other than INR and USD.

For `ORD-1006`, the validation reasons changed:

| Before | After |
|---|---|
| `bad_email`, `bad_pincode` | `bad_email`, `bad_pincode`, `unsupported_currency` |

The Gold revenue total remained unchanged because `ORD-1006` was already invalid and excluded from the clean and Gold datasets.

A second quarantine row was not added for the same record version. The quarantine insertion uses `NOT EXISTS` to check whether a matching source, order ID, and update timestamp have already been quarantined. A `QUALIFY ROW_NUMBER()` condition also avoids inserting duplicate versions within the same batch.

**Evidence:** `B3_ORD1006_Reasons_Before.png`, `B3_ORD1006_Reasons_After.png`, `B3_Gold_Totals_After_Validation.png`.

## B4. SCD Type 2 Change and Idempotency

A new CRM event changed Arjun (`CUST-02`) to Gold effective **15 August 2026**.

The predictions were compared against the subsequent pipeline results:

| Quantity | Predicted | Actual |
|---|---|---|
| `CUST-02` SCD2 rows | 2 | 2 |
| Tier for `ORD-1002` | Gold | Gold |
| Points for `ORD-1002` | 70 | 70 |
| Total Gold loyalty points | 161 | 161 |
| Gold rows with changed `published_at` | 1 | 1 |

For `ORD-1002`, USD 42.50 was converted using an FX rate of 83.2:

`amount_inr = 42.50 × 83.2 = ₹3,536`

With Gold multiplier 2:

`loyalty_points = FLOOR(3536 / 100) × 2 = 70`

Previously, the Silver multiplier gave 35 points. Thus total loyalty points increased from **126 to 161** without changing revenue.

**Idempotency:** Each Gold row contains a `row_hash` computed from its business values. The `MERGE` matches rows by `order_id` and updates an existing row only when its new hash differs from the stored hash. Therefore, unchanged reruns preserve `published_at`, whereas a genuine tier or points change updates the relevant Gold row. New orders are inserted through the `WHEN NOT MATCHED` branch. Bronze, however, is an append-oriented raw layer and receives eight new ingested rows on each normal rerun, preserving ingestion history without multiplying the four distinct Gold orders.

**Evidence:** `B4_Arjun_SCD2_History.png`, `B4_ORD1002_After_Tier_Change.png`, `B4_Idempotent_Timestamps.png`.

## B5. Additional Data-Quality Check and ELT versus ETL

A sixth quality check was added to detect **future-dated orders in `silver.orders_dedup`**.

A temporary test order, `ORD-B5-FUTURE`, with order date `2099-01-01`, was introduced deliberately. The new check returned:

`orders with future order dates: 1 — PROBLEM`

The same experiment also exposed a missing-FX-rate warning for the future date. After the temporary record was removed and the pipeline was rerun, all six quality checks returned **0 — OK**. The final Gold table again contained four orders, ₹7,785 in revenue, and 161 loyalty points.

**ELT versus ETL:** ELT suits FreshCart because the source APIs have different schemas and the raw data must be preserved for investigation and reprocessing. Loading first allows Snowflake to perform SQL normalization, validation, deduplication, and historical enrichment centrally. It also makes it easier to add new validation rules without repeatedly extracting source data. Traditional ETL is preferable when sensitive information must be masked or removed before it enters the destination warehouse.

**Evidence:** `B5_Intentional_Quality_Failure.png`, `B5_Six_Quality_Checks_Passing.png`.