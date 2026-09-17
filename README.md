# Financeinator

Financeinator is a personal finance dashboard for reviewing imported transaction data, identifying spending patterns, and cleaning up transaction categorization before analysis.

The original idea behind this app was to import closed invoices exported from Nubank as CSV files, bring them into the app, and then review the spending patterns in a clearer and more useful way than the raw export gives you.

The project combines:

- a Python FastAPI backend that stores transactions, imports CSV files, and exposes transaction APIs
- a Dash + Plotly frontend that visualizes spending trends and allows category filtering
- an AI-assisted title mapping workflow that tries to categorize imported transaction titles and merchants

This is designed for users who want a quick way to upload bank or card exports, review their spending by month and category, and spot patterns in where money is going.

## What the app does

The dashboard helps you:

- upload CSV transaction files
- view recent spending totals and category summaries
- compare monthly trends across categories
- identify merchants and transaction types driving spend
- fix or improve title-to-category mappings before analysis
- drill into invoice items within a selected category and time window

The workflow is intentionally simple:

1. Upload a CSV file with transaction data.
2. Let the backend store and normalize the data.
3. Review the mapped transaction types and merchants.
4. Explore monthly, category, and merchant insights in the dashboard.

## Architecture

### Backend

The backend lives in `server_side/` and is built with FastAPI. It provides the APIs for:

- importing CSV files
- listing transactions
- listing title mappings
- saving title mappings

It also uses environment configuration values for the app name and the OpenAI settings used by the categorization services.

### Frontend

The frontend lives in `client_side/` and is built with Dash. It renders the dashboard screen, filter controls, KPI cards, and chart panels. All visual analysis is built from the transaction data returned by the backend.

## Dashboard sections and graph explanations

### Data Provision

This tab is used to bring transactions into the system.

- upload a CSV file
- review the title mapping table
- assign a type and merchant to titles when needed
- submit the mapping so later analysis uses the corrected values

This is the setup and cleanup stage before the spending analysis becomes meaningful.

### Data Analysis

This tab is the main reporting section. It gives you a high-level view of your spending patterns across time and categories.

#### Monthly Type Comparison

This chart compares how much was spent in each category across the selected months.

Use it to answer questions like:

- Are meals, groceries, or transport growing over time?
- Which categories are consistently the largest contributors?
- Has one type of spending changed materially compared with the others?

Each bar group represents a month, and each colored bar within the group represents a spending category.

#### Month-over-Month Change by Category

This chart shows how each category changed compared with the previous month.

It is useful for spotting short-term spikes or drops. For example:

- a category suddenly jumping upward in a given month
- a rapid reduction in one expense bucket
- which categories are driving monthly volatility

Positive values indicate spending increased compared with the prior month; negative values indicate a reduction.

#### Change vs Selected Month

This chart compares monthly spending across categories against a chosen baseline month.

It is helpful when you want to answer:

- how much higher or lower was spending this month compared with a reference month?
- which categories are trending up or down relative to a known baseline?

This is the broader “vs baseline” view, while the previous chart shows the more immediate move from one month to the next.

#### Daily Spend Comparison

This chart shows daily spending patterns within the selected recent months.

Use it to identify:

- spending spikes on certain dates
- patterns in week-to-week or month-to-month behavior
- whether a recent month looks unusually concentrated in a few days

Each line represents a month, and the points track spending by day of the month.

#### Top Spend Breakdown

This section includes the donut charts for:

- top merchants by spend
- top categories by spend

These charts help quickly identify the biggest spending drivers without digging through raw rows.

This is especially useful for seeing whether a small number of merchants or categories account for most of your total spending.

#### Invoice Items by Category

This table lists the individual transactions in the selected category and optional merchant filter.

It allows you to:

- inspect the actual titles and dates behind the summary numbers
- validate whether the category assignment is correct
- find unusual or outlier purchases
- narrow the data to a category or merchant for deeper review

## Project structure

```text
Financeinator/
├── client_side/
│   ├── src/
│   ├── requirements.txt
│   └── README.md (optional local frontend notes)
├── server_side/
│   ├── src/
│   ├── tests/
│   ├── .env.example
│   ├── .env
│   ├── requirements.txt
│   └── README.md
├── .gitignore
└── README.md
```

## Environment variables

Use the template in `server_side/.env.example` as the source of truth. Do not read or copy values from `.env` when setting up the project; instead, create your own local `.env` from the example.

The required variables are:

```env
APP_NAME=Financeinator API
API_PREFIX=/api/v1
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

### What each variable does

- `APP_NAME`: readable application name shown by the API metadata
- `API_PREFIX`: base API prefix for the FastAPI routes, defaulting to `/api/v1`
- `OPENAI_API_KEY`: API key used by the AI categorization services for transaction title/merchant classification
- `OPENAI_MODEL`: model name to use for the LLM-based categorization workflow

To configure it locally:

```bash
cd server_side
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Then fill in the empty values in `.env` with your real keys and settings.

## How to run the project

### 1) Create and activate a virtual environment

```bash
cd Financeinator
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 2) Install backend dependencies

```bash
cd server_side
python -m pip install -r requirements.txt
```

### 3) Configure environment variables

```bash
copy .env.example .env
```

Then edit `.env` and provide the correct values.

### 4) Start the backend

```bash
cd server_side
uvicorn server_side.main:app --app-dir src --reload
```

The API should be available at:

- http://127.0.0.1:8000/docs
- base API: http://127.0.0.1:8000/api/v1

### 5) Install frontend dependencies

Open a second terminal and run:

```bash
cd client_side
python -m pip install -r requirements.txt
```

### 6) Start the dashboard

```bash
cd client_side
python .\src\main.py
```

The app should open locally in the browser at:

- http://127.0.0.1:8150

## Typical usage flow

1. Start the backend.
2. Start the frontend.
3. Upload a CSV file in the Data Provision tab.
4. Review the title mapping table and correct any manual classifications.
5. Switch to Data Analysis.
6. Explore the chart panels and filter the data by month, category, or merchant.

## Notes

- The dashboard is intended for local personal finance analysis.
- CSV import and mapping logic is designed around transaction exports with common fields like date, title, and amount.
- The OpenAI key is only needed if you are using the categorization and mapping features that rely on the LLM-based classification services.

## Future ideas

Possible extensions for the project include:

- recurring expense detection
- budget tracking against historical spending
- multi-account rollups
- export to CSV or PDF reports
- dark mode and more premium dashboard themes
