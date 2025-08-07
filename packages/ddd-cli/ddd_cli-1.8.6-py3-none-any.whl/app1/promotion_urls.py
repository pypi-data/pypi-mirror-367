
from django.urls import path

from . import promotion_views

app_name = "app1"

urlpatterns = [

    path('', promotion_views.promotion_list, name="index"),  # ← Esta es la URL por defecto    
    path('promotion-list/', promotion_views.promotion_list, name="promotion_list"),
    path('promotion-create/', promotion_views.promotion_create, name="promotion_create"),
    path('promotion-edit/<int:id>', promotion_views.promotion_edit, name="promotion_edit"),
    path('promotion-detail/<int:id>', promotion_views.promotion_detail, name="promotion_detail"),
    path('promotion-delete/<int:id>', promotion_views.promotion_delete, name="promotion_delete"),    

]
