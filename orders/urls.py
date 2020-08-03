from django.urls    import path

from .views         import (
    OrderColorItemView,
    CartList,
    OrderBulkItem,
)

urlpatterns = [
    path('/color-select',OrderColorItemView.as_view()),
    path('/cart-list',CartList.as_view()),
    path('/bulk-order',OrderBulkItem.as_view()),
]
