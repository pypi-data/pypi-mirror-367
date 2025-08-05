

from django.urls import path

from core.views import create_table_row, delete_table_row, get_table_data, get_tables, list_databases, login_view, update_table_row
from django.contrib.auth.views import LogoutView


urlpatterns = [
     path('', login_view, name='login'),    
     path('das/', list_databases, name='das'),
     path('tables/<str:db_name>/', get_tables, name='get_tables'),
     path('tables/<str:db_name>/<str:table_name>/', get_table_data, name='get_table_data'),
     path('tables/<str:db_name>/<str:table_name>/update/<str:pk>/', update_table_row, name='update_table_row'),
     path('tables/<str:db_name>/<str:table_name>/create/', create_table_row, name='create_table_row'),
     path('tables/<str:db_name>/<str:table_name>/delete/<str:row_id>/', delete_table_row, name='delete_table_row'),
     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]
