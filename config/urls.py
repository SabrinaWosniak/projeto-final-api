from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from financeiro.views import CategoriaViewSet, ContaViewSet, LancamentoViewSet

router = DefaultRouter()
router.register('categorias', CategoriaViewSet)
router.register('contas', ContaViewSet)
router.register('lancamentos', LancamentoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', obtain_auth_token),
    path('api-auth/', include('rest_framework.urls')),
]
