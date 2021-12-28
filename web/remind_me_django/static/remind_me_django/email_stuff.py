import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'
django.setup()
from django.core.mail import send_mail


class Product_Email:
    def __init__(self, product:object, redis_product:dict):
        self.product = product
        self.redis_product = redis_product
        self.old_price = product.price
        self.new_prod_price = redis_product['price']

    @property
    def price_diff(self):
        return self.old_price - self.new_prod_price
    
    @property
    def positive_diff(self):
        return self.price_diff * -1

    def send_price_decrease_email(self):
        """
        Sends a email notifiying user that the price of their product has decreased
        """
        send_mail(
            'RemindMeWhen Price Alert!',
            f"""
            Hello, your product "{self.product.name}" has decreased in price by ${self.price_diff}!

            Old price: {self.old_price}\n------\nUpdated price: {self.redis_product['price']}            


            Here is your product page: {self.product.url}
            """,
            'denzelthecreator@gmail.com',
            [self.product.author.email],
            fail_silently=False,
        )
    
    def send_in_stock_price_decrease(self):
        """
        Sends a email notifiying user that the price of their product has decreased and their product is in stock.
        """
        send_mail(
            'RemindMeWhen Price & Stock Alert!',
            f"""
            Hello, your product "{self.product.name}" has decreased in price by ${self.price_diff}
            and is now back in stock!

            Old price: {self.old_price}\n------\nUpdated price: {self.redis_product['price']}            


            Here is your product page: {self.product.url}
            """,
            'denzelthecreator@gmail.com',
            [self.product.author.email],
            fail_silently=False,
        )

    def send_price_increase_email(self):
        """
        Sends a email notifiying user that the price of their product has increased
        """
        send_mail(
            'RemindMeWhen Price Alert!',
            f"""
            Hello, your product "{self.product.name}" has increased in price by ${self.price_diff}!

            Old price: {self.old_price}\n------\nUpdated price: {self.redis_product['price']}            


            Here is your product page: {self.product.url}
            """,
            'denzelthecreator@gmail.com',
            [self.product.author.email],
            fail_silently=False,
        )

    def send_in_stock_price_increase(self):
        """
        Sends a email notifiying user that the price of their product has decreased and their product is in stock.
        """
        send_mail(
            'RemindMeWhen Price & Stock Alert!',
            f"""
            Hello, your product "{self.product.name}" has increased in price by ${self.price_diff}
            and is now back in stock!

            Old price: {self.old_price}\n------\nUpdated price: {self.redis_product['price']}            


            Here is your product page: {self.product.url}
            """,
            'denzelthecreator@gmail.com',
            [self.product.author.email],
            fail_silently=False,
        )

    def send_out_stock_price_increase(self):
        """
        Sends a email notifiying user that the price of their product has increased
        """
        send_mail(
            'RemindMeWhen Price Alert!',
            f"""
            Hello, your product "{self.product.name}" has increased in price by ${self.price_diff}
            and is unfortunately out of stock.

            Old price: {self.old_price}\n------\nUpdated price: {self.redis_product['price']}            


            Here is your product page: {self.product.url}
            """,
            'denzelthecreator@gmail.com',
            [self.product.author.email],
            fail_silently=False,
        )
    

    
    def send_out_of_stock_email(self):
        """
        Sends a email notifiying user that their product is now out of stock
        """
        send_mail(
            'RemindMeWhen *Stock* Alert!',
            f"""
            Hello, your product "{self.product.name}" is now unfortunately out of stock.          

            Here is your product page: {self.product.url}
            """,
            'denzelthecreator@gmail.com',
            [self.product.author.email],
            fail_silently=False,
        )

    def send_in_stock_email(self):
        """
        Sends a email notifiying user that their product is now in stock
        """
        send_mail(
            'RemindMeWhen *Stock* Alert!',
            f"""
            Hello, your product "{self.product.name}" is now back in stock!          

            Here is your product page: {self.product.url}
            """,
            'denzelthecreator@gmail.com',
            [self.product.author.email],
            fail_silently=False,
        )