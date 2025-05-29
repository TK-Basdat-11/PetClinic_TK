# Create your views here.
from django.db import connection, InternalError
from django.shortcuts import render, redirect
from django.contrib import messages

from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages

import uuid

def login(request):
    if request.method != "POST":
        return render(request, "login.html")

    email    = request.POST["email"].strip().lower()
    password = request.POST["password"]

    with connection.cursor() as cur:
        cur.execute(
            "SELECT password_user FROM PETCLINIC.USERS WHERE email = %s",
            [email]
        )
        row = cur.fetchone()
        if not row or row[0] != password:
            messages.error(request, "Email atau password salah.")
            return render(request, "login.html")

        cur.execute(
            """
            SELECT role, id_user
            FROM (
                /* — Dokter — */
                SELECT 'dokter' AS role, d.no_dokter_hewan AS id_user
                FROM   PETCLINIC.DOKTER_HEWAN d
                JOIN   PETCLINIC.PEGAWAI      p ON p.no_pegawai = d.no_dokter_hewan
                WHERE  p.email = %s

                UNION ALL
                /* — Perawat — */
                SELECT 'perawat' AS role, ph.no_perawat_hewan AS id_user
                FROM   PETCLINIC.PERAWAT_HEWAN ph
                JOIN   PETCLINIC.PEGAWAI       p ON p.no_pegawai = ph.no_perawat_hewan
                WHERE  p.email = %s

                UNION ALL
                /* — FDO — */
                SELECT 'fdo' AS role, fd.no_front_desk AS id_user
                FROM   PETCLINIC.FRONT_DESK fd
                JOIN   PETCLINIC.PEGAWAI    p ON p.no_pegawai = fd.no_front_desk
                WHERE  p.email = %s

                UNION ALL
                /* — Klien — */
                SELECT 'klien' AS role, KLIEN.no_identitas AS id_user
                FROM   PETCLINIC.KLIEN
                WHERE  email = %s
            ) AS roles
            LIMIT 1;
            """,
            [email, email, email, email]
        )
        role_row = cur.fetchone()
        if role_row:
            role, user_id = role_row
        else:
            role, user_id = "guest", None

    request.session["is_auth"]   = True
    request.session["email"]     = email
    request.session["user_role"] = role
    request.session["user_id"] = str(user_id) if user_id else None
    

    messages.success(request, f"Selamat datang, {email}!")
    
    if role == "dokter":
        return redirect('dashboard:dashboard_dokter')
    elif role == "fdo":
        return redirect('dashboard:dashboard_fdo')
    elif role == "klien":
        return redirect('dashboard:dashboard_klien')
    elif role == "perawat":
        return redirect('dashboard:dashboard_perawat')
    else:
        return redirect("authentication:hero")

# def show_login(request):
#     if request.method == "POST":
#         return login(request)
#     return render(request, "login.html")

def hero_section(request):
    return render(request,"hero.html")

def user_logout(request):
   if "is_auth" in request.session:
       del request.session["is_auth"]
   if "email" in request.session:
       del request.session["email"]
   if "user_role" in request.session:
       del request.session["user_role"]
   
   messages.success(request, "You have been logged out successfully.")
   return redirect("authentication:hero")

def register(request):
    return render(request,"register.html")

