from django.shortcuts import render

def bildirim(request):
    """Renders the notification page."""
    return render(request, 'hizmet_sunum_app/bildirim.html')

# Create your views here.
