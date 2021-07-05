from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app_main.urls', namespace='app_main')),
    path('users/', include('app_users.urls', namespace='app_users')),
    path('matches/', include('app_matches.urls', namespace='app_matches')),
    path('ipladmin/', include('app_admin.urls', namespace='app_admin')),
]

urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls)),
                    ]
