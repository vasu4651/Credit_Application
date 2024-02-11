import pandas as pd
from myapp.constants import CONFIG
from decimal import Decimal

def get_new_customer_id():
    from .models import Customer
    last_customer = Customer.objects.order_by('-customer_id').first()
    if last_customer:
        customer_id = last_customer.customer_id + 1
    else:
        customer_id = 1

    return customer_id


def get_new_loan_id():
    from .models import Loan
    last_row = Loan.objects.order_by('-loan_id').first()
    if last_row:
        loan_id = last_row.loan_id + 1
    else:
        loan_id = 1

    return loan_id


def calculate_approved_limit(monthly_salary: int) -> int:
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


def calculate_credit_score(customer_id: int) -> float:
    from myapp.models import Customer, Loan
    customer_row = Customer.objects.get(customer_id=customer_id)
    loan_rows = Loan.objects.filter(customer_id=customer_id)

    # (available_limit/approved_limit) * 100
    sum_of_current_loans = get_sum_of_current_loans(customer_id=customer_id)
    approved_limit = customer_row.approved_limit
    available_limit = approved_limit - sum_of_current_loans
    score1 = float(available_limit/approved_limit) * 100


    # sigma((emis_paid_on_time/tenure)*monthly_payment)/sigma(monthly_payment)   * 100
    sum_numerator = 0
    sum_denominator = 0
    for loan_row in loan_rows:
        sum_numerator += (loan_row.emis_paid_on_time/loan_row.tenure)*float(loan_row.monthly_payment)
        sum_denominator += float(loan_row.monthly_payment)
    if not sum_denominator:
        score2 = 0
    else:
        score2 = (sum_numerator/sum_denominator) * 100


    # sum_of_monthly_installments/monthly_salary * 100
    sum_of_current_emis = get_sum_of_current_emis(customer_id=customer_id)
    if customer_row.monthly_salary <= sum_of_current_emis:
        score3 = 0
    else:
        score3 = float((customer_row.monthly_salary - sum_of_current_emis)/customer_row.monthly_salary) * 100

    credit_score = 0.4*score1 + 0.2*score2 + 0.4*score3
    return credit_score


def get_sum_of_current_emis(customer_id: int) -> float:
    from .models import Loan

    loan_rows = Loan.objects.filter(customer_id=customer_id)
    loan_list = list(loan_rows.values())
    res = 0
    for loan in loan_list:
        res += loan.get('monthly_payment', 0)
    return res


def get_sum_of_current_loans(customer_id: int) -> float:
    from .models import Loan

    loan_rows = Loan.objects.filter(customer_id=customer_id)
    loan_list = list(loan_rows.values())
    res = 0
    for loan in loan_list:
        res += loan.get('loan_amount', 0)
    return res


def calculate_check_eligibility(customer_id: int, loan_amount: int, interest_rate: float, tenure: int) -> bool:
    from .models import Customer

    # If sum of all current EMIs > 50% of monthly salary ,don’t approve any loans
    customer_row = Customer.objects.get(customer_id=customer_id)
    monthly_salary = customer_row.monthly_salary
    if (get_sum_of_current_emis(customer_id=customer_id) >= monthly_salary/2):
        return False, None


    # If current exisiting loan amount + asked loan amount > approved limit is_limit_available = false
    sum_of_current_loans = get_sum_of_current_loans(customer_id=customer_id)
    approved_limit = customer_row.approved_limit
    if sum_of_current_loans + loan_amount >= approved_limit:
        return False, None


    # On the basis of credit score
    credit_score = calculate_credit_score(customer_id=customer_id)
    if credit_score >= 50:
        return True, None
    
    elif credit_score >= 30:
        if interest_rate >= 12:
            return True, None
        return False, 12
    
    elif credit_score >= 10:
        if interest_rate >= 16:
            return True, None
        return False, 16
    
    return False, None


def calculate_monthly_installment(loan_amount: float, interest_rate: float, tenure: int) -> float:
    monthly_interest_rate = (interest_rate / 12.00) / 100.00
    num_payments = tenure

    monthly_installment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**num_payments) / ((1 + monthly_interest_rate)**num_payments - 1)

    return round(monthly_installment, 2)
