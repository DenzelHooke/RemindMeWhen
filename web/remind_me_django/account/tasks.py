# Create your tasks here
from account.models import CustomUser
from listings.models import Product
from celery import shared_task, Celery
from decouple import config



@shared_task
def update_item(user_email):
    try:
        user = CustomUser.objects.filter(email=user_email).first()
        print()
        item = user.product.all().latest('-date_added')
        item.name = 'Changed by Celery Worker'
        item.save()

    except Exception as e:
        print(f'\nTask could not complete beacuase of the following error:\n{e}')   