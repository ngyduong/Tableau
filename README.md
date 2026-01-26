# Tableau Hyper API — Build Extracts Outside Tableau Cloud

Generate, control, and publish Tableau `.hyper` extracts **outside Tableau Cloud** to overcome performance, scalability, and reliability limits of classic extract refreshes.


---

## Why use the Hyper API

Tableau Cloud extract refreshes work well for small datasets, but they quickly become a bottleneck when:

- datasets grow large
- refreshes take too long or fail

This project shows how to **build Hyper extracts programmatically**, then **publish them to Tableau Cloud**, instead of relying on Tableau to generate them.

---

## Classic extracts vs Hyper API

### Classic Tableau extract limitations

| Limitation | Description |
|-----------|-------------|
| Limited control | No control over batching, ordering, or ingestion strategy |
| Performance issues | Slow or failing refreshes on large datasets |
| Poor observability | Limited logs and difficult debugging |
| Tight coupling | Requires access to source systems |

---

### What the Hyper API enables

| Feature | Hyper API |
|------|-----------|
| Ingestion control | Full control over how data is loaded |
| Performance | Optimized bulk ingestion |
| Observability | Logs, metrics, explicit failures |
| Integration | Works with Python, Spark, Parquet, CI/CD |

---

## Hyper API–based extract architecture

```text
┌──────────────────────────────┐
│ Data source / Data Lake      │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Data pipeline                │
│ (Python / Spark / Parquet)   │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ .hyper file                  │
│ (Hyper API)                  │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Tableau Cloud                │
│ (publish only)               │
└───────────────┬──────────────┘
                ↓
┌──────────────────────────────┐
│ Dashboard                    │
└──────────────────────────────┘
```

#### What this repository demonstrates
- Generating .hyper files using the Tableau Hyper API
- Loading data efficiently via Parquet
- Append vs replace extract strategies
- Publishing Hyper files to Tableau Cloud
- Running extract logic outside Tableau
- Logging and controlling the full extract lifecycle

### Requirements

#### Python
This project requires Python 3.14.
```markdownn
pyenv install 3.14.0
pyenv local 3.14.0
```

#### Dependency management

All dependencies are managed with Poetry.

Install Poetry
```markdownn
curl -sSL https://install.python-poetry.org | python3 -
```

Install project dependencies
```markdownn
poetry install
```

### Configuration

Set the following environment variables
```markdownn
export tab_pat_name="your_pat_name"
export tab_secret_id="your_pat_secret"
export tab_site_id="your_site_id"
export tab_site_url="https://your-site.tableau.com"
export tab_api_version="3.21"
```

### Usage

#### Generate a Hyper file

```markdownn
poetry run python main.py --script generate_hyper
```
This step:
- extracts source data
- exports it to Parquet
- builds a .hyper file using the Hyper API

#### Publish the Hyper file to Tableau Cloud

```markdownn
poetry run python main.py --script publish_hyper
```
This step:
- authenticates using a Tableau Personal Access Token
- publishes the Hyper file to Tableau Cloud
- overwrites or appends depending on configuration

### Typical workflow

1.	Extract data from source systems
2.	Transform and validate data
3.	Export data to Parquet
4.	Generate .hyper using Hyper API
5.	Publish to Tableau Cloud
6.	Visualize in dashboards

### Best practices
- Use Parquet as an intermediate format
- Validate data before generating Hyper files
- Treat Hyper files as deployable artifacts
- Publish only after successful generation

---

## ⚠️ Important limitation: SQL compute on Tableau Cloud extracts

Even when using the Hyper API, it is important to understand that **Tableau Cloud still enforces SQL compute limits at query time**.

### The 20 GB SQL compute limit

On Tableau Cloud, **SQL compute is capped at ~20 GB per query**, regardless of:

- the size of the extract
- how the extract was generated
- whether it was built via classic refresh or Hyper API

This means that **publishing a very large extract (e.g. 50 GB, 80 GB, 100 GB)** does *not* remove this limitation.

### Impact on calculated fields

Certain operations are particularly expensive in terms of SQL compute, for example:

- `COUNT(DISTINCT ...)`
- high-cardinality aggregations
- complex calculated fields evaluated at query time
- LOD expressions over large dimensions

On large extracts, these calculations can:

- fail silently
- return errors
- never finish
- exceed the 20 GB SQL compute limit

Even though the extract exists and is published successfully.


### Why this happens

- Hyper API optimizes **data ingestion**
- Tableau Cloud still controls **query execution**
- Query-time calculations are executed within Tableau Cloud’s SQL compute limits

In short:

> **Hyper API solves extract generation problems, not query-time compute limits.**

### Recommended approach for very large datasets

If your use case requires:

- very large datasets (tens or hundreds of GB)
- heavy aggregations
- `COUNT DISTINCT` on high-cardinality columns
- complex analytical logic

Then **a Live connection is often the better option**, because:

- compute is pushed down to the source system
- databases / warehouses scale compute elastically
- Tableau Cloud only renders results


### Practical rule of thumb

| Use case | Recommended approach |
|--------|----------------------|
| Large data, simple aggregations | Hyper extract |
| Large data + complex calculations | Live connection |
| Heavy `COUNT DISTINCT` | Live connection |
| High-cardinality dimensions | Live connection |
| Pre-aggregated / curated data | Hyper extract |


### Best practice

If you want to keep using extracts on large datasets:

- pre-aggregate data **before** generating the extract
- avoid `COUNT DISTINCT` in Tableau
- materialize metrics upstream
- reduce cardinality where possible

Otherwise, prefer **Live connections** for analytical workloads that exceed Tableau Cloud’s SQL compute limits.

> **Hyper API is powerful — but it does not replace the need for a scalable compute engine.**