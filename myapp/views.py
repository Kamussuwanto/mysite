

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import UploadedFile
from .forms import FileUploadForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

@never_cache
@login_required
def upload_file_view(request):
    user_files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')

    # If the user has no files, it returns None, so we default to 0

    # Replace the storage_dict and total_bytes_used lines
    #storage_dict = user_files.aggregate(total_size=Sum('file_size')) # file_size reads physical bytes
    #total_bytes_used = storage_dict['total_size'] or 0
    # with this:
    # Calculate current storage use in bytes using Python loop
    total_bytes_used = sum(f.file.size for f in user_files if f.file)

    # Define our 50MB quota cap limit in bytes (50 * 1024 * 1024)
    MAX_QUOTA_BYTES = 50 * 1024 * 1024

    # Convert to Megabytes for clean presentation variables
    mb_used = round(total_bytes_used / (1024 * 1024), 2)

    if request.method == 'POST':
        # Rule Check A: File Count Barrier (Max 10)
        if user_files.count() >= 10:
            messages.error(request, "Storage limit reached! You cannot upload more than 10 files.")
            return redirect('upload_file')

        # Rule Check B: Total Space Quota Barrier (Max 50MB)
        if total_bytes_used >= MAX_QUOTA_BYTES:
            messages.error(request, "Your 50MB storage space quota is completely full!")
            return redirect('upload_file')

        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = request.FILES['file']

            # Predictive Validation Check: Will this specific file push them over 50MB?
            if total_bytes_used + new_file.size > MAX_QUOTA_BYTES:
                messages.error(request, f"Upload rejected. This file ({round(new_file.size/(1024*1024), 2)}MB) will exceed your remaining 50MB quota space.")
                return redirect('upload_file')

            uploaded_item = form.save(commit=False)
            uploaded_item.user = request.user
            uploaded_item.save()
            messages.success(request, "File uploaded successfully!")
            return redirect('upload_file')
        else:
            messages.error(request, "Upload failed. Please check the errors below.")
    else:
        form = FileUploadForm()

    return render(request, 'myapp/upload.html', {
        'form': form,
        'files': user_files,
        'mb_used': mb_used,  # Send current space usage to HTML template view context
    })


@never_cache
@login_required
@require_POST  # Only accepts secure POST actions to prevent scraping/accidental hits
def delete_file_view(request, file_id):
    file_obj = get_object_or_404(UploadedFile, id=file_id)
    filename = file_obj.get_clean_filename()

    if file_obj.file and os.path.exists(file_obj.file.path):
        os.remove(file_obj.file.path)

    file_obj.delete()

    messages.success(request, f"Successfully removed: {filename}")

    # MATCH THIS: Use the exact 'name' from your urls.py
    return redirect('upload_file')


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically logs the user in after successful signup
            return redirect('upload_file')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})







