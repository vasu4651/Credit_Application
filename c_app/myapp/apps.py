from django.apps import AppConfig
# from .utils import load_excel_to_postgresql

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # Add your code to run when the app is starting
        print("MyApp is starting. Perform initialization tasks here.")
        # load_excel_to_postgresql()
