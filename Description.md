# Aim
I want to make an invoices to pay manager.

# Functionalities/structures
It will allow me to enter a new invoice to pay giving:
- the primary receiver's name (could be None if not an invoice payment reminder)
- the receiver's name (with index on it)
- the receiver's address
- the receiver's account (with index on it)
- the primary reference of the invoice  (with index on it)
- the secondary reference of the invoice (With index on it. Could be None if not an invoice payment reminder.)
- the date of the invoice (with index on it)
- the date to be paid (with index on it)
- the date it was paid (with index on it. Could be None if not paid)
- the amount (with index on it)
- the account which will pay (with index on it)
- a link (file_path) to the referenced document  (could be None if not document)
- a remark   (could be None)
- a description (could be None)
- a note (could be None)
- a tag (with index **tag**. Could be None)
- a category (with index **category** . Could be None)
It will have an id as unique primary key auto-incremented too.

The account which will pay will have the infos:
- id as unique primary key auto-incremented
- the description (with index on it)
- the bank's name
- the account number (with a unique index **account_nb** on it)

If an invoice is paid ( the date it was paid is not None ), it creates an operation and put the amount into the field outcome.
The fields of the operations are:
- id as unique primary key auto-incremented
- the income which as a default value of 0
- the outcome which as a default value of 0
- the id of the account which will pay (it's a foreign key to the account which will pay)
- the id of the invoice to pay (it's a foreign key to the invoice to pay which can be None)
                                                                                               
# Views:
## Invoices to pay
I must be able to list the invoices to pay, enter a new one, delete one if no operations on it, modify one.
I can set a link (file_path) to the referenced document by using a file browser.
## Accounts
I must be able to list the accounts which will pay, enter a new one, delete one if no operations on it, modify one.
## Account's operations
I must be able to list the operations related to an account as rows with the values of the fields of the invoice to pay related to, enter a new operations, delete operations, modify operations. And when I double click a row it will open the file linked to the invoice to pay if set.
An extra rows at last position will, after every new or modification or deletion of an operation, calculate the sum of all operations incomes minus all the operations outcomes.

# technologies
sqlite for storing acounts which wil pay, operations, invoices to pay
TKinter with possibility to switch from one view to another.
