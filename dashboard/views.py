from django.contrib import messages
from django.db import connection
from django.shortcuts import render, redirect
from datetime import datetime
from authentication.decorators import role_required

BULAN_INDONESIA = {
    'January': 'Januari',
    'February': 'Februari',
    'March': 'Maret',
    'April': 'April',
    'May': 'Mei',
    'June': 'Juni',
    'July': 'Juli',
    'August': 'Agustus',
    'September': 'September',
    'October': 'Oktober',
    'November': 'November',
    'December': 'Desember'
}

def format_tanggal_indonesia(date_obj):
    day = date_obj.day
    month = BULAN_INDONESIA[date_obj.strftime("%B")]
    year = date_obj.year
    return f"{day} {month} {year}"

@role_required('dokter')
def dashboard_dokter(request):
    dokter_id = request.session.get("user_id")
    if not dokter_id:
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        # Ambil profil dokter lengkap
        cursor.execute("""
            SELECT d.no_dokter_hewan, tm.no_izin_praktik, p.email, 
                   TO_CHAR(p.tanggal_mulai_kerja, 'YYYY-MM-DD'), 
                   TO_CHAR(p.tanggal_akhir_kerja, 'YYYY-MM-DD'), 
                   u.alamat, u.nomor_telepon
            FROM PETCLINIC.DOKTER_HEWAN d
            JOIN PETCLINIC.PEGAWAI p ON p.no_pegawai = d.no_dokter_hewan
            JOIN PETCLINIC.TENAGA_MEDIS tm ON tm.no_tenaga_medis = d.no_dokter_hewan
            JOIN PETCLINIC.USERS u ON u.email = p.email
            WHERE d.no_dokter_hewan = %s
        """, [dokter_id])
        row = cursor.fetchone()

        if not row:
            return redirect("authentication:login")

        tanggal_diterima = datetime.strptime(row[3], "%Y-%m-%d")
        tanggal_diterima_fmt = format_tanggal_indonesia(tanggal_diterima)

        if row[4] is None:
            tanggal_akhir_fmt = "-"
        else:
            tanggal_akhir = datetime.strptime(row[4], "%Y-%m-%d")
            tanggal_akhir_fmt = format_tanggal_indonesia(tanggal_akhir)

        profile = {
            "id": row[0],
            "izin": row[1],
            "email": row[2],
            "diterima": tanggal_diterima_fmt,
            "akhir": tanggal_akhir_fmt,
            "alamat": row[5],
            "telepon": row[6],
        }

        # Ambil sertifikat
        cursor.execute("""
            SELECT no_sertifikat_kompetensi, nama_sertifikat
            FROM PETCLINIC.SERTIFIKAT_KOMPETENSI
            WHERE no_tenaga_medis = %s
        """, [dokter_id])
        sertifikat_list = cursor.fetchall()

        # Ambil jadwal praktik
        cursor.execute("""
            SELECT hari, jam
            FROM PETCLINIC.JADWAL_PRAKTIK
            WHERE no_dokter_hewan = %s
            ORDER BY 
              CASE hari
                WHEN 'Senin' THEN 1
                WHEN 'Selasa' THEN 2
                WHEN 'Rabu' THEN 3
                WHEN 'Kamis' THEN 4
                WHEN 'Jumat' THEN 5
                WHEN 'Sabtu' THEN 6
                ELSE 7
              END
        """, [dokter_id])
        jadwal_list = cursor.fetchall()

    return render(request, "dashboard/dashboard_dokter.html", {
        "profile": profile,
        "sertifikat_list": sertifikat_list,
        "jadwal_list": jadwal_list,
        "user_role": "dokter",
    })

@role_required('fdo')
def dashboard_fdo(request):
    fdo_id = request.session.get("user_id")
    if not fdo_id:
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.no_front_desk, p.email,
                   TO_CHAR(p.tanggal_mulai_kerja, 'YYYY-MM-DD'),
                   TO_CHAR(p.tanggal_akhir_kerja, 'YYYY-MM-DD'),
                   u.alamat, u.nomor_telepon
            FROM PETCLINIC.FRONT_DESK f
            JOIN PETCLINIC.PEGAWAI p ON p.no_pegawai = f.no_front_desk
            JOIN PETCLINIC.USERS u ON u.email = p.email
            WHERE f.no_front_desk = %s
        """, [fdo_id])
        row = cursor.fetchone()

        if not row:
            return redirect("authentication:login")

        tanggal_diterima = datetime.strptime(row[2], "%Y-%m-%d")
        tanggal_diterima_fmt = format_tanggal_indonesia(tanggal_diterima)

        if row[3] is None:
            tanggal_akhir_fmt = "-"
        else:
            tanggal_akhir = datetime.strptime(row[3], "%Y-%m-%d")
            tanggal_akhir_fmt = format_tanggal_indonesia(tanggal_akhir)

        profile = {
            "id": row[0],
            "email": row[1],
            "diterima": tanggal_diterima_fmt,
            "akhir": tanggal_akhir_fmt,
            "alamat": row[4],
            "telepon": row[5],
        }

    return render(request, "dashboard/dashboard_fdo.html", {
        "profile": profile,
        "user_role": "fdo",
    })

@role_required('klien')
def dashboard_klien(request):
    client_id = request.session.get('user_id')
    if not client_id:
        return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.no_identitas, u.email,
                   CASE
                        WHEN i.nama_depan IS NOT NULL THEN TRIM(CONCAT_WS(' ', i.nama_depan, i.nama_tengah, i.nama_belakang))
                        ELSE p.nama_perusahaan
                   END AS nama,
                   TO_CHAR(k.tanggal_registrasi, 'YYYY-MM-DD') AS tanggal,
                   u.alamat, u.nomor_telepon
            FROM PETCLINIC.KLIEN k
            JOIN PETCLINIC.USERS u ON u.email = k.email
            LEFT JOIN PETCLINIC.INDIVIDU i ON k.no_identitas = i.no_identitas_klien
            LEFT JOIN PETCLINIC.PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
            WHERE k.no_identitas = %s
        """, [client_id])
        row = cursor.fetchone()

        if not row:
            messages.error(request, "Data klien tidak ditemukan.")
            return redirect('authentication:login')

        tanggal_obj = datetime.strptime(row[3], '%Y-%m-%d')
        tanggal_formatted = format_tanggal_indonesia(tanggal_obj)

        profile = {
            'id': row[0],
            'email': row[1],
            'nama': row[2],
            'tanggal': tanggal_formatted,
            'alamat': row[4],
            'telepon': row[5],
        }

    return render(request, 'dashboard/dashboard_klien.html', {
        'profile': profile,
        'user_role': 'klien',
    })

