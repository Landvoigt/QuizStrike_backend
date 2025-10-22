from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('answer.urls')),
    path('api/', include('category.urls')),
    path('api/', include('player.urls')),
    path('api/', include('question.urls')),
    path('api/', include('quiz.urls')),
    path('api/', include('response.urls')),
    path('api/', include('score.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