def register_individu(request):
    if request.method == "POST":
        email          = request.POST["email"].strip().lower()
        password       = request.POST["password"]
        nama_depan     = request.POST["nama_depan"]
        nama_tengah    = request.POST.get("nama_tengah")  # boleh None
        nama_belakang  = request.POST["nama_belakang"]
        nomor_telepon  = request.POST["nomor_telepon"]
        alamat         = request.POST["alamat"]

        no_identitas = uuid.uuid4()
    
        try:
            with connection.cursor() as cur:
                # USERS ----------------------------------------------------------
                cur.execute(
                    """INSERT INTO PETCLINIC.USERS
                       (email, password_user, alamat, nomor_telepon)
                       VALUES (%s, %s, %s, %s)""",
                    [email, password, alamat, nomor_telepon]
                )
                # KLIEN ----------------------------------------------------------
                cur.execute(
                    """INSERT INTO PETCLINIC.KLIEN
                       (no_identitas, tanggal_registrasi, email)
                       VALUES (%s, CURRENT_DATE, %s)""",
                    [no_identitas, email]
                )
                # INDIVIDU -------------------------------------------------------
                cur.execute(
                    """INSERT INTO PETCLINIC.INDIVIDU
                       (no_identitas_klien, nama_depan, nama_tengah, nama_belakang)
                       VALUES (%s, %s, %s, %s)""",
                    [no_identitas, nama_depan, nama_tengah, nama_belakang]
                )

            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect("authentication:login")
        except InternalError as e:
            error_msg = str(e)
            if "ERROR:" in error_msg:
                error_msg = error_msg.split("ERROR:")[1].strip()
                if "CONTEXT:" in error_msg:
                    error_msg = error_msg.split("CONTEXT:")[0].strip()
            messages.error(request, error_msg)
            return render(request, "register_individu.html")

    return render(request, "register_individu.html")
	
def register_perusahaan(request):
    if request.method == "POST":
        email          = request.POST["email"].strip().lower()
        password       = request.POST["password"]
        nama_perusahaan= request.POST["nama_perusahaan"]
        nomor_telepon  = request.POST["nomor_telepon"]
        alamat         = request.POST["alamat"]

        no_identitas = uuid.uuid4()

        try:
            with connection.cursor() as cur:
                cur.execute(
                    """INSERT INTO PETCLINIC.USERS
                       (email, password_user, alamat, nomor_telepon)
                       VALUES (%s, %s, %s, %s)""",
                    [email, password, alamat, nomor_telepon]
                )
                cur.execute(
                    """INSERT INTO PETCLINIC.KLIEN
                       (no_identitas, tanggal_registrasi, email)
                       VALUES (%s, CURRENT_DATE, %s)""",
                    [no_identitas, email]
                )
                cur.execute(
                    """INSERT INTO PETCLINIC.PERUSAHAAN
                       (no_identitas_klien, nama_perusahaan)
                       VALUES (%s, %s)""",
                    [no_identitas, nama_perusahaan]
                )

            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect("authentication:login")
        except InternalError as e:
            error_msg = str(e)
            if "ERROR:" in error_msg:
                error_msg = error_msg.split("ERROR:")[1].strip()
                if "CONTEXT:" in error_msg:
                    error_msg = error_msg.split("CONTEXT:")[0].strip()
            messages.error(request, error_msg)
            return render(request, "register_perusahaan.html")

    return render(request, "register_perusahaan.html")

def register_fdo(request):
    if request.method == "POST":
        email            = request.POST["email"].strip().lower()
        password         = request.POST["password"]
        nomor_telepon    = request.POST["nomor_telepon"]
        tanggal_diterima = request.POST["tanggal_diterima"]  # YYYY-MM-DD
        alamat           = request.POST["alamat"]

        no_pegawai = uuid.uuid4()          # juga jadi PK FRONT_DESK

        try:
            with connection.cursor() as cur:
                # USERS
                cur.execute(
                    """INSERT INTO PETCLINIC.USERS
                       (email, password_user, alamat, nomor_telepon)
                       VALUES (%s, %s, %s, %s)""",
                    [email, password, alamat, nomor_telepon]
                )
                # PEGAWAI
                cur.execute(
                    """INSERT INTO PETCLINIC.PEGAWAI
                       (no_pegawai, tanggal_mulai_kerja, email)
                       VALUES (%s, %s, %s)""",
                    [no_pegawai, tanggal_diterima, email]
                )
                # FRONT_DESK
                cur.execute(
                    """INSERT INTO PETCLINIC.FRONT_DESK
                       (no_front_desk) VALUES (%s)""",
                    [no_pegawai]
                )

            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect("authentication:login")
        except InternalError as e:
            error_msg = str(e)
            if "ERROR:" in error_msg:
                error_msg = error_msg.split("ERROR:")[1].strip()
                if "CONTEXT:" in error_msg:
                    error_msg = error_msg.split("CONTEXT:")[0].strip()
            messages.error(request, error_msg)
            return render(request, "register_fdo.html")

    return render(request, "register_fdo.html")

