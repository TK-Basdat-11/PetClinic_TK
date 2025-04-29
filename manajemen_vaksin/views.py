from django.shortcuts import render

def vaksin_dokter(request):
    return render(request, "dokter/vaksin_dokter.html")

def create_vaksin_dokter(request):
    return render(request, "dokter/create_vaksin_dokter.html")

def update_vaksin_dokter(request):
    return render(request, "dokter/update_vaksin_dokter.html")

def delete_vaksin_dokter(request):
    return render(request, "dokter/delete_vaksin_dokter.html")

def vaksin_perawat(request):
    return render(request, "perawat/vaksin_perawat.html")

def create_vaksin_perawat(request):
    return render(request, "perawat/create_vaksin_perawat.html")

def update_vaksin_perawat(request):
    return render(request, "perawat/update_vaksin_perawat.html")

def update_stok(request):
    return render(request, "perawat/update_stok.html")

def delete_vaksin_perawat(request):
    return render(request, "perawat/delete_vaksin_perawat.html")