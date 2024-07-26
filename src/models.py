import sqlite3
from datetime import date

class Account:
    def __init__(self, id=None, description=None, bank_name=None, iban=None):
        self.id          = id
        self.description = description
        self.bank_name   = bank_name
        self.iban        = iban

class Invoice:
    def __init__(self, id=None, primary_receiver=None, receiver_name=None, receiver_address=None, receiver_account=None, primary_reference=None, secondary_reference=None, invoice_date=None, due_date=None, paid_date=None, amount=None, paying_account_id=None, file_path=None, remark=None, description=None, note=None, tag=None, category=None):
        self.id                  = id
        self.primary_receiver    = primary_receiver
        self.receiver_name       = receiver_name
        self.receiver_address    = receiver_address
        self.receiver_account    = receiver_account
        self.primary_reference   = primary_reference
        self.secondary_reference = secondary_reference
        self.invoice_date        = invoice_date
        self.due_date            = due_date
        self.paid_date           = paid_date
        self.amount              = amount
        self.paying_account_id   = paying_account_id
        self.file_path           = file_path
        self.remark              = remark
        self.description         = description
        self.note                = note
        self.tag                 = tag
        self.category            = category

    def is_paid(self):
        if self.paid_date:
            return True
        else:
            return False
    
    def has_amount(self):
        return self.amount != None
    
    def has_paid_date(self):
        return self.paid_date != None
    
    def has_paying_account(self):
        return self.paying_account_id != None

class Operation:
    op_types=['customized_account_closure', 'starting_amount']
    def __init__(self, id=None, paid_date=None, income=None, outcome=None, account_id=None, invoice_id=None, type=None):
        self.id         = id
        self.paid_date  = paid_date
        self.income     = income
        self.outcome    = outcome
        self.account_id = account_id
        self.invoice_id = invoice_id
        self.type       = type
        self.file_path  = None

