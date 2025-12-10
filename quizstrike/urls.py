from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path

from quizstrike.views import QuestionStartView, QuestionFinishView

def api_root(request):
    return JsonResponse({"message": "Quizstrike_backend API is running."})

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),

    path('api/start/', QuestionStartView.as_view(), name='question-start'),
    path('api/finish/', QuestionFinishView.as_view(), name='question-finish'),

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
