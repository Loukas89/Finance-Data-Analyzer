# Finance Data Analyzer

## Live Demo

The application is deployed and available online here:

https://finance-data-analyzer-tpb9quxg6isxesyjdk72sx.streamlit.app

---

## Project Overview

**Finance Data Analyzer** is a Python-based web application built with Streamlit for managing, analysing, importing, exporting, and reporting personal financial data.

The application allows users to record income and expense transactions, view financial summaries, analyse spending behaviour, import CSV and Excel files, detect unusual expenses, and generate financial reports for different time periods.

The main goal of this project is to combine **personal finance management** with **data analysis and visualisation**, creating a practical dashboard that helps users understand their financial activity in a clear and interactive way.

---

## Main Features

### 1. Income and Expense Management

Users can manually add financial transactions through a simple form.

Each transaction includes:

* Date
* Transaction type: Income or Expense
* Category
* Amount
* Payment method
* Description

Transactions are stored locally in an SQLite database.

---

### 2. Dashboard Overview

The dashboard provides a quick summary of the selected financial period.

It includes:

* Total income
* Total expenses
* Net balance
* Saving rate
* Expenses by category
* Monthly income vs expenses

The dashboard gives users a fast overview of their financial position.

---

### 3. Transactions Management

The Transactions section allows users to view and manage all saved transactions.

Available functionality includes:

* View all transactions in a table
* Filter transactions by:

  * Type
  * Category
  * Payment method
* Search transactions by:

  * Category
  * Payment method
  * Description
  * Transaction type
* Edit existing transactions
* Delete a selected transaction
* Delete all transactions with confirmation
* Export filtered transactions to CSV
* Export filtered transactions to Excel

This provides full CRUD functionality:

| Operation | Description                    |
| --------- | ------------------------------ |
| Create    | Add a new transaction          |
| Read      | View saved transactions        |
| Update    | Edit an existing transaction   |
| Delete    | Delete one or all transactions |

---

### 4. Category Selection

The application uses predefined transaction categories to make data entry faster and more consistent.

Available categories include:

* Salary
* Food
* Fuel
* Rent
* Bills
* Shopping
* Entertainment
* Coffee
* Health
* Transport
* Subscriptions
* Education
* Travel
* Other

Using dropdown categories helps reduce typing mistakes and improves the quality of financial analysis.

---

### 5. CSV and Excel Import

The application supports importing external data files.

Supported file types:

* `.csv`
* `.xlsx`

The import feature is flexible and does not require files to have predefined column names.

When a file is uploaded, the application performs automatic analysis, including:

* Dataset preview
* Number of rows and columns
* Column data types
* Missing values
* Duplicate rows
* Unique values per column
* Descriptive statistics
* Basic visual analysis

If the uploaded file contains financial data, users can optionally map its columns to transaction fields and save the data into the SQLite database.

---

### 6. Data Analysis

The Analytics section provides deeper insights into expenses.

Current analytics include:

* Average expense
* Highest expense
* Number of expense transactions
* Top expense category
* Total expenses per category
* Daily expenses trend
* Automatic financial insights

The application helps users identify where most of their money is spent and how expenses change over time.

---

### 7. Outlier Detection

The application includes an outlier detection feature for identifying unusual expense transactions.

The method used is the **IQR method**.

IQR stands for **Interquartile Range** and is calculated as:

```text
IQR = Q3 - Q1
```

The application calculates expected lower and upper boundaries:

```text
Lower Bound = Q1 - 1.5 * IQR
Upper Bound = Q3 + 1.5 * IQR
```

Any expense outside this range may be marked as unusual.

The outlier detection checks:

* Category-level outliers
* Global expense outliers

For each detected outlier, the app displays:

* Transaction ID
* Date
* Category
* Amount
* Payment method
* Description
* Outlier method
* Expected range
* Reason

This helps users detect unusually high or suspicious expenses.

---

### 8. Date Filtering

The application includes sidebar date filters that affect the displayed dashboard and analytics.

Available filters include:

* All Data
* This Month
* Last Month
* Last 3 Months
* Custom Range

This allows users to analyse specific time periods instead of always viewing all transactions together.

---

### 9. Financial Reports

The Reports section allows users to generate financial reports for different time periods.

Available report periods:

* Weekly
* 15 Days
* Monthly
* 3 Months
* 6 Months
* 1 Year
* 2 Years

Each report includes:

* Total income
* Total expenses
* Balance
* Saving rate
* Top expense categories
* Income vs expenses chart
* Automatic insights
* Transactions included in the report

Reports can be downloaded as:

* HTML report
* CSV report data

The HTML report can also be opened in a browser and saved as a PDF using the browser print option.

On macOS:

```bash
Command + P
```

Then select:

```text
Save as PDF
```

---

## Technologies Used

This project was built using the following technologies:

