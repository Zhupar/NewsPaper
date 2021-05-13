from django_filters import FilterSet, CharFilter, DateFilter
from django.forms import DateInput

from .models import Post


class PostFilter(FilterSet):
    post_title = CharFilter(field_name='post_title', lookup_expr='icontains', label='Заголовок')
    post_date_time = DateFilter(field_name='post_date_time', widget=DateInput(attrs={'type': 'date'}),
                                         lookup_expr='gt', label='Позже даты')

    class Meta:
        model = Post
        fields = ['post_author',]