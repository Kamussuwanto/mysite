from django import forms
from django.core.exceptions import ValidationError
from .models import UploadedFile

# Configurable constraints
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 Megabytes
BANNED_EXTENSIONS = ['.exe', '.bat', '.sh', '.py', '.php', '.js']

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # 1. Size Validation
            if file.size > MAX_FILE_SIZE:
                raise ValidationError("File size exceeds the maximum limit of 5MB.")

            # 2. Extension Validation
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext in BANNED_EXTENSIONS:
                raise ValidationError(f"Files with extension {ext} are not allowed for security reasons.")

        return file
