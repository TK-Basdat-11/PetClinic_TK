from django.shortcuts import render

def dashboard_dokter(request):
    return render(request, "dashboard/dashboard_dokter.html")

def dashboard_fdo(request):
    return render(request, "dashboard/dashboard_fdo.html")

def dashboard_klien(request):
    return render(request, "dashboard/dashboard_klien.html")

def dashboard_perawat(request):
    return render(request, "dashboard/dashboard_perawat.html")

def update_password(request):
    return render(request, "update_password.html")