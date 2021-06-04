from services.models import Service

def services(request):
    return {"services": Service.objects.all()}