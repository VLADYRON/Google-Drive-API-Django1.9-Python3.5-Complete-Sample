from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    #url(r'^plus/', include('plus.urls')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url(r'^admin/', admin.site.urls),
    url(r'^$','Workspace.views.index'),
    url(r'^oauth2callback', 'Workspace.views.auth_return')
]
