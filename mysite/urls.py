from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from myapp import views  # Imports all views from your app

# Smart root view: controls where users land based on login status
def smart_root_view(request):
    if request.user.is_authenticated:
        return redirect('upload_file')
    return redirect('login')

urlpatterns = [
    # 1. Root Domain
    path('', smart_root_view, name='root'),

    # 2. Django Built-in Admin
    path('admin/', admin.site.urls),

    # 3. Authentication Routes (Built-in + Custom Signup)
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')), # Provides login/logout

    # 4. Core Application File Management Routes
    path('upload/', views.upload_file_view, name='upload_file'),
    path('upload/delete/<int:file_id>/', views.delete_file_view, name='delete_file'),
]

# Append media and static configurations for local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