| Technology | Purpose                              |
| ---------- | ------------------------------------ |
| Python     | Main programming language            |
| Streamlit  | Web application framework            |
| Pandas     | Data processing and analysis         |
| NumPy      | Numerical operations                 |
| Plotly     | Interactive data visualisations      |
| SQLite     | Local database storage               |
| OpenPyXL   | Excel file support                   |
| HTML/CSS   | Custom styling and report generation |

---

## Project Structure

```text
Finance Data Analyzer/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── assets/
│   └── style.css
│
├── modules/
│   ├── __init__.py
│   └── db.py
│
└── database/
    └── .gitkeep
```

### File Descriptions

| File / Folder       | Description                            |
| ------------------- | -------------------------------------- |
| `app.py`            | Main Streamlit application file        |
| `requirements.txt`  | Python dependencies                    |
| `README.md`         | Project documentation                  |
| `.gitignore`        | Files and folders excluded from GitHub |
| `assets/style.css`  | Custom CSS styling                     |
| `modules/db.py`     | Database functions                     |
| `database/.gitkeep` | Keeps the database folder in GitHub    |

---

## Database

The application uses SQLite for local data storage.

The database file is created automatically when the application runs:

```text
database/finance.db
```

The main table is:

```text
transactions
```

The transactions table stores:

| Column         | Description                      |
| -------------- | -------------------------------- |
| id             | Unique transaction ID            |
| date           | Transaction date                 |
| type           | Income or Expense                |
| category       | Transaction category             |
| amount         | Transaction amount               |
| payment_method | Payment method used              |
| description    | Optional transaction description |

---

## Data Privacy

The SQLite database file is not uploaded to GitHub.

This file is excluded using `.gitignore`:

```gitignore
database/finance.db
*.db
*.sqlite3
```

This means:

* The source code is stored on GitHub
* Personal financial data stays local
* The deployed demo should be used mainly for demonstration purposes

For production use, a proper external database such as PostgreSQL or Supabase would be recommended.

---

## Installation and Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Loukas89/finance-data-analyzer.git
```

### 2. Navigate into the Project Folder

```bash
cd finance-data-analyzer
```

### 3. Create a Virtual Environment

```bash
python3 -m venv venv
```

### 4. Activate the Virtual Environment

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python3 -m streamlit run app.py
```

The application will open in the browser at:

```text
http://localhost:8501
```

---

## Requirements

The main dependencies are:

```txt
streamlit
pandas
numpy
plotly
openpyxl
```

---

## How to Use the Application

### Dashboard

Use the Dashboard tab to get a quick overview of your finances.

It displays:

* Total income
* Total expenses
* Balance
* Saving rate
* Expense charts
* Monthly comparisons

---

### Add Transaction

Use the Add Transaction tab to manually add income or expense records.

Steps:

1. Select the date
2. Choose Income or Expense
3. Select a category
4. Enter the amount
5. Select a payment method
6. Add an optional description
7. Save the transaction

---

### Transactions

Use the Transactions tab to manage existing records.

You can:

* Search transactions
* Filter transactions
* Edit a transaction
* Delete a transaction
* Delete all transactions
* Export transactions to CSV
* Export transactions to Excel

---

### Analytics

Use the Analytics tab to understand spending behaviour.

It includes:

* Average expense
* Highest expense
* Top expense category
* Category charts
* Expense trend charts
* Outlier detection

---

### Import and Analyze

Use the Import and Analyze tab to upload CSV or Excel files.

The app will automatically analyse the uploaded file and display:

* Preview
* Dataset overview
* Missing values
* Column types
* Descriptive statistics
* Visualisations

If the file contains financial transactions, users can map columns and save the data into the database.

---

### Reports

Use the Reports tab to generate financial reports.

Supported periods:

* Weekly
* 15 Days
* Monthly
* 3 Months
* 6 Months
* 1 Year
* 2 Years

Reports can be downloaded as:

* HTML
* CSV

---

## Deployment

The application is deployed using Streamlit Community Cloud.

Live demo:

```text
https://finance-data-analyzer-tpb9quxg6isxesyjdk72sx.streamlit.app
```

The app is deployed from the GitHub repository using:

```text
Branch: main
Main file path: app.py
```

---

## Current Limitations

The current version has some limitations:

* SQLite is used locally and is not ideal for multi-user cloud storage
* No login system is currently implemented
* Report PDF export is not directly implemented yet
* The UI is still based on Streamlit components
* Data entered in the online demo should not be considered permanent production data

---

## Purpose of the Project

This project was developed as a practical data analysis and finance management application.

It demonstrates skills in:

* Python programming
* Data analysis
* Data visualisation
* Database management
* Streamlit app development
* CRUD operations
* CSV and Excel processing
* Financial analytics
* Report generation
* GitHub version control
* Web app deployment

---

## Author

**Loukas Theos**

GitHub: [Loukas89](https://github.com/Loukas89)

---

## License

This project is currently intended for educational and portfolio purposes.
