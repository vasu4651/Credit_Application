from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .utils import load_excel_to_postgresql

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Add your code to run when the app is starting
        print("MyApp is starting. Perform initialization tasks here.")

@receiver(post_migrate)
def on_post_migrate(sender, **kwargs):
    if sender.name == 'myapp':
        print("post_migrate signal received")
        load_excel_to_postgresql()
        print("Application running on localhost:8000")