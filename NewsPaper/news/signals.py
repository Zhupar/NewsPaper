from django.db.models.signals import post_save
from django.dispatch import receiver  # импортируем нужный декоратор
from django.core.mail import mail_managers
from django.contrib.sites.models import Site
from .models import Post

last_news = []
@receiver(post_save, sender=Post)
def notify_managers_appointment(sender, instance, created, **kwargs):
    if created:
        last_news.append(instance)
        subject = f'{instance.post_title}'
        current_site = Site.objects.get_current()
        message = f'Dear Subscriber,\n' \
                  f'{instance.post_category.values()}'\
                  f'New article is published: \n' \
                  f'{instance.post_title}\n' \
                  f'{instance.post_text[:50]}\n' \
                  f'Follow link:{current_site}:8000{instance.get_absolute_url()} '  \

    else:
        subject = f'Appointment changed for {instance.post_title} '

    mail_managers(
        subject=subject,
        message=message
    )
