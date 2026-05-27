import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from modules.db import (
    create_transactions_table,
    add_transaction,
    add_multiple_transactions,
    get_all_transactions,
    delete_transaction, 
    update_transaction 
)


# --------------------------------------------------
# Page settings
# --------------------------------------------------
st.set_page_config(
    page_title="Finance Data Analyzer",
    page_icon="💰",
    layout="wide"
)


# --------------------------------------------------
# Database initialization
# --------------------------------------------------
create_transactions_table()


# --------------------------------------------------
# Helper functions
# --------------------------------------------------
def prepare_dataframe(df):
    """
    Prepares the transactions dataframe for analysis.
    Converts the date column to datetime format.
    """
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)
    df["day_name"] = df["date"].dt.day_name()

    return df


def calculate_metrics(df):
    """
    Calculates the main financial metrics.
    """
    if df.empty:
        return 0, 0, 0, 0

    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expenses = df[df["type"] == "Expense"]["amount"].sum()
    balance = total_income - total_expenses

    if total_income > 0:
        saving_rate = (balance / total_income) * 100
    else:
        saving_rate = 0

    return total_income, total_expenses, balance, saving_rate

def apply_date_filter(df):
    """
    Applies a date filter to the transactions dataframe using the sidebar.
    """
    if df.empty:
        return df

    st.sidebar.header("Date Filter")

    filter_option = st.sidebar.selectbox(
        "Select period",
        ["All Data", "This Month", "Last Month", "Last 3 Months", "Custom Range"]
    )

    today = pd.Timestamp.today()
    current_month_start = today.replace(day=1)

    if filter_option == "All Data":
        return df

    elif filter_option == "This Month":
        return df[df["date"] >= current_month_start]

    elif filter_option == "Last Month":
        last_month_end = current_month_start - pd.Timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        return df[
            (df["date"] >= last_month_start) &
            (df["date"] <= last_month_end)
        ]

    elif filter_option == "Last 3 Months":
        three_months_ago = today - pd.DateOffset(months=3)

        return df[df["date"] >= three_months_ago]

    elif filter_option == "Custom Range":
        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        start_date = st.sidebar.date_input(
            "Start date",
            value=min_date
        )

        end_date = st.sidebar.date_input(
            "End date",
            value=max_date
        )

        return df[
            (df["date"].dt.date >= start_date) &
            (df["date"].dt.date <= end_date)
        ]

    return df
# --------------------------------------------------
# App title
# --------------------------------------------------
st.title("Finance Data Analyzer")

st.write("""
Manage your income and expenses, analyse your financial data, 
and understand your spending habits.
""")


# --------------------------------------------------
# Load data
# --------------------------------------------------
all_transactions_df = get_all_transactions()
all_transactions_df = prepare_dataframe(all_transactions_df)

transactions_df = apply_date_filter(all_transactions_df)

total_income, total_expenses, balance, saving_rate = calculate_metrics(transactions_df)

# --------------------------------------------------
# Navigation tabs
# --------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Dashboard",
    "Add Transaction",
    "Transactions",
    "Analytics",
    "Import / Analyze File"
])


# --------------------------------------------------
# Dashboard tab
# --------------------------------------------------
with tab1:
    st.subheader("Financial Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Income", f"€{total_income:,.2f}")
        st.caption("The values below are based on the selected date filter.")

    with col2:
        st.metric("Total Expenses", f"€{total_expenses:,.2f}")

    with col3:
        st.metric("Balance", f"€{balance:,.2f}")

    with col4:
        st.metric("Saving Rate", f"{saving_rate:.1f}%")

    st.divider()

    if transactions_df.empty:
        st.info("No transactions have been added yet.")
    else:
        expenses_df = transactions_df[transactions_df["type"] == "Expense"]
        income_df = transactions_df[transactions_df["type"] == "Income"]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Expenses by Category")

            if expenses_df.empty:
                st.info("No expenses available yet.")
            else:
                category_expenses = (
                    expenses_df
                    .groupby("category", as_index=False)["amount"]
                    .sum()
                    .sort_values(by="amount", ascending=False)
                )

                fig = px.pie(
                    category_expenses,
                    names="category",
                    values="amount",
                    title="Expense Distribution by Category"
                )

                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Monthly Income vs Expenses")

            monthly_summary = (
                transactions_df
                .groupby(["month", "type"], as_index=False)["amount"]
                .sum()
            )

            fig = px.bar(
                monthly_summary,
                x="month",
                y="amount",
                color="type",
                barmode="group",
                title="Monthly Income and Expenses"
            )

            st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Add transaction tab
