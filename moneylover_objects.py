from __future__ import annotations

import copy
import datetime
import json
from typing import Iterable, Union

import requests
from enum import Enum
from rich.console import Console
from rich.table import Table

transaction_template = {
    "with": [],
    "account": None,
    "category": None,
    "amount": None,
    "note": None,
    "displayDate": None,
    "event": "",
    "exclude_report": False,
    "longtitude": 0,
    "latitude": 0,
    "addressName": "",
    "addressDetails": "",
    "addressIcon": "",
    "image": ""
}


class MoneyLover:
    def __init__(self, jwt_token: str, user_agent: str):
        self.jwt_token: str = jwt_token
        self.categories: list = []
        self.session: requests.Session = requests.Session()
        self.user_agent: str = user_agent
        self.headers: dict = {'authorization': f'AuthJWT {self.jwt_token}',
                              'origin': 'https://web.moneylover.me',
                              'referer': 'https://web.moneylover.me/',
                              'user-agent': self.user_agent}
        self.transaction_crete_headers: dict = copy.deepcopy(self.headers)
        self.transaction_crete_headers.update({'dataformat': 'json',
                                               'content-type': 'application/json'})
        self.retrieve_categories()

    def retrieve_categories(self) -> None:
        response = self.session.post("https://web.moneylover.me/api/category/list-all",
                                     headers=self.headers)
        response.raise_for_status()
        response_dict: dict = json.loads(response.text)
        if 'msg' in response_dict and response_dict['msg'] == Errors.NOT_AUTHORIZED:
            raise Exception("Wrong JWT token")
        if 'data' not in response_dict:
            raise Exception("No categories found in response")
        for category in response_dict['data']:
            category_instance: Category = Category(category['_id'],
                                                   category['type'],
                                                   category['account'],
                                                   category['name'])
            self.categories.append(category_instance)

    def create_transaction(self, transaction: Transaction):
        if transaction.category not in self.categories:
            raise Exception("Category should belong to the MoneyLover instance")
        request_body = copy.deepcopy(transaction_template)
        request_body.update({
            "account": transaction.category.account,
            "category": transaction.category.id,
            "amount": transaction.amount,
            "note": transaction.note,
            "displayDate": transaction.date
        })
        response = self.session.post('https://web.moneylover.me/api/transaction/add',
                                     headers=self.transaction_crete_headers,
                                     data=json.dumps(request_body))
        response_dict = json.loads(response.text)
        if int(response_dict['error']) == 1:
            raise Exception(f"Error adding new transaction: {response_dict}")

    def get_category_by_id(self, category_id: str) -> Union[Category, None]:
        for category in self.categories:
            if category.id == category_id:
                return category

    def get_category_by_name(self, category_name: str) -> Union[str, None]:
        for category in self.categories:
            if category.name == category_name:
                return category

    def print_categories(self):
        console = Console()

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Category id", style="dim")
        table.add_column("Name")
        table.add_column("Type")

        for category in self.categories:
            table.add_row(category.id, category.name, str(category.type))
        console.print(table)


class TransactionTypes(Enum):
    INCOME = 1
    EXPENSE = 2




class Errors:
    NOT_AUTHORIZED = 'Not authorized error'


class Category:
    def __init__(self, category_id: str, category_type: int, account: str, name: str):
        self.id: str = category_id
        self.name: str = name
        self.account: str = account
        self.type: int = category_type


class Transaction:
    def __init__(self, category: Category,
                 amount: float,
                 date: datetime,
                 transaction_type: Union[TransactionTypes, None] = None,
                 note: str = ''):
        self.transaction_type: TransactionTypes = transaction_type
        self.category: Category = category
        self.date: str = date
        self.note: str = note
        self.amount: float = amount

    def check_and_set_transaction_type(self, amount):
        if self.transaction_type is None:
            if amount > 0:
                self.transaction_type = TransactionTypes.INCOME
            else:
                self.transaction_type = TransactionTypes.EXPENSE

    @property
    def transaction_type(self) -> TransactionTypes:
        return self.__type

    @transaction_type.setter
    def transaction_type(self, value) -> None:
        try:
            self.__type: TransactionTypes = TransactionTypes(value)
        except ValueError:
            raise Exception(f"Wrong transaction id, available options: {list(TransactionTypes)}")

    @property
    def amount(self) -> float:
        return self.__amount

    @amount.setter
    def amount(self, value: str):
        amount: float = float(value)
        self.check_and_set_transaction_type(amount)
        self.__amount: float = abs(amount)

    @property
    def date(self) -> str:
        return self.__date

    @date.setter
    def date(self, value: datetime):
        self.__date: str = value.strftime('%Y-%m-%d')
