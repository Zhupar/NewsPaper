from django import template

register = template.Library()

censor_words = ['идиот', 'блять', 'сука', 'ёмоё', 'дурак']


@register.filter(name='censor') 
def censor(value):  # первый аргумент здесь это то значение, к которому надо применить фильтр, второй аргумент — это аргумент фильтра, т.е. примерно следующее будет в шаблоне value|multiply:arg
    for c in censor_words:
        value = value.replace(c, '!@#$%')
    return value