@role_required('perawat')
def dashboard_perawat(request):
    perawat_id = request.session.get("user_id")
    if not perawat_id:
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        # Ambil data profil
        cursor.execute("""
            SELECT ph.no_perawat_hewan, tm.no_izin_praktik, p.email,
                   TO_CHAR(p.tanggal_mulai_kerja, 'YYYY-MM-DD'),
                   TO_CHAR(p.tanggal_akhir_kerja, 'YYYY-MM-DD'),
                   u.alamat, u.nomor_telepon
            FROM PETCLINIC.PERAWAT_HEWAN ph
            JOIN PETCLINIC.PEGAWAI p ON p.no_pegawai = ph.no_perawat_hewan
            JOIN PETCLINIC.TENAGA_MEDIS tm ON tm.no_tenaga_medis = ph.no_perawat_hewan
            JOIN PETCLINIC.USERS u ON u.email = p.email
            WHERE ph.no_perawat_hewan = %s
        """, [perawat_id])
        row = cursor.fetchone()
        print(row)
        print(row[3])
        if not row:
            return redirect("authentication:login")

        tanggal_diterima = datetime.strptime(row[3], "%Y-%m-%d")
        tanggal_diterima_fmt = format_tanggal_indonesia(tanggal_diterima)

        if row[4] is None:
            tanggal_akhir_fmt = "-"
        else:
            tanggal_akhir = datetime.strptime(row[4], "%Y-%m-%d")
            tanggal_akhir_fmt = format_tanggal_indonesia(tanggal_akhir)

        profile = {
            "id": row[0],
            "izin": row[1],
            "email": row[2],
            "diterima": tanggal_diterima_fmt,
            "akhir": tanggal_akhir_fmt,
            "alamat": row[5],
            "telepon": row[6],
        }

        # Ambil sertifikat
        cursor.execute("""
            SELECT no_sertifikat_kompetensi, nama_sertifikat
            FROM PETCLINIC.SERTIFIKAT_KOMPETENSI
            WHERE no_tenaga_medis = %s
        """, [perawat_id])
        sertifikat_list = cursor.fetchall()

    return render(request, "dashboard/dashboard_perawat.html", {
        "profile": profile,
        "sertifikat_list": sertifikat_list,
        "user_role": "perawat",
    })

def update_password(request):
    user_email = request.session.get("email")
    if not user_email:
        messages.error(request, "Anda belum login.")
        return redirect("authentication:login")

    user_role = request.session.get('user_role')
    print(user_role)

    if user_role == 'klien':
        cancel_url = 'dashboard:dashboard_klien'
    elif user_role == 'dokter':
        cancel_url = 'dashboard:dashboard_dokter'
    elif user_role == 'perawat':
        cancel_url = 'dashboard:dashboard_perawat'
    elif user_role == 'fdo':
        cancel_url = 'dashboard:dashboard_fdo'
    else:
        cancel_url = 'authentication:login'

    if request.method == "POST":
        password_lama = request.POST.get("current_password")
        password_baru = request.POST.get("new_password")
        konfirmasi = request.POST.get("confirm_password")

        if not password_lama:
            messages.error(request, "Semua field wajib diisi.")
            return redirect('dashboard:update_password')
        
        if not password_baru:
            messages.error(request, "Semua field wajib diisi.")
            return redirect('dashboard:update_password')

        if not konfirmasi:
                    messages.error(request, "Semua field wajib diisi.")
                    return redirect('dashboard:update_password')

        if password_baru != konfirmasi:
            messages.error(request, "Konfirmasi password tidak sesuai.")
            return redirect('dashboard:update_password')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM PETCLINIC.USERS
                WHERE email = %s AND password_user = %s
            """, [user_email, password_lama])
            valid = cursor.fetchone()

        if not valid:
            messages.error(request, "Password lama tidak sesuai.")
            return redirect('dashboard:update_password')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PETCLINIC.USERS
                SET password_user = %s
                WHERE email = %s
            """, [password_baru, user_email])
        
        request.session["email"] = user_email
        request.session["user_role"] = user_role

        messages.success(request, "Password berhasil diperbarui.")
        return redirect(cancel_url)

    return render(request, 'update_password.html', {
        'cancel_url': cancel_url
    })

@role_required('dokter')
def update_profile_dokter(request):
    return render(request, "dashboard/update_profile_dokter.html")

@role_required('fdo')
def update_profile_fdo(request):
    return render(request, "dashboard/update_profile_fdo.html")

@role_required('perawat')
def update_profile_perawat(request):
    return render(request, "dashboard/update_profile_perawat.html")

@role_required('klien')
def update_profile_klien_individu(request):
    return render(request, "dashboard/update_profile_klien_individu.html")

@role_required('klien')
def update_profile_klien_perusahaan(request):
    return render(request, "dashboard/update_profile_klien_perusahaan.html")