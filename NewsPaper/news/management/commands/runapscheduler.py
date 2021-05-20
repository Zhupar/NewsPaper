import logging
import requests
import lxml.html


from django.conf import settings
from datetime import datetime
from Lib.datetime import timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution



from ...models import Category

logger = logging.getLogger(__name__)


def send_email():
    message = ''
    categories = Category.objects.all()
    for category in categories:
        posts_cat = category.posts.all()
        print(posts_cat)
        post_filter = posts_cat.filter(post_date_time__gt=datetime.now() - timedelta(days=7))
        print(post_filter)
        for post in post_filter:
            post_url = f'http://127.0.0.1:8000/{post.pk}'
            message += f'{post.post_title} \n {post.post_text[:50]}...\n Follow link: {post_url}\n'
            categories = post.post_category.all()
            cat_id = 0
            for c in categories:
                cat_id = c.id
                print(cat_id)

                get_subscribers = Category.objects.get(id=cat_id)
                subs_list = get_subscribers.subscribers.all()
                print(subs_list)
                for sub in subs_list:
                    send_to = sub.email
                    send_to_uname = sub.username
                    send_mail(
                        subject=f'Dear {send_to_uname}! Please, get the latest news!',
                        message=message,
                        from_email='zhuparadamova@yandex.ru',
                        recipient_list=[send_to]
                    )



# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику

        scheduler.add_job(
            send_email,
            trigger=CronTrigger(second="*/604_800"),
            # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="send_email",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'send_email'."
        )

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")