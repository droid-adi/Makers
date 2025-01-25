from flask import Flask, render_template, request, redirect, url_for, flash
import os
import PyPDF2
import csv
import re
from werkzeug.utils import secure_filename
# import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret key
UPLOAD_FOLDER = "uploads"
CSV_FOLDER = "csv_output"
GRAPH_FOLDER = "static/graphs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_FOLDER, exist_ok=True)
os.makedirs(GRAPH_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CSV_FOLDER"] = CSV_FOLDER
app.config["GRAPH_FOLDER"] = GRAPH_FOLDER


def parse_transactions(text):
    lines = text.split("\n")
    transactions = []
    current_transaction = {}

    for line in lines:
        line = line.replace("Sept", "Sep")
        if re.match(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{2}, \d{4}", line):
            if current_transaction:
                transactions.append(current_transaction)
            current_transaction = {"Date": line.strip()}
        elif "DEBIT" in line or "CREDIT" in line:
            current_transaction["Type"] = "DEBIT" if "DEBIT" in line else "CREDIT"
        elif "₹" in line:  # Matches the rupee symbol
            match = re.search(r"₹(\d+)", line)
            current_transaction["Amount"] = match.group(1) if match else "0"
        elif "Transaction ID" in line:
            current_transaction["Transaction_ID"] = line.split("Transaction ID")[-1].strip()
        elif re.match(r"[A-Z0-9]{20,}", line):
            current_transaction["Transaction_ID"] = line
        elif "UTR No." in line:
            current_transaction["UTR_No"] = line.split("UTR No.")[-1].strip()
        elif "Paid by" in line or "Credited to" in line:
            current_transaction["Paid_Credited_Info"] = line.strip()
        elif any(keyword in line for keyword in ["Mobile recharged", "Paid to", "Received from", "Payment"]):
            current_transaction["Details"] = line.strip()

    if current_transaction:
        transactions.append(current_transaction)

    for transaction in transactions:
        transaction.setdefault("Date", "")
        transaction.setdefault("Details", "")
        transaction.setdefault("Type", "")
        transaction.setdefault("Amount", "0")
        transaction.setdefault("Transaction_ID", "")
        transaction.setdefault("UTR_No", "")
        transaction.setdefault("Paid_Credited_Info", "")

    return transactions


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)

        final_balance = request.form.get("final_balance", type=float)

        if  final_balance is None:
            flash("Please provide the final balance.")
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            try:
                with open(file_path, "rb") as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = "".join(page.extract_text() for page in pdf_reader.pages)

                transactions = parse_transactions(text)
                csv_file_path = os.path.join(app.config["CSV_FOLDER"], f"{os.path.splitext(filename)[0]}.csv")
                with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
                    fieldnames = ["Date", "Details", "Type", "Amount", "Transaction_ID", "UTR_No", "Paid_Credited_Info"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(transactions)

            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
               

            df = pd.DataFrame(transactions)
            df["Date"] = pd.to_datetime(df["Date"], format="%b %d, %Y", errors="coerce")
            df = df.dropna(subset=["Date"])
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
            df["Amount"] = df.apply(lambda x: -x["Amount"] if x["Type"] == "DEBIT" else x["Amount"], axis=1)
            df = df.sort_values("Date")
            net_transactions = df["Amount"].sum()

            
            initial_balance = final_balance - net_transactions

            df["Balance"] = df["Amount"].cumsum() + initial_balance

            balance_trend_data = {
                "dates": df["Date"].dt.strftime("%Y-%m-%d").tolist(),
                "balances": df["Balance"].tolist(),
            }

            df["Month"] = df["Date"].dt.to_period("M")
            monthly_summary = df.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)
            monthly_summary.index = monthly_summary.index.astype(str)
            monthly_data = monthly_summary.to_dict("index")

            grouped_transactions = defaultdict(list)
            for transaction in transactions:
                try:
                    month = datetime.strptime(transaction['Date'], '%b %d, %Y').strftime('%B %Y')
                    grouped_transactions[month].append(transaction)
                except ValueError:
                    pass

            return render_template(
                "transactions.html",
                transactions=transactions,
                csv_file=os.path.basename(csv_file_path),
                monthly_data=monthly_data,
                balance_trend_data=balance_trend_data,
                grouped_transactions=grouped_transactions
            )
            

    return render_template("upload.html")

@app.route("/download/<filename>")
def download_csv(filename):
    return redirect(url_for("static", filename=f"csv_output/{filename}", _external=True))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
