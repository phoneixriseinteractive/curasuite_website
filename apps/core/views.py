"""CuraSuite — Core Views."""
from django.shortcuts import render


def search_view(request):
    query = request.GET.get("q", "").strip()
    results = {"query": query, "pages": [], "blogs": [], "products": []}
    # TODO: implement full-text search using GIN indexes
    return render(request, "core/search.html", results)
