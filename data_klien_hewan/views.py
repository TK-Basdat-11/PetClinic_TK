from django.shortcuts import render

def list_klien(request):
    return render(request, "list_klien.html")

def detail_individu(request):
    return render(request, "detail_individu.html")

def detail_perusahaan(request):
    return render(request, "detail_perusahaan.html")