def register_dokter(request):
    if request.method == "POST":
        email            = request.POST["email"].strip().lower()
        password         = request.POST["password"]
        no_izin_praktik  = request.POST["izin_praktik"]
        nomor_telepon    = request.POST["nomor_telepon"]
        tanggal_diterima = request.POST["tanggal_diterima"]
        alamat           = request.POST["alamat"]

        nomor_sertifikat = request.POST.getlist("nomor_sertifikat[]")
        nama_sertifikat  = request.POST.getlist("nama_sertifikat[]")
        hari_list        = request.POST.getlist("hari[]")
        jam_list         = request.POST.getlist("jam[]")

        no_pegawai = uuid.uuid4()          # PK untuk seluruh rantai

        try:
            with connection.cursor() as cur:
                # USERS
                cur.execute(
                    """INSERT INTO PETCLINIC.USERS
                       (email, password_user, alamat, nomor_telepon)
                       VALUES (%s, %s, %s, %s)""",
                    [email, password, alamat, nomor_telepon]
                )
                # PEGAWAI
                cur.execute(
                    """INSERT INTO PETCLINIC.PEGAWAI
                       (no_pegawai, tanggal_mulai_kerja, email)
                       VALUES (%s, %s, %s)""",
                    [no_pegawai, tanggal_diterima, email]
                )
                # TENAGA_MEDIS
                cur.execute(
                    """INSERT INTO PETCLINIC.TENAGA_MEDIS
                       (no_tenaga_medis, no_izin_praktik)
                       VALUES (%s, %s)""",
                    [no_pegawai, no_izin_praktik]
                )
                # DOKTER_HEWAN
                cur.execute(
                    """INSERT INTO PETCLINIC.DOKTER_HEWAN
                       (no_dokter_hewan) VALUES (%s)""",
                    [no_pegawai]
                )
                # SERTIFIKAT
                for no_ser, nm_ser in zip(nomor_sertifikat, nama_sertifikat):
                    if no_ser and nm_ser:
                        cur.execute(
                            """INSERT INTO PETCLINIC.SERTIFIKAT_KOMPETENSI
                               (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat)
                               VALUES (%s, %s, %s)""",
                            [no_ser, no_pegawai, nm_ser]
                        )
                # JADWAL
                for hari, jam in zip(hari_list, jam_list):
                    if hari and jam:
                        cur.execute(
                            """INSERT INTO PETCLINIC.JADWAL_PRAKTIK
                               (no_dokter_hewan, hari, jam)
                               VALUES (%s, %s, %s)""",
                            [no_pegawai, hari, jam]
                        )

            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect("authentication:login")
        except InternalError as e:
            error_msg = str(e)
            if "ERROR:" in error_msg:
                error_msg = error_msg.split("ERROR:")[1].strip()
                if "CONTEXT:" in error_msg:
                    error_msg = error_msg.split("CONTEXT:")[0].strip()
            messages.error(request, error_msg)
            return render(request, "register_dokter.html")

    return render(request, "register_dokter.html")