# --------------------------------------------------
with tab2:
    st.subheader("Add New Transaction")

    with st.form("transaction_form"):
        col1, col2 = st.columns(2)

        with col1:
            transaction_date = st.date_input("Date", value=date.today())
            transaction_type = st.selectbox("Type", ["Income", "Expense"])
            amount = st.number_input("Amount (€)", min_value=0.01, step=0.50)

        with col2:
            category = st.text_input(
                "Category",
                placeholder="e.g. Salary, Food, Fuel, Rent"
            )

            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "Card", "Bank Transfer", "Other"]
            )

            description = st.text_area(
                "Description",
                placeholder="Optional notes..."
            )

        submitted = st.form_submit_button("Save Transaction")

        if submitted:
            if category.strip() == "":
                st.error("Please enter a category.")
            else:
                add_transaction(
                    str(transaction_date),
                    transaction_type,
                    category.strip(),
                    amount,
                    payment_method,
                    description.strip()
                )

                st.success("Transaction saved successfully.")
                st.rerun()


# --------------------------------------------------
# Transactions tab
# --------------------------------------------------
with tab3:
    st.subheader("All Transactions")

    if transactions_df.empty:
        st.info("No transactions have been added yet.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_type = st.selectbox(
                "Filter by Type",
                ["All", "Income", "Expense"]
            )

        with col2:
            categories = ["All"] + sorted(transactions_df["category"].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories)

        with col3:
            payment_methods = ["All"] + sorted(transactions_df["payment_method"].unique().tolist())
            selected_payment = st.selectbox("Filter by Payment Method", payment_methods)

        filtered_df = transactions_df.copy()

        if selected_type != "All":
            filtered_df = filtered_df[filtered_df["type"] == selected_type]

        if selected_category != "All":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]

        if selected_payment != "All":
            filtered_df = filtered_df[filtered_df["payment_method"] == selected_payment]

        st.dataframe(filtered_df, use_container_width=True)

        st.divider()

        st.subheader("Edit Transaction")

        with st.expander("Edit a selected transaction"):
            if filtered_df.empty:
                st.info("No transactions available to edit.")
            else:
                edit_transaction_id = st.selectbox(
                    "Select transaction ID to edit",
                    filtered_df["id"].tolist(),
                    key="edit_transaction_id"
                )

                transaction_to_edit = filtered_df[
                    filtered_df["id"] == edit_transaction_id
                ].iloc[0]

                with st.form("edit_transaction_form"):
                    col1, col2 = st.columns(2)

                    with col1:
                        edited_date = st.date_input(
                            "Date",
                            value=pd.to_datetime(transaction_to_edit["date"]).date(),
                            key="edited_date"
                        )

                        edited_type = st.selectbox(
                            "Type",
                            ["Income", "Expense"],
                            index=["Income", "Expense"].index(transaction_to_edit["type"]),
                            key="edited_type"
                        )

                        edited_amount = st.number_input(
                            "Amount (€)",
                            min_value=0.01,
                            step=0.50,
                            value=float(transaction_to_edit["amount"]),
                            key="edited_amount"
                        )

                    with col2:
                        edited_category = st.text_input(
                            "Category",
                            value=str(transaction_to_edit["category"]),
                            key="edited_category"
                        )

                        edited_payment_method = st.selectbox(
                            "Payment Method",
                            ["Cash", "Card", "Bank Transfer", "Other"],
                            index=(
                                ["Cash", "Card", "Bank Transfer", "Other"].index(transaction_to_edit["payment_method"])
                                if transaction_to_edit["payment_method"] in ["Cash", "Card", "Bank Transfer", "Other"]
                                else 3
                            ),
                            key="edited_payment_method"
                        )

                        edited_description = st.text_area(
                            "Description",
                            value=str(transaction_to_edit["description"]),
                            key="edited_description"
                        )

                    update_submitted = st.form_submit_button("Save Changes")

                    if update_submitted:
                        if edited_category.strip() == "":
                            st.error("Category cannot be empty.")
                        else:
                            update_transaction(
                                edit_transaction_id,
                                str(edited_date),
                                edited_type,
                                edited_category.strip(),
                                edited_amount,
                                edited_payment_method,
                                edited_description.strip()
                            )

                            st.success("Transaction updated successfully.")
                            st.rerun()
        
        st.divider()

        st.subheader("Delete Transaction")

        with st.expander("Delete a selected transaction"):
            if filtered_df.empty:
                st.info("No transactions available to delete.")
            else:
                transaction_ids = filtered_df["id"].tolist()

                selected_transaction_id = st.selectbox(
                    "Select transaction ID to delete",
                    transaction_ids
                )

                selected_transaction = filtered_df[
                    filtered_df["id"] == selected_transaction_id
                ]

                st.write("Selected transaction:")
                st.dataframe(selected_transaction, use_container_width=True)

                confirm_delete = st.checkbox(
                    "I confirm that I want to delete this transaction."
                )

                if st.button("Delete Selected Transaction"):
                    if confirm_delete:
                        delete_transaction(selected_transaction_id)
                        st.success("Transaction deleted successfully.")
                        st.rerun()
                    else:
                        st.warning("Please confirm before deleting the transaction.")


