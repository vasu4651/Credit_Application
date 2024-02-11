import json
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import Customer, Loan
from django.views.decorators.csrf import csrf_exempt
from .utils import calculate_approved_limit, get_new_customer_id
from django.http import Http404



def home(x):
    temp = {
        "name": "vasu",
        "age": 34
    }
    return JsonResponse(temp)



@csrf_exempt
def register(request):
    if request.method == 'GET':
        return JsonResponse({'error': 'GET method is not supported for registration'}, status=405)

    try:
        data = json.loads(request.body)
        customer_id = get_new_customer_id()
        approved_limit = calculate_approved_limit(monthly_salary=data['monthly_salary'])
        new_customer = Customer(
            customer_id = customer_id,
            first_name = data['first_name'],
            last_name = data['last_name'],
            age = data['age'],
            phone_number = data['phone_number'],
            monthly_salary = data['monthly_salary'],
            approved_limit = approved_limit,
            current_debt = 0
        )
        new_customer.save()
        print(f"User saved successfully")
        response = {
            'customer_id': customer_id,
            'name': data['first_name'] + " " + data['last_name'],
            'age': data['age'],
            'monthly_income': data['monthly_salary'],
            'approved_limit': approved_limit,
            'phone_number': data['phone_number']

        }
        return JsonResponse(response, status=200)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)




def view_loan_by_loan_id(request, loan_id):
    if request.method != 'GET':
        return JsonResponse({'Error': f'{request.method} is not supported for this operation. Use GET instead.'})
    
    try:
        try:
            loan_row = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return JsonResponse({'Error': f'Loan with Loan ID: {loan_id} does not exist.'}, status=404)
        
        try:
            customer_row = Customer.objects.get(customer_id = loan_row.customer_id)
        except Exception as e:
            return JsonResponse({'Error': e}, status=404)
        
        
        customer = {
            'id': customer_row.customer_id,
            'first_name': customer_row.first_name,
            'last_name': customer_row.last_name,
            'phone_number': customer_row.phone_number,
            'age': customer_row.age
        }

        response = {
            'loan_id': loan_id,
            'customer': customer,
            'loan_amount': loan_row.loan_amount,
            'interest_rate': loan_row.interest_rate,
            'monthly_installment': loan_row.monthly_payment,
            'tenure': loan_row.tenure
        }

        if not response:
            response = {
                "response": f"Loan data does not exist for Loan ID: {loan_id}"
            }

        return JsonResponse(response, status=200)
    
    except Exception as e:
        return JsonResponse({'Error': e}, status=400)


def view_loans_by_customer_id(request, customer_id):
    if request.method != 'GET':
        return JsonResponse({'Error': f'{request.method} is not supported for this operation. Use GET instead.'})
    
    try:
        loan_rows = Loan.objects.filter(customer_id=customer_id)
        loan_list = list(loan_rows.values())
        response = []
        for loan in loan_list:
            fmted_loan = {
                'load_id': loan.get('loan_id', None),
                'loan_amount': loan.get('loan_amount', None),
                'interest_rate': loan.get('interest_rate', None),
                'monthly_installment': loan.get('monthly_payment', None),
                'repayments_left': (loan.get('tenure') - loan.get('emis_paid_on_time')) if (loan.get('tenure') and loan.get('emis_paid_on_time')) else None
            }
            response.append(fmted_loan)

        if len(response) == 0:
            response = {
                "response": "No loans found for this customer"
            }
                
        return JsonResponse(response, status=200, safe=False)
    
    except Exception as e:
        return JsonResponse({'Error': e}, status=400)