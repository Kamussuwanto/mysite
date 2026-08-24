
import os
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Add this function so the old migration file stops crashing

def validate_file_size(value):
    MAX_FILE_SIZE = 50 * 1024 * 1024  # Raise to 50 Megabytes
    if value.size > MAX_FILE_SIZE:
        raise ValidationError("File size exceeds the 50MB storage ceiling limit.")
    return value


class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='user_uploads/', validators=[validate_file_size])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

    # 1. Clean filename extractor method
    def get_clean_filename(self):
        return os.path.basename(self.file.name)

    # 2. Existing icon method (Keep ONLY this one copy)
    def get_icon(self):
        # os.path.splitext returns (root, ext) tuple. [1] extracts the extension string.
        ext = os.path.splitext(self.file.name)[1].lower()

        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']
        document_exts = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
        spreadsheet_exts = ['.xls', '.xlsx', '.csv', '.ods']
        archive_exts = ['.zip', '.tar', '.gz', '.rar', '.7z']
        audio_video_exts = ['.mp3', '.wav', '.mp4', '.mkv', '.avi', '.mov']

        if ext in image_exts:
            return "🖼️"
        elif ext in document_exts:
            return "📄"
        elif ext in spreadsheet_exts:
            return "📊"
        elif ext in archive_exts:
            return "📦"
        elif ext in audio_video_exts:
            return "🎬"
        return "📁"
