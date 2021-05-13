from django.urls import path
from .views import NewsList, PostDetail, Search, PostCreateView, PostUpdateView, PostDeleteView, upgrade_me, subscribe

urlpatterns = [
    path('', NewsList.as_view(), name='news'),
    path('<int:pk>', PostDetail.as_view(), name = 'post'),
    path('search/', Search.as_view(), name = 'search'),
    path('add/', PostCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='delete'),
    path('upgrade/', upgrade_me, name = 'upgrade'),
    path('subscribe/', subscribe, name = 'subscribe'),
]