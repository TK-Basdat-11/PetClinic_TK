from django.shortcuts import render

# Create your views here.
def list_treatment(request):
    return render(request, 'list_treatment.html')
    
def create_treatment(request):
    return render(request, 'create_treatment.html')
    
def update_treatment(request):
    return render(request, 'update_treatment.html')
    
def delete_treatment(request):
    return render(request, 'delete_treatment.html')

def list_kunjungan(request):
    return render(request, 'list_kunjungan.html')

def create_kunjungan(request):
    return render(request, 'create_kunjungan.html')

def update_kunjungan(request):
    return render(request, 'update_kunjungan.html')

def delete_kunjungan(request):
    return render(request, 'delete_kunjungan.html')

def rekam_medis(request):
    return render(request, 'rekam_medis.html')

def create_rekam_medis(request):
    return render(request, 'create_rekam_medis.html')

def update_rekam_medis(request):
    return render(request, 'update_rekam_medis.html')

def rekam_medis_unavailable(request):
    return render(request, 'rekam_medis_unavailable.html')
