All the functionality as mentioned in the assignment document has been implemented. The data from excel sheets are loaded to the database after the "post_migrate" signal is received which denotes the event of the completion of the migration from models to the Postgresql database.


Run this command at the location where the docker-compose.yml file is present to run the application on localhost:8000/:
    docker-compose up


I have also pushed the image to Docker Hub. The application can be run locally just by saving the below as a docker-compose.yml file and running the command "docker-compose up" without the requirement of any code.
"""

version: "3.8"
services:

    postgres_db:
        image: postgres:latest
        environment:
        - POSTGRES_DB=test11
        - POSTGRES_USER=postgres
        - POSTGRES_PASSWORD=1234
        ports:
        - "5432:5432"
        
    web:
        image: vasu4651/myapp:1
        ports:
        - "8000:8000"
        command: ["sh", "./start.sh"]
        depends_on:
        - postgres_db

"""




Here is a breif info about each endpoint

    1) /register
        This function creates a new customer row in the database.
    
    2) /check-eligibility
        This function checks if a loan is eligible for a customer based on the following parameters:
        * If sum of all current EMIs > 50% of monthly salary ,don’t approve any loans
        * If current exisiting loan amount + asked loan amount > approved limit, is_limit_available = false, don’t approve
        * On the basis of credit score. Calculation of credit score :
            score1 = (available_limit/approved_limit) * 100
            score2 = sigma((emis_paid_on_time/tenure)*monthly_payment)/sigma(monthly_payment)   * 100
            score3 = sum_of_monthly_installments/monthly_salary * 100
            credit_score = 0.4*score1 + 0.2*score2 + 0.4*score3

    3) /create-loan
        Firstly the eligibilty is checked using the above methods. If a customer is eligible then the loan is created in the loan table of
        the database with a new unique Loan ID

    4) /view-loan/loan_id
        Returns the details of the loan and customer corressponding to the loan_id given.
    
    5) /view-loans/customer_id
        Returns the list of all loans relating to the provided customer_id.



Sample requests and responses:

    1) /register
        Request: 
            curl --location 'http://localhost:8000/register/' \
            --header 'Content-Type: application/json' \
            --header 'Cookie: csrftoken=W3raQo9ZrhgmGK4ZiGpjncLMjzlXriXA' \
            --data '{
                "first_name": "Gautam",
                "last_name": "Agrawal",
                "age": 24,
                "phone_number": "9231231234",
                "monthly_salary": 30000
            }'
        Response:
            {
                "customer_id": 301,
                "name": "Gautam Agrawal",
                "age": 24,
                "monthly_income": 30000,
                "approved_limit": 1100000,
                "phone_number": "9231231234"
            }


    2) /check-eligibility
        Request:
            curl --location --request GET 'localhost:8000/check-eligibility/' \
            --header 'Content-Type: application/json' \
            --header 'Cookie: csrftoken=W3raQo9ZrhgmGK4ZiGpjncLMjzlXriXA' \
            --data '{
                "customer_id": 213,
                "loan_amount": 90000,
                "interest_rate": 8,
                "tenure": 24
            }'
        Response:
            {
                "customer_id": 213,
                "approval": true,
                "interest_rate": 8,
                "corrected_interest_rate": null,
                "tenure": 24,
                "monthly_installment": 4070.46
            }

    
    3) /create-loan
        Request:
            curl --location 'http://localhost:8000/create-loan/' \
            --header 'Content-Type: application/json' \
            --header 'Cookie: csrftoken=W3raQo9ZrhgmGK4ZiGpjncLMjzlXriXA' \
            --data '{
                "customer_id": 301,
                "loan_amount": 200000,
                "interest_rate": 12,
                "tenure": 23
            }'
        Response:
            {
                "loan_id": 9997,
                "customer_id": 301,
                "loan_approved": true,
                "message": "Congrats, loan approved.",
                "monthly_installment": 9777.17
            }


    4) /view-loan/loan_id
        Request:
            curl --location 'localhost:8000/view-loan/2751' \
            --header 'Cookie: csrftoken=W3raQo9ZrhgmGK4ZiGpjncLMjzlXriXA' \
            --data ''
        Response:
            {
                "loan_id": 2751,
                "customer": {
                    "id": 173,
                    "first_name": "Amal",
                    "last_name": "Salazar",
                    "phone_number": "9401771136",
                    "age": 44
                },
                "loan_amount": "200000.00",
                "interest_rate": "12.84",
                "monthly_installment": "5097.00",
                "tenure": 81
            }
        
    
    5) /view-loans/customer_id
        Request:
            curl --location 'localhost:8000/view-loans/173' \
            --header 'Cookie: csrftoken=W3raQo9ZrhgmGK4ZiGpjncLMjzlXriXA'
        Response:
            [
                {
                    "load_id": 2751,
                    "loan_amount": "200000.00",
                    "interest_rate": "12.84",
                    "monthly_installment": "5097.00",
                    "repayments_left": 31
                },
                {
                    "load_id": 7191,
                    "loan_amount": "300000.00",
                    "interest_rate": "14.61",
                    "monthly_installment": "8379.00",
                    "repayments_left": 3
                },
                {
                    "load_id": 9255,
                    "loan_amount": "500000.00",
                    "interest_rate": "10.06",
                    "monthly_installment": "14385.00",
                    "repayments_left": 4
                },
                {
                    "load_id": 7481,
                    "loan_amount": "600000.00",
                    "interest_rate": "11.22",
                    "monthly_installment": "13471.00",
                    "repayments_left": 50
                },
                {
                    "load_id": 4526,
                    "loan_amount": "500000.00",
                    "interest_rate": "16.35",
                    "monthly_installment": "24361.00",
                    "repayments_left": 73
                },
                {
                    "load_id": 7327,
                    "loan_amount": "200000.00",
                    "interest_rate": "17.28",
                    "monthly_installment": "9405.00",
                    "repayments_left": 50
                }
            ]



