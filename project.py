import sys
import csv
import re
from datetime import datetime, date
from tabulate import tabulate



def main():
    try:
        command = sys.argv[1]
    except IndexError:
        sys.exit("No command")

    if command == "add":
        add_expense()
    elif command == "view":
        view_expenses()
    elif command == "summary":
        summarize_expenses()
    elif command == "delete":
        delete_expense()
    elif command == "export":
        export_expenses()
    else:
        sys.exit("Invalid command")

def load_expenses():  #opens a csv file called expenses and checks if it exists from before or not
    try:
        with open ("expenses.csv", newline="") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        return list()

def get_next_id():   #assigns a number to an entry in the expense.csv
    expenses = load_expenses()
    if len(expenses) == 0:
        return 1
    else:
        highest = 0
        for e in expenses:
            if int(e["id"]) > highest:   #highest = max(int(e["id"]) for e in expenses)
                highest = int(e["id"])
        return highest + 1


def add_expense():   #adds list of expenses to the csv file
    while True:   #Checking date format
        date_str = input("Date: ")
        if date_str == "":
            date_str = date.today().strftime("%Y-%m-%d")
            break
        if not re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date_str):
            print("Invalid Format")
            continue
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid Date")

    categories = ["Food", "Transport", "Shopping", "Bills", "Other"]    #Checking Category
    while True:
        category = input("Category (Food/Transport/Shopping/Bills/Other): ")
        if category.title() in categories:
            category = category.title()
            break
        print("Invalid Category")

    while True:   #Checking correct description input
        description = input("Description: ")
        if not description:
            print("Description cannot be empty")
            continue
        break

    while True:    #Checking correct amount input
        amount_str = input("Amount: ")
        try:
            amount = float(amount_str)
            if amount <= 0:
                print("Amount cannot be negative")
                continue
            break
        except ValueError:
            print("Invalid Amount")


    new_id = get_next_id()    #Creating expenses as a dictionary
    expense = {
        "id": new_id,
        "date": date_str,
        "category": category,
        "description": description,
        "amount": amount
    }


    with open("expenses.csv", "a", newline="") as file:    #adding expenses to csv
        writer = csv.DictWriter(file, fieldnames = ["id", "date", "category", "description", "amount"])
        if len(load_expenses()) < 1:
            writer.writeheader()
        writer.writerow(expense)
    print("Expense added successfully")



def view_expenses():
    expenses = load_expenses()
    if not expenses:
        print("No expenses found")
        return None

    rows = []
    for e in expenses:
        rows.append([e["id"], e["date"], e["category"], e["description"], float(e["amount"])])
    print(tabulate(rows, headers=["ID", "Date", "Category", "Description", "Amount"], tablefmt="grid", colalign=("center",)*5))
    total = sum(float(e["amount"]) for e in expenses)
    print(f"Total: {total}")

def summarize_expenses():
    expenses = load_expenses()
    if not expenses:
        print("No expenses found.")
        return None

    totals = {}
    for e in expenses:
        category = e["category"]
        totals[category] = totals.get(category, 0) + float(e["amount"])

    print("Expense Summary:")
    print("=" * 30)

    max_total = max(totals.values())
    for category in totals:
        total = totals[category]
        bar = "█" * int((total / max_total) * 30)
        print(f"{category:<15} {total:<10} {bar}")

    print("=" * 30)
    grand_total = sum(totals.values())
    print(f"Grand Total: {grand_total}")
    sorted_totals = sorted(totals, key=totals.get, reverse=True)
    highest_total = sorted_totals[0]
    print(f"Highest spending: {highest_total}")



def delete_expense():
    expenses = load_expenses()
    if not expenses:
        print("No expenses found.")
        return None
    view_expenses()

    try:
        user_id = int(input("Enter ID to delete: "))
    except ValueError:
        print("Invalid ID")
        return

    expense = None
    for e in expenses:
        if int(e["id"]) == user_id:
            expense = e
            break
    if expense is None:
        print("ID is not found")
        return

    confirm = input(f'Delete: "{expense["description"]} - {expense["amount"]}"? (y/n): ')
    if confirm != "y":
        print("Deletion Cancelled")
        return
    expenses.remove(expense)

    for i, e in enumerate(expenses, 1):
        e["id"] = i

    with open("expenses.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames = ["id", "date", "category", "description", "amount"])
        writer.writeheader()
        writer.writerows(expenses)
    print("Expense successfully deleted")


def export_expenses():
    expenses = load_expenses()
    if not expenses:
        print("No expenses found.")
        return None

    start_date = input("Start Date (YYYY-MM-DD): ")
    if start_date == "":
        start_date = None
    else:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid Date")
            return

    end_date = input("End Date (YYYY-MM-DD): ")
    if end_date == "":
        end_date = date.today()
    else:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid Date")
            return

    filtered = []
    for e in expenses:
        e_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
        if start_date == None or start_date <= e_date <= end_date:
            filtered.append(e)
    if not filtered:
        print("No expenses found in given range")
        return

    filename = f"export_{date.today()}.csv"   #saves name of file as export_today's date
    with open (filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "date", "category", "description", "amount"])
        writer.writeheader()
        writer.writerows(filtered)
    if len(filtered) == 1:
        print(f"Exported {len(filtered)} expense to {filename}")
    else:
        print(f"Exported {len(filtered)} expenses to {filename}")   #will be written as exported 4 expenses to export_2026-04-21

if __name__ == "__main__":
    main()
