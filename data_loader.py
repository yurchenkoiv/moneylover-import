import argparse
import csv
import datetime
import random
import sys
from time import sleep
from typing import List, Tuple

from rich.console import Console
from rich.progress import track
from rich.table import Table

from moneylover_objects import Transaction, MoneyLover, TransactionTypes

from config import config_dict, load_csv_config


def get_transaction_id(transaction_type: str) -> TransactionTypes:
    lowered_transaction_type = transaction_type.lower()
    if lowered_transaction_type not in ['income', 'expense']:
        raise Exception("Transaction type could be expense or income")
    return TransactionTypes(2) if lowered_transaction_type == 'expense' else TransactionTypes(1)


def load_csv_file() -> List[list]:
    with open(csv_file_config['filePath'], 'r') as f:
        rows = csv.reader(f, delimiter=csv_file_config['delimiter'])
        csv_rows_list = list(rows)[1 if csv_file_config['withHeaders'] else 0:]
        return csv_rows_list


def create_transactions_from_csv(csv_rows_list: list, ml: MoneyLover) -> Tuple[List[Transaction], set]:
    transactions = []
    unmapped = set()
    for trans in csv_rows_list:
        csv_header_index = csv_file_config['csvHeader']
        categories_mapping = csv_file_config['categories']
        amount = trans[csv_header_index['amount']]
        date = trans[csv_header_index['date']]
        trans_type = trans[csv_header_index['type']]
        category = trans[csv_header_index['category']]
        if ('ignoredCategories' in csv_file_config and category in csv_file_config['ignoredCategories']) \
                or category == '':
            continue
        notes = trans[csv_header_index['notes']]
        mapped_category = categories_mapping.get(category, None)
        if mapped_category is None:
            unmapped.add(category)
            continue
        try:
            datetime_instance = datetime.datetime.strptime(date, csv_file_config['dateFormat'])
        except ValueError:
            raise Exception(f"Provided datetime format {csv_file_config['dateFormat']} is invalid")
        cat = ml.get_category_by_id(mapped_category)
        if cat is None:
            raise Exception(f"Cant find {mapped_category}: {category}")
        transaction_type = get_transaction_id(trans_type)
        t = Transaction(cat,
                        amount,
                        datetime_instance,
                        transaction_type=transaction_type,
                        note=notes)
        transactions.append(t)
    return transactions, unmapped


def check_unmapped(unmapped: set) -> None:
    if unmapped:
        console.print(f"These categories are not mapped: {unmapped}", style="bold red")
        console.print(f"Please map them using the table below", style="bold red")
        money_lover.print_categories()
        sys.exit(1)


def check_correctness(transactions: List[Transaction]):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim")
    table.add_column("Category")
    table.add_column("Type")
    table.add_column("Amount")
    table.add_column("Notes")
    transactions_count = len(transactions)
    for transaction in random.sample(transactions, 10 if transactions_count > 10 else transactions_count):
        table.add_row(transaction.date, transaction.category.name, str(TransactionTypes(transaction.category.type)), str(transaction.amount), transaction.note)
    console.print(table)
    correct = input("Everything is correct? (y=yes, n=no): ").lower() == 'y'
    if not correct:
        console.print("Check mapping and try once again", style="bold red")
        sys.exit(1)


def create_transactions(transactions):
    for t in track(transactions):
        money_lover.create_transaction(t)
        sleep(config_dict['requestsDelaySeconds'])
    console.print(f"{len(transactions)} transactions were successfully created")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_config_path', type=str,
                        help='Path to the csv file config yaml')

    args = parser.parse_args()
    console = Console()
    csv_file_config = load_csv_config(args.csv_config_path)
    money_lover = MoneyLover(config_dict["jwtToken"], config_dict['userAgent'])
    csv_rows = load_csv_file()

    transactions_list, unmapped_categories = create_transactions_from_csv(csv_rows, money_lover)
    check_unmapped(unmapped_categories)
    check_correctness(transactions_list)
    create_transactions(transactions_list)
