from django.shortcuts import render

def vaksin_dokter(request):
    return render(request, "dokter/vaksin_dokter.html")

def create_vaksin_dokter(request):
    return render(request, "dokter/create_vaksin_dokter.html")

def update_vaksin_dokter(request):
    return render(request, "dokter/update_vaksin_dokter.html")

def delete_vaksin_dokter(request):
    return render(request, "dokter/delete_vaksin_dokter.html")