import pandas as pd
from myapp.constants import CONFIG

def get_new_customer_id():
    from .models import Customer
    last_customer = Customer.objects.order_by('-customer_id').first()
    if last_customer:
        customer_id = last_customer.customer_id + 1
    else:
        customer_id = 1

    return customer_id


def calculate_approved_limit(monthly_salary: int):
    limit = 36*monthly_salary
    rounded_limit = round(limit, -5)
    return rounded_limit


def load_excel_to_postgresql_util_customer():
    from .models import Customer
    count = Customer.objects.count()
    if count != 0:
        print(f"Data already present in Customer table in PostgreSQL so not loading from xlsx file, count: {count}")
        return
    try:
        df = pd.read_excel(CONFIG['customer_excel_file_path'])

        for _, row in df.iterrows():
            customer = Customer(
                customer_id=row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                age=row['Age'],
                phone_number=row['Phone Number'],
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit'],
                current_debt=0
            )
            customer.save()

        count = Customer.objects.count()
        print(f'Successfully loaded data into the Customer table, count: {count}')

    except Exception as e:
        print(f'Error loading data: {str(e)}')


def load_excel_to_postgresql_util_loan():
    from .models import Loan
    count = Loan.objects.count()
    print(f"Loan Data Count: {count}")
    if count != 0:
        print(f"Data already present in Loan table in PostgreSQL, so not loading from xlsx file, count: {count}")
        return

    try:
        df = pd.read_excel(CONFIG['loan_excel_file_path'])

        for _, row in df.iterrows():
            loan = Loan(
                customer_id=row['Customer ID'],
                loan_id=row['Loan ID'],
                loan_amount=row['Loan Amount'],
                tenure=row['Tenure'],
                interest_rate=row['Interest Rate'],
                monthly_payment=row['Monthly payment'],
                emis_paid_on_time=row['EMIs paid on Time'],
                date_of_approval=row['Date of Approval'],
                end_date=row['End Date']
            )
            try:
                loan.save()
            except Exception as e:
                print(f"Error in saving row to loan table, error message: {e}")


        count = Loan.objects.count()
        print(f'Successfully loaded data into the Loan table, count: {count}')

    except Exception as e:
        print(f'Error loading data: {str(e)}')


def load_excel_to_postgresql():
    load_excel_to_postgresql_util_customer()
    load_excel_to_postgresql_util_loan()