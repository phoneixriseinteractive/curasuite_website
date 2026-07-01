"""CuraSuite — Media Selectors"""
from django.db.models import QuerySet
from .models import MediaFile, MediaFolder


def get_all_files(file_type: str = None, folder=None) -> QuerySet:
    qs = MediaFile.objects.select_related("folder", "uploaded_by")
    if file_type:
        qs = qs.filter(file_type=file_type)
    if folder is not None:
        qs = qs.filter(folder=folder)
    return qs.order_by("-created_at")

def get_images() -> QuerySet:
    return get_all_files(file_type=MediaFile.FileType.IMAGE)

def get_file_by_id(pk) -> MediaFile | None:
    return MediaFile.objects.filter(pk=pk).first()

def search_files(query: str) -> QuerySet:
    return MediaFile.objects.filter(
        original_name__icontains=query
    ) | MediaFile.objects.filter(
        title__icontains=query
    ) | MediaFile.objects.filter(
        alt_text__icontains=query
    )

def get_root_folders() -> QuerySet:
    return MediaFolder.objects.filter(parent__isnull=True).order_by("name")
