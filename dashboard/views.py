from django.shortcuts import render

def dashboard_dokter(request):
    return render(request, "dashboard/dashboard_dokter.html")

def dashboard_fdo(request):
    return render(request, "dashboard/dashboard_fdo.html")

def dashboard_klien(request):
    # In a real app, this would be determined by database query
    # For now, we'll default to 'individu' (can be 'individu' or 'perusahaan')
    client_type = request.session.get('client_type', 'individu')
    return render(request, "dashboard/dashboard_klien.html", {'client_type': client_type})

def dashboard_perawat(request):
    return render(request, "dashboard/dashboard_perawat.html")

def update_password(request):
    return render(request, "update_password.html")

def update_profile_dokter(request):
    return render(request, "dashboard/update_profile_dokter.html")

def update_profile_fdo(request):
    return render(request, "dashboard/update_profile_fdo.html")

def update_profile_perawat(request):
    return render(request, "dashboard/update_profile_perawat.html")

def update_profile_klien_individu(request):
    return render(request, "dashboard/update_profile_klien_individu.html")

def update_profile_klien_perusahaan(request):
    return render(request, "dashboard/update_profile_klien_perusahaan.html")