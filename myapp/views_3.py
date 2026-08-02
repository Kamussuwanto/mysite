# To this correct version:


# Replace it with this line:
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from .models import UploadedFile
from .forms import FileUploadForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum  # <-- Add this import at the top of the file

"""

@never_cache
@login_required
def upload_file_view(request):
    # Query files belonging only to the current user
    user_files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')

    if request.method == 'POST':
        # 1. Enforce the 10-file storage limit barrier
        if user_files.count() >= 10:
            messages.error(request, "Storage limit reached! You cannot upload more than 10 files.")
            return redirect('upload_file')

        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
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
        'files': user_files
    })

"""

@never_cache
@login_required
def upload_file_view(request):
    user_files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')

    # 1. Calculate current storage use in bytes
    # If the user has no files, it returns None, so we default to 0
    storage_dict = user_files.aggregate(total_size=Sum('file__size')) # file__size reads physical bytes

    total_bytes_used = storage_dict['total_size'] or 0

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
def delete_file_view(request, file_id):
    # Security barrier: Ensures users can't delete files belonging to other users
    file_item = get_object_or_404(UploadedFile, id=file_id, user=request.user)

    # Delete the physical file asset from storage
    if file_item.file:
        file_item.file.delete(save=False)

    file_item.delete()
    messages.success(request, "File removed safely.")
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

