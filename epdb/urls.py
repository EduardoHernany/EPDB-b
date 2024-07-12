from django.urls import path
from .views import DockingView

from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
#router.register(r'authors', AuthorViewSet)
#router.register(r'books', BookViewSet)
router.register(r'epdb',DockingView)
#router.register(r'virtual-screening-simple',VirtualScreeningView)
#router.register(r'virtualscreeningnxn', VirtualScreeningNXNView)

urlpatterns = [
   path('', include(router.urls)),
   #path('books', AuthorViewSet.as_view(), name='virtual_screening_nxn_api'),
   #path('virtual-screening-NxN/', VirtualScreeningNXNView.as_view(), name='virtual_screening_nxn_api'),
   #path('virtualscreeningnxn/<int:pk>/', VirtualScreeningNXNView.as_view(), name='virtualscreeningnxn-detail'),
]
