'''
    This file contains utility functions used throughout the core project
'''


import qrcode
import random, string

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.conf import settings
from config.settings.base import TICKET_URL


from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent




class Util:

    # RANDOM STRING GENERATOR #

    @staticmethod
    def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


    @staticmethod
    def random_digit_generator(size=10, chars=string.digits):
        return ''.join(random.choice(chars) for _ in range(size))


    # SEND EMAIL #

    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']]
        )
        email.send()


    def send_email_attach(msg):
        body_html = "<html><p>This is your ticket</p></html>"


        message = EmailMultiAlternatives(
            subject=msg['subject'],
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[msg['recipient']],
        )
        message.mixed_subtype = 'related'
        message.attach_alternative(body_html, "text/html")
        url = TICKET_URL/"{}.png".format(msg['ticket'])
        message.attach_file('{}'.format(url))

        message.send(fail_silently=False)


    # GENERATE QRCODE #

    @staticmethod
    def generate_qrcode(data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

        qr.add_data(data['url'])
        qr.make(fit=True)
        
        img = qr.make_image(fill_color='black', back_color='white').convert('RGB')
        img.save(TICKET_URL/"{}.png".format(data['ticket']))





