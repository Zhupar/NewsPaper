import logging
import requests
import lxml.html


from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.contrib.sites.models import Site


logger = logging.getLogger(__name__)
last = [('test', 'test')]

class Parce:
    url = 'http://127.0.0.1:8000/'
    def req(self, url=url):
        html = requests.get(url).content
        tree = lxml.html.document_fromstring(html)
        a = tree.xpath('/html/body/div/a[3]')
        title = tree.xpath('/html/body/div/a[4]/h3')

        for link in a:
            current_href = link.get('href')
            for l in link:
                current_title = l.text
            return l.text, url+current_href

def my_job():
    current = Parce()
    current = current.req()
    if last[-1] != current:
        last.append(current)



def send_email():
    message = 'Dear Subscriber!\n Please, get the latest news:\n '
    for l in last:
        message+= f'{l[0]} --- Follow link: {l[1]}\n'
        print(message)
    send_mail(
        'The latest news',
        message,
        'zhuparadamova@yandex.ru',
        ['zhuparadamova@gmail.com'],
        fail_silently=False,
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
            my_job,
            trigger=CronTrigger(second="*/5"),
            # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            send_email,
            trigger=CronTrigger(second="*/15"),
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