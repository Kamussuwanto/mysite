
"""
from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    # Displays these columns in the admin panel list view
    list_display = ('title', 'file', 'uploaded_at')

    # Adds a sidebar filter based on the upload date
    list_filter = ('uploaded_at',)

    # Enables a search bar at the top to search by title
    search_fields = ('title',)

"""
from django.contrib import admin
from .models import UploadedFile

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    # Change 'title' to 'file' here to match your model attributes
    list_display = ('file', 'user', 'uploaded_at')
