import sqlite3
import pandas as pd


DB_PATH = "database/finance.db"


def get_connection():
    """
    Creates and returns a connection to the SQLite database.
    """
    return sqlite3.connect(DB_PATH)


def create_transactions_table():
    """
    Creates the transactions table if it does not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_transaction(date, transaction_type, category, amount, payment_method, description):
    """
    Adds a new income or expense transaction to the database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions 
        (date, type, category, amount, payment_method, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, transaction_type, category, amount, payment_method, description))

    conn.commit()
    conn.close()


def add_multiple_transactions(transactions):
    """
    Adds multiple transactions to the database.
    Each transaction must be a tuple:
    (date, type, category, amount, payment_method, description)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO transactions 
        (date, type, category, amount, payment_method, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, transactions)

    conn.commit()
    conn.close()


def get_all_transactions():
    """
    Returns all transactions as a pandas DataFrame.
    """
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT 
            id,
            date,
            type,
            category,
            amount,
            payment_method,
            description
        FROM transactions
        ORDER BY date DESC, id DESC
    """, conn)

    conn.close()
    return df


def delete_transaction(transaction_id):
    """
    Deletes one transaction from the database based on its ID.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM transactions
        WHERE id = ?
    """, (transaction_id,))

    conn.commit()
    conn.close()