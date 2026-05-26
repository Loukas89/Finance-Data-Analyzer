import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from modules.db import (
    create_transactions_table,
    add_transaction,
    get_all_transactions
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
transactions_df = get_all_transactions()
transactions_df = prepare_dataframe(transactions_df)

total_income, total_expenses, balance, saving_rate = calculate_metrics(transactions_df)


# --------------------------------------------------
# Navigation tabs
# --------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Dashboard",
    "Add Transaction",
    "Transactions",
    "Analytics"
])


# --------------------------------------------------
# Dashboard tab
# --------------------------------------------------
with tab1:
    st.subheader("Financial Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Income", f"€{total_income:,.2f}")

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