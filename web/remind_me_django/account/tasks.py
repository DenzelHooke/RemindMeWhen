# Create your tasks here
from account.models import CustomUser
from listings.models import Product
from celery import shared_task, Celery
from decouple import config



@shared_task
def update_item(user_email):
    try:
        user = CustomUser.objects.filter(email=user_email).first()
        item = user.product.all().latest('-date_added')
        item.name = 'Changed by Celery Worker'
        item.save()
        print(f"{user}'s last product item changed to {item.name}")

    except Exception as e:
        print(f'\nTask could not complete because of the following error:\n{e}')   