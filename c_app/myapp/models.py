from django.db import models

# Create your models here.
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=10, decimal_places=2)
    current_debt = models.DecimalField(max_digits=10, decimal_places=2)


class Loan(models.Model):
    customer_id = models.IntegerField()
    loan_id = models.IntegerField(unique=True, primary_key=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    date_of_approval = models.DateField()
    end_date = models.DateField()