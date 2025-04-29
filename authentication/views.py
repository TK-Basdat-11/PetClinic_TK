from django.shortcuts import redirect, render

# Create your views here.


def show_login(request):

    if request.POST:
      data = request.POST  

      match data["email"]:
         
         case "dokter@example.com":
            return redirect('dashboard:dashboard_dokter')
         
         case "frontDeskOfficer@example.com":
            return redirect('dashboard:dashboard_fdo')
         
         case "klien@example.com":
            return redirect('dashboard:dashboard_klien')
         
         case "perawat@example.com":
            return redirect("dashboard:dashboard_perawat")

    return render(request,"login.html")

def hero_section(request):

    return render(request,"hero.html")

def user_logout(request):
   
   return redirect("authentication:hero")

def register(request):
    return render(request,"register.html")

def register_individu(request):
    return render(request,"register_individu.html")

def register_perusahaan(request):
    return render(request,"register_perusahaan.html")

def register_fdo(request):
    return render(request,"register_fdo.html")

def register_dokter(request):
    return render(request,"register_dokter.html")

def register_perawat(request):
    return render(request,"register_perawat.html")