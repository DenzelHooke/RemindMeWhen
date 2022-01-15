import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'
django.setup()
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template.context import Context

class Product_Email:
    from_email = 'denzelthecreator@gmail.com'

    def __init__(self, product:object, redis_product:dict):
        self.product = product
        self.redis_product = redis_product
        self.old_price = self.product.price
        self.new_prod_price = redis_product['price']

    @property
    def price_diff(self):
        return self.old_price - self.new_prod_price
    
    @property
    def positive_diff(self):
        return self.price_diff * -1

    @property
    def context(self):
        return {
            'product':self.product, 
            'redis_product':self.redis_product,
            'old_price':self.old_price,
            'new_price':self.new_prod_price,
            'price_diff':self.price_diff,
        }

    def send_price_decrease_email(self):
        """
        Sends a email notifiying user that the price of their product has decreased
        """

        html_template = get_template("listings/price_decrease.html").render(context=self.context)

        email_msg = EmailMultiAlternatives(
            subject='RemindMeWhen Price Decrease Alert!',
            body="Hello there.",
            from_email=Product_Email.from_email,
            to=[self.product.author.email],
        )
    
        email_msg.attach_alternative(html_template, "text/html")
        email_msg.send()
        print(f"email sent to {self.product.author} by {Product_Email.from_email}")
        print(self.context)

    def send_in_stock_price_decrease(self):
        """
        Sends a email notifiying user that the price of their product has decreased and their product is in stock.
        """
        html_template = get_template("listings/price_decrease_in_stock.html").render(context=self.context)

        email_msg = EmailMultiAlternatives(
            subject='RemindMeWhen Price & Stock Alert!',
            from_email=Product_Email.from_email,
            to=[self.product.author.email],
        )
    
        email_msg.attach_alternative(html_template, "text/html")
        email_msg.send()
        print(f"email sent to {self.product.author} by {Product_Email.from_email}")
        print(self.context)

    def send_price_increase_email(self):
        """
        Sends a email notifiying user that the price of their product has increased
        """
        html_template = get_template("listings/price_increase.html").render(context=self.context)

        email_msg = EmailMultiAlternatives(
            subject='RemindMeWhen Price Increase Alert!',
            from_email=Product_Email.from_email,
            to=[self.product.author.email],
        )
    
        email_msg.attach_alternative(html_template, "text/html")
        email_msg.send()
        print(f"email sent to {self.product.author} by {Product_Email.from_email}")
        print(self.context)

    def send_in_stock_price_increase(self):
        """
        Sends a email notifiying user that the price of their product has decreased and their product is in stock.
        """
        html_template = get_template("listings/price_increase_in_stock.html").render(context=self.context)

        email_msg = EmailMultiAlternatives(
            subject='RemindMeWhen Price Increase & Stock Alert!',
            from_email=Product_Email.from_email,
            to=[self.product.author.email],
        )
    
        email_msg.attach_alternative(html_template, "text/html")
        email_msg.send()
        print(f"email sent to {self.product.author} by {Product_Email.from_email}")
        print(self.context)

    def send_out_stock_price_increase(self):
        """
        Sends a email notifiying user that the price of their product has increased
        """
        html_template = get_template("listings/price_increase_out_stock.html").render(context=self.context)

        email_msg = EmailMultiAlternatives(
            subject='RemindMeWhen Price Increase & Stock Alert!',
            from_email=Product_Email.from_email,
            to=[self.product.author.email],
        )
    
        email_msg.attach_alternative(html_template, "text/html")
        email_msg.send()
        print(f"email sent to {self.product.author} by {Product_Email.from_email}")
        print(self.context)
    
    def send_out_of_stock_email(self):
        """
        Sends a email notifiying user that their product is now out of stock
        """
        html_template = get_template("listings/out_stock.html").render(context=self.context)

        email_msg = EmailMultiAlternatives(
            subject='RemindMeWhen Stock Alert!',
            from_email=Product_Email.from_email,
            to=[self.product.author.email],
        )
    
        email_msg.attach_alternative(html_template, "text/html")
        email_msg.send()
        print(f"email sent to {self.product.author} by {Product_Email.from_email}")
        print(self.context)

    def send_in_stock_email(self):
        """
        Sends a email notifiying user that their product is now in stock
        """
        html_template = get_template("listings/in_stock.html").render(context=self.context)

        email_msg = EmailMultiAlternatives(
            subject='RemindMeWhen Stock Alert!',
            from_email=Product_Email.from_email,
            to=[self.product.author.email],
        )
    
        email_msg.attach_alternative(html_template, "text/html")
        email_msg.send()
        print(f"email sent to {self.product.author} by {Product_Email.from_email}")
        print(self.context)