# --------------------------------------------------
# Analytics tab
# --------------------------------------------------
with tab4:
    st.subheader("Financial Analytics")

    if transactions_df.empty:
        st.info("No data available for analysis yet.")
    else:
        expenses_df = transactions_df[transactions_df["type"] == "Expense"]

        if expenses_df.empty:
            st.info("No expense data available yet.")
        else:
            average_expense = expenses_df["amount"].mean()
            highest_expense = expenses_df["amount"].max()
            number_of_expenses = len(expenses_df)

            top_category = (
                expenses_df
                .groupby("category")["amount"]
                .sum()
                .sort_values(ascending=False)
                .index[0]
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Average Expense", f"€{average_expense:,.2f}")

            with col2:
                st.metric("Highest Expense", f"€{highest_expense:,.2f}")

            with col3:
                st.metric("Number of Expenses", number_of_expenses)

            with col4:
                st.metric("Top Expense Category", top_category)

            st.divider()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Top Expense Categories")

                category_expenses = (
                    expenses_df
                    .groupby("category", as_index=False)["amount"]
                    .sum()
                    .sort_values(by="amount", ascending=False)
                )

                fig = px.bar(
                    category_expenses,
                    x="category",
                    y="amount",
                    title="Total Expenses per Category"
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Expenses Over Time")

                daily_expenses = (
                    expenses_df
                    .groupby("date", as_index=False)["amount"]
                    .sum()
                    .sort_values(by="date")
                )

                fig = px.line(
                    daily_expenses,
                    x="date",
                    y="amount",
                    markers=True,
                    title="Daily Expenses Trend"
                )

                st.plotly_chart(fig, use_container_width=True)

            st.divider()

            st.subheader("Automatic Insights")

            most_expensive_category_amount = (
                expenses_df
                .groupby("category")["amount"]
                .sum()
                .sort_values(ascending=False)
                .iloc[0]
            )

            expense_percentage = (most_expensive_category_amount / total_expenses) * 100

            st.write(
                f"Your highest spending category is **{top_category}**, "
                f"representing **{expense_percentage:.1f}%** of your total expenses."
            )

            st.write(
                f"Your average expense transaction is **€{average_expense:,.2f}**."
            )

            if balance > 0:
                st.success(
                    f"You currently have a positive balance of €{balance:,.2f}."
                )
            elif balance < 0:
                st.warning(
                    f"Your expenses are higher than your income by €{abs(balance):,.2f}."
                )
            else:
                st.info("Your income and expenses are currently equal.")

# --------------------------------------------------
# Import / Analyze Any File tab
# --------------------------------------------------
with tab5:
    st.subheader("Import and Analyze Any CSV or Excel File")

    st.write("""
    Upload any `.csv` or `.xlsx` file.  
    The app will automatically inspect the dataset without requiring predefined column names.
    """)

    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            # --------------------------------------------------
            # Load any CSV or Excel file
            # --------------------------------------------------
            if uploaded_file.name.endswith(".csv"):
                imported_df = pd.read_csv(
                    uploaded_file,
                    sep=None,
                    engine="python"
                )
            else:
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_name = st.selectbox(
                    "Select Excel sheet",
                    excel_file.sheet_names
                )
                imported_df = excel_file.parse(sheet_name)

            st.success("File loaded successfully.")

            # --------------------------------------------------
            # Basic dataset overview
            # --------------------------------------------------
            st.subheader("Dataset Overview")

            rows, columns = imported_df.shape
            duplicate_rows = imported_df.duplicated().sum()
            total_missing = imported_df.isnull().sum().sum()

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Rows", rows)

            with col2:
                st.metric("Columns", columns)

            with col3:
                st.metric("Missing Values", total_missing)

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Duplicate Rows", duplicate_rows)

            with col2:
                st.metric("File Type", uploaded_file.name.split(".")[-1].upper())

            st.divider()

            # --------------------------------------------------
            # Data preview
            # --------------------------------------------------
            st.subheader("Data Preview")
            st.dataframe(imported_df.head(100), use_container_width=True)

            # --------------------------------------------------
            # Column analysis
            # --------------------------------------------------
            st.subheader("Column Analysis")

            column_summary = pd.DataFrame({
                "Column": imported_df.columns,
                "Data Type": imported_df.dtypes.astype(str).values,
                "Missing Values": imported_df.isnull().sum().values,
                "Missing %": (
                    imported_df.isnull().sum().values / len(imported_df) * 100
                    if len(imported_df) > 0 else 0
                ),
                "Unique Values": imported_df.nunique(dropna=True).values
            })

            st.dataframe(column_summary, use_container_width=True)

            # --------------------------------------------------
            # Descriptive statistics
            # --------------------------------------------------
            st.subheader("Descriptive Statistics")

            numeric_columns = imported_df.select_dtypes(include=["number"]).columns.tolist()
            categorical_columns = imported_df.select_dtypes(include=["object", "category"]).columns.tolist()

            if numeric_columns:
                st.write("Numerical Columns")
                st.dataframe(
                    imported_df[numeric_columns].describe().T,
                    use_container_width=True
                )
            else:
                st.info("No numerical columns detected.")

            if categorical_columns:
                st.write("Categorical Columns")
                categorical_summary = imported_df[categorical_columns].describe().T
                st.dataframe(categorical_summary, use_container_width=True)
            else:
                st.info("No categorical columns detected.")

            st.divider()

            # --------------------------------------------------
            # Missing values chart
            # --------------------------------------------------
            st.subheader("Missing Values Analysis")

            missing_data = (
                imported_df
                .isnull()
                .sum()
                .reset_index()
            )

            missing_data.columns = ["Column", "Missing Values"]
            missing_data = missing_data[missing_data["Missing Values"] > 0]

            if missing_data.empty:
                st.success("No missing values detected.")
            else:
                fig = px.bar(
                    missing_data,
                    x="Column",
                    y="Missing Values",
                    title="Missing Values per Column"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # --------------------------------------------------
            # Automatic visual analysis
            # --------------------------------------------------
            st.subheader("Automatic Visual Analysis")

            if numeric_columns:
                selected_numeric = st.selectbox(
                    "Select numerical column for distribution",
                    numeric_columns
                )

                fig = px.histogram(
                    imported_df,
                    x=selected_numeric,
                    title=f"Distribution of {selected_numeric}"
                )

                st.plotly_chart(fig, use_container_width=True)

            if categorical_columns:
                selected_category = st.selectbox(
                    "Select categorical column for frequency analysis",
                    categorical_columns
                )

                category_counts = (
                    imported_df[selected_category]
                    .value_counts()
                    .head(20)
                    .reset_index()
                )

                category_counts.columns = [selected_category, "Count"]

                fig = px.bar(
                    category_counts,
                    x=selected_category,
                    y="Count",
                    title=f"Top Values in {selected_category}"
                )

                st.plotly_chart(fig, use_container_width=True)

            if len(numeric_columns) >= 2:
                st.subheader("Scatter Plot")

                x_axis = st.selectbox(
                    "Select X axis",
                    numeric_columns,
                    key="scatter_x"
                )

                y_axis = st.selectbox(
                    "Select Y axis",
                    numeric_columns,
                    key="scatter_y"
                )

                fig = px.scatter(
                    imported_df,
                    x=x_axis,
                    y=y_axis,
                    title=f"{x_axis} vs {y_axis}"
                )

                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Correlation Heatmap")

                correlation_matrix = imported_df[numeric_columns].corr()

                fig = px.imshow(
                    correlation_matrix,
                    text_auto=True,
                    title="Correlation Matrix"
                )

                st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # --------------------------------------------------
            # Optional finance transaction mapping
            # --------------------------------------------------
            st.subheader("Optional: Save This File as Finance Transactions")

            st.write("""
            If this file contains financial data, you can map its columns to the transaction fields below.
            This allows the app to save the uploaded data into the SQLite transactions database.
            """)

            with st.expander("Map columns to transaction fields"):
                all_columns = imported_df.columns.tolist()
                optional_columns = ["None"] + all_columns

                amount_column = st.selectbox(
                    "Amount column",
                    all_columns
                )

                date_column = st.selectbox(
                    "Date column",
                    optional_columns
                )

                type_column = st.selectbox(
                    "Type column",
                    optional_columns
                )

                category_column = st.selectbox(
                    "Category column",
                    optional_columns
                )

                payment_method_column = st.selectbox(
                    "Payment method column",
                    optional_columns
                )

                description_column = st.selectbox(
                    "Description column",
                    optional_columns
                )

                default_type = st.selectbox(
                    "Default transaction type",
                    ["Expense", "Income"]
                )

                default_category = st.text_input(
                    "Default category",
                    value="Imported"
                )

                default_payment_method = st.selectbox(
                    "Default payment method",
                    ["Other", "Cash", "Card", "Bank Transfer"]
                )

                if st.button("Save Mapped Data as Transactions"):
                    mapped_df = imported_df.copy()

                    # Amount handling
                    mapped_df["_amount"] = pd.to_numeric(
                        mapped_df[amount_column],
                        errors="coerce"
                    )

                    mapped_df = mapped_df.dropna(subset=["_amount"])

                    # Date handling
                    if date_column != "None":
                        mapped_df["_date"] = pd.to_datetime(
                            mapped_df[date_column],
                            errors="coerce"
                        ).dt.strftime("%Y-%m-%d")

                        mapped_df["_date"] = mapped_df["_date"].fillna(
                            str(date.today())
                        )
                    else:
                        mapped_df["_date"] = str(date.today())

                    # Type handling
                    if type_column != "None":
                        mapped_df["_type"] = (
                            mapped_df[type_column]
                            .astype(str)
                            .str.strip()
                            .str.lower()
                        )

                        mapped_df["_type"] = mapped_df["_type"].replace({
                            "income": "Income",
                            "credit": "Income",
                            "deposit": "Income",
                            "salary": "Income",
                            "expense": "Expense",
                            "debit": "Expense",
                            "withdrawal": "Expense",
                            "payment": "Expense"
                        })

                        mapped_df["_type"] = mapped_df["_type"].apply(
                            lambda value: value if value in ["Income", "Expense"] else default_type
                        )
                    else:
                        mapped_df["_type"] = mapped_df["_amount"].apply(
                            lambda value: "Expense" if value < 0 else default_type
                        )

                    # Store amount as positive value
                    mapped_df["_amount"] = mapped_df["_amount"].abs()

                    # Category handling
                    if category_column != "None":
                        mapped_df["_category"] = (
                            mapped_df[category_column]
                            .fillna(default_category)
                            .astype(str)
                            .str.strip()
                        )
                    else:
                        mapped_df["_category"] = default_category

                    # Payment method handling
                    if payment_method_column != "None":
                        mapped_df["_payment_method"] = (
                            mapped_df[payment_method_column]
                            .fillna(default_payment_method)
                            .astype(str)
                            .str.strip()
                        )
                    else:
                        mapped_df["_payment_method"] = default_payment_method

                    # Description handling
                    if description_column != "None":
                        mapped_df["_description"] = (
                            mapped_df[description_column]
                            .fillna("")
                            .astype(str)
                        )
                    else:
                        mapped_df["_description"] = ""

                    transactions = list(
                        mapped_df[
                            [
                                "_date",
                                "_type",
                                "_category",
                                "_amount",
                                "_payment_method",
                                "_description"
                            ]
                        ].itertuples(index=False, name=None)
                    )

                    add_multiple_transactions(transactions)

                    st.success(
                        f"{len(transactions)} transactions saved successfully."
                    )

                    st.rerun()

        except Exception as e:
            st.error("Something went wrong while reading or analysing the file.")
            st.exception(e)