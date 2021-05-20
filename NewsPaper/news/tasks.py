from celery import shared_task
from django.core.mail import send_mail
from datetime import datetime
from Lib.datetime import timedelta
from .models import Category, Post


@ shared_task
def send_email(send_to, post_url, post_text, post_title, send_to_uname):
    send_mail(
        subject=f'Dear {send_to_uname}! Please, get the latest news!',
        # имя клиента и дата записи будут в теме для удобства
        message=f'{post_title} \n {post_text[:50]}...\n Follow link: {post_url}',  # сообщение с кратким описанием проблемы
        from_email='zhuparadamova@yandex.ru',  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        recipient_list=[send_to]  # здесь список получателей. Например, секретарь, сам врач и т. д.
    )


@ shared_task
def scheduled_email():
    message = ''
    categories = Category.objects.all()
    for category in categories:
        posts_cat=category.posts.all()
        post_filter= posts_cat.filter(post_date_time__gt=datetime.now()-timedelta(days=7))
        # print(post_filter)
        for post in post_filter:
            post_url = f'http://127.0.0.1:8000/{post.pk}'
            message += f'{post.post_title} \n {post.post_text[:50]}...\n Follow link: {post_url}\n'
            categories = post.post_category.all()
            cat_id = 0
            for c in categories:
                cat_id = c.id
                # print(cat_id)

            get_subscribers = Category.objects.get(id=cat_id)
            subs_list = get_subscribers.subscribers.all()
            # print(subs_list)
            for sub in subs_list:
                send_to = sub.email
                send_to_uname = sub.username
                send_mail(
                    subject=f'Dear {send_to_uname}! Please, get the latest news!',
                    message=message,
                    from_email='zhuparadamova@yandex.ru',
                    recipient_list=[send_to]
                )
