from .models import Country

def countries_context(request):
    return {
        'countries': Country.objects.all()
    }