def register_perawat(request):
    if request.method == "POST":
        email            = request.POST["email"].strip().lower()
        password         = request.POST["password"]
        no_izin_praktik  = request.POST["izin_praktik"]
        nomor_telepon    = request.POST["nomor_telepon"]
        tanggal_diterima = request.POST["tanggal_diterima"]
        alamat           = request.POST["alamat"]

        nomor_sertifikat = request.POST.getlist("nomor_sertifikat[]")
        nama_sertifikat  = request.POST.getlist("nama_sertifikat[]")

        no_pegawai = uuid.uuid4()

        try:
            with connection.cursor() as cur:
                # USERS
                cur.execute(
                    """INSERT INTO PETCLINIC.USERS
                       (email, password_user, alamat, nomor_telepon)
                       VALUES (%s, %s, %s, %s)""",
                    [email, password, alamat, nomor_telepon]
                )
                # PEGAWAI
                cur.execute(
                    """INSERT INTO PETCLINIC.PEGAWAI
                       (no_pegawai, tanggal_mulai_kerja, email)
                       VALUES (%s, %s, %s)""",
                    [no_pegawai, tanggal_diterima, email]
                )
                # TENAGA_MEDIS
                cur.execute(
                    """INSERT INTO PETCLINIC.TENAGA_MEDIS
                       (no_tenaga_medis, no_izin_praktik)
                       VALUES (%s, %s)""",
                    [no_pegawai, no_izin_praktik]
                )
                # PERAWAT_HEWAN
                cur.execute(
                    """INSERT INTO PETCLINIC.PERAWAT_HEWAN
                       (no_perawat_hewan) VALUES (%s)""",
                    [no_pegawai]
                )
                # SERTIFIKAT
                for no_ser, nm_ser in zip(nomor_sertifikat, nama_sertifikat):
                    if no_ser and nm_ser:
                        cur.execute(
                            """INSERT INTO PETCLINIC.SERTIFIKAT_KOMPETENSI
                               (no_sertifikat_kompetensi, no_tenaga_medis, nama_sertifikat)
                               VALUES (%s, %s, %s)""",
                            [no_ser, no_pegawai, nm_ser]
                        )

            messages.success(request, "Registrasi berhasil! Silakan login.")
            return redirect("authentication:login")
        except InternalError as e:
            error_msg = str(e)
            if "ERROR:" in error_msg:
                error_msg = error_msg.split("ERROR:")[1].strip()
                if "CONTEXT:" in error_msg:
                    error_msg = error_msg.split("CONTEXT:")[0].strip()
            messages.error(request, error_msg)
            return render(request, "register_perawat.html")

    return render(request, "register_perawat.html")

def hero_section(request):

    return render(request,"hero.html")

def user_logout(request):
   
    request.session['user_type'] = "empty"
    request.session['user_id'] = "empty"
   
    return redirect("authentication:hero")

def get_klien_joined_with_users_data_from_id(id):

    dto_klien = dict()

    with connection.cursor() as cursor:

        cursor.execute(
        "SELECT * FROM USERS u " \
        "JOIN KLIEN k " \
        "ON u.email = k.email " \
        "WHERE k.no_identitas = %s", (id,))

        klien_raw = cursor.fetchone()

        dto_klien = {
            "email": klien_raw[0],
            # "password_user": klien_raw[1],
            "alamat": klien_raw[2],
            "nomor_telepon": klien_raw[3],
            # "no_identitas": klien_raw[4],
            "tanggal_registrasi": klien_raw[5]
        }

    return dto_klien

def get_nama_klien_from_individu(id):

    nama = ""

    with connection.cursor() as cursor:

        cursor.execute("SELECT * FROM PETCLINIC.INDIVIDU WHERE no_identitas_klien=%s",(id,))

        klien_raw = cursor.fetchone()

        if klien_raw:
            nama = f"{klien_raw[1]} {klien_raw[2]} {klien_raw[3]}"

        else:
            cursor.execute("SELECT nama_perusahaan FROM PETCLINIC.PERUSAHAAN WHERE no_identitas_klien=%s",(id,))
            klien_raw = cursor.fetchone()

            nama = klien_raw[0]


    return nama