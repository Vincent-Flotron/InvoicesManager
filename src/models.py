import sqlite3
from datetime import date

class Account:
    def __init__(self, id=None, description=None, bank_name=None, account_number=None):
        self.id = id
        self.description = description
        self.bank_name = bank_name
        self.account_number = account_number

class Invoice:
    def __init__(self, id=None, primary_receiver=None, receiver_name=None, receiver_address=None, receiver_account=None, primary_reference=None, secondary_reference=None, invoice_date=None, due_date=None, paid_date=None, amount=None, paying_account_id=None, file_path=None, remark=None, description=None, note=None, tag=None, category=None):
        self.id = id
        self.primary_receiver = primary_receiver
        self.receiver_name = receiver_name
        self.receiver_address = receiver_address
        self.receiver_account = receiver_account
        self.primary_reference = primary_reference
        self.secondary_reference = secondary_reference
        self.invoice_date = invoice_date
        self.due_date = due_date
        self.paid_date = paid_date
        self.amount = amount
        self.paying_account_id = paying_account_id
        self.file_path = file_path
        self.remark = remark
        self.description = description
        self.note = note
        self.tag = tag
        self.category = category

class Operation:
    def __init__(self, id=None, income=0, outcome=0, account_id=None, invoice_id=None, description=None, ):
        self.id = id
        self.income = income
        self.outcome = outcome
        self.account_id = account_id
        self.invoice_id = invoice_id
        self.description = description
        
