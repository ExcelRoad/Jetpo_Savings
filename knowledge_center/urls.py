from django.urls import path
from . import views

urlpatterns = [
    path('', views.knowledge_center_list, name='knowledge_center'),
    path('submit/', views.submit_article, name='submit_article'),
    path('submission/<int:submission_id>/', views.view_submission, name='view_submission'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
]
