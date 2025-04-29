from django.shortcuts import render

# Create your views here.

def jenis_hewan(request):
    return render(request, "jenis_hewan.html")