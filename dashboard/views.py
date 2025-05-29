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

        cursor.execute("""
            SELECT no_sertifikat_kompetensi, nama_sertifikat
            FROM PETCLINIC.SERTIFIKAT_KOMPETENSI
            WHERE no_tenaga_medis = %s
        """, [dokter_id])
        sertifikat_list = cursor.fetchall()

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

    notices = connection.connection.notices
    if notices:
        latest_notice = notices[-1]
        messages.info(request, latest_notice.strip())

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
                   u.alamat, u.nomor_telepon,
                   CASE
                        WHEN i.nama_depan IS NOT NULL THEN 'individu'
                        ELSE 'perusahaan'
                   END AS client_type
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

        client_type = row[6]

    return render(request, 'dashboard/dashboard_klien.html', {
        'profile': profile,
        'user_role': 'klien',
        'client_type': client_type,  
    })

@role_required('perawat')
def dashboard_perawat(request):
    perawat_id = request.session.get("user_id")
    if not perawat_id:
        return redirect("authentication:login")

    with connection.cursor() as cursor:
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
    user_email = request.session.get("email")
    no_dokter = request.session.get("user_id")

    if not user_email or not no_dokter:
        messages.error(request, "Anda belum login.")
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.alamat, u.nomor_telepon, TO_CHAR(p.tanggal_akhir_kerja, 'YYYY-MM-DD')
            FROM PETCLINIC.USERS u
            JOIN PETCLINIC.PEGAWAI p ON p.email = u.email
            WHERE p.no_pegawai = %s
        """, [no_dokter])
        result = cursor.fetchone()

        if not result:
            messages.error(request, "Data dokter tidak ditemukan.")
            return redirect("dashboard:dashboard_dokter")

        alamat_awal, telepon_awal, akhir_kerja_awal = result

        cursor.execute("""
            SELECT no_sertifikat_kompetensi, nama_sertifikat
            FROM PETCLINIC.SERTIFIKAT_KOMPETENSI
            WHERE no_tenaga_medis = %s
        """, [no_dokter])
        sertifikat_list = cursor.fetchall()

        cursor.execute("""
            SELECT hari, jam
            FROM PETCLINIC.JADWAL_PRAKTIK
            WHERE no_dokter_hewan = %s
        """, [no_dokter])
        hasil_query_jadwal = cursor.fetchall()

    jadwal_list = []
    for jadwal in hasil_query_jadwal:
        hari = jadwal[0]
        jam = jadwal[1] or ""
        jadwal_list.append((hari, jam))

    if request.method == "POST":
        alamat = request.POST.get("alamat", "").strip()
        telepon = request.POST.get("telepon", "").strip()
        akhir_kerja = request.POST.get("akhir_kerja", "").strip()

        if not alamat or not telepon:
            messages.error(request, "Alamat dan nomor telepon wajib diisi.")
            return redirect("dashboard:update_profile_dokter")

        cert_numbers = request.POST.getlist("certificate_number[]")
        cert_names = request.POST.getlist("certificate_name[]")
        
        if not cert_numbers or not cert_names or not cert_numbers[0] or not cert_names[0]:
            messages.error(request, "Minimal satu sertifikat kompetensi wajib diisi.")
            return redirect("dashboard:update_profile_dokter")

        days = request.POST.getlist("day[]")
        schedule_times = request.POST.getlist("schedule_time[]")
        
        if not akhir_kerja: 
            if not days or not schedule_times or not days[0] or not schedule_times[0]:
                messages.error(request, "Minimal satu jadwal praktik wajib diisi.")
                return redirect("dashboard:update_profile_dokter")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PETCLINIC.USERS
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, telepon, user_email])

            if akhir_kerja:
                cursor.execute("""
                    UPDATE PETCLINIC.PEGAWAI
                    SET tanggal_akhir_kerja = %s
                    WHERE no_pegawai = %s
                """, [akhir_kerja, no_dokter])
            else:
                cursor.execute("""
                    UPDATE PETCLINIC.PEGAWAI
                    SET tanggal_akhir_kerja = NULL
                    WHERE no_pegawai = %s
                """, [no_dokter])

            cursor.execute("""
                DELETE FROM PETCLINIC.SERTIFIKAT_KOMPETENSI
                WHERE no_tenaga_medis = %s
            """, [no_dokter])
            
            for cert_num, cert_name in zip(cert_numbers, cert_names):
                if cert_num.strip() and cert_name.strip():
                    cursor.execute("""
                        INSERT INTO PETCLINIC.SERTIFIKAT_KOMPETENSI (no_sertifikat_kompetensi, nama_sertifikat, no_tenaga_medis)
                        VALUES (%s, %s, %s)
                    """, [cert_num.strip(), cert_name.strip(), no_dokter])

            if not akhir_kerja:  
                cursor.execute("""
                    DELETE FROM PETCLINIC.JADWAL_PRAKTIK
                    WHERE no_dokter_hewan = %s
                """, [no_dokter])
                
                for day, schedule_time in zip(days, schedule_times):
                    if day.strip() and schedule_time.strip():
                        cursor.execute("""
                            INSERT INTO PETCLINIC.JADWAL_PRAKTIK (hari, jam, no_dokter_hewan)
                            VALUES (%s, %s, %s)
                        """, [day.strip(), schedule_time.strip(), no_dokter])

        messages.success(request, "Profil dokter berhasil diperbarui.")
        notices = connection.connection.notices
        if notices:
            cleaned_notice = notices[0]
            cleaned_notice = cleaned_notice.split('NOTICE:')[1].split('tidak aktif.')[0] + 'tidak aktif.'
            messages.info(request, cleaned_notice.strip())
        return redirect("dashboard:dashboard_dokter")

    return render(request, "dashboard/update_profile_dokter.html", {
        "alamat": alamat_awal,
        "telepon": telepon_awal,
        "akhir_kerja": akhir_kerja_awal,
        "sertifikat_list": sertifikat_list,
        "jadwal_list": jadwal_list,
        "hari_list": ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
    })

@role_required('fdo')
def update_profile_fdo(request):
    user_email = request.session.get("email")
    no_fdo = request.session.get("user_id")

    if not user_email or not no_fdo:
        messages.error(request, "Anda belum login.")
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.alamat, u.nomor_telepon, TO_CHAR(p.tanggal_akhir_kerja, 'YYYY-MM-DD')
            FROM PETCLINIC.USERS u
            JOIN PETCLINIC.PEGAWAI p ON p.email = u.email
            WHERE p.no_pegawai = %s
        """, [no_fdo])
        result = cursor.fetchone()

        if not result:
            messages.error(request, "Data FDO tidak ditemukan.")
            return redirect("dashboard:dashboard_fdo")

        alamat_awal, telepon_awal, akhir_kerja_awal = result

    if request.method == "POST":
        alamat = request.POST.get("alamat", "").strip()
        telepon = request.POST.get("telepon", "").strip()
        akhir_kerja = request.POST.get("akhir_kerja", "").strip() or None

        if not alamat or not telepon:
            messages.error(request, "Alamat dan nomor telepon wajib diisi.")
            return redirect("dashboard:update_profile_fdo")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PETCLINIC.USERS
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, telepon, user_email])

            cursor.execute("""
                UPDATE PETCLINIC.PEGAWAI
                SET tanggal_akhir_kerja = %s
                WHERE no_pegawai = %s
            """, [akhir_kerja, no_fdo])

        messages.success(request, "Profil FDO berhasil diperbarui.")
        return redirect("dashboard:dashboard_fdo")

    return render(request, "dashboard/update_profile_fdo.html", {
        "alamat": alamat_awal,
        "telepon": telepon_awal,
        "akhir_kerja": akhir_kerja_awal,
    })


@role_required('perawat')
def update_profile_perawat(request):
    user_email = request.session.get("email")
    no_perawat = request.session.get("user_id")

    if not user_email or not no_perawat:
        messages.error(request, "Anda belum login.")
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.alamat, u.nomor_telepon, TO_CHAR(p.tanggal_akhir_kerja, 'YYYY-MM-DD')
            FROM PETCLINIC.USERS u
            JOIN PETCLINIC.PEGAWAI p ON p.email = u.email
            WHERE p.no_pegawai = %s
        """, [no_perawat])
        result = cursor.fetchone()

        if not result:
            messages.error(request, "Data perawat tidak ditemukan.")
            return redirect("dashboard:dashboard_perawat")

        alamat_awal, telepon_awal, akhir_kerja_awal = result

        cursor.execute("""
            SELECT no_sertifikat_kompetensi, nama_sertifikat
            FROM PETCLINIC.SERTIFIKAT_KOMPETENSI
            WHERE no_tenaga_medis = %s
        """, [no_perawat])
        sertifikat_list = cursor.fetchall()

    if request.method == "POST":
        alamat = request.POST.get("alamat", "").strip()
        telepon = request.POST.get("telepon", "").strip()
        akhir_kerja = request.POST.get("akhir_kerja", "").strip()

        if not alamat or not telepon:
            messages.error(request, "Alamat dan nomor telepon wajib diisi.")
            return redirect("dashboard:update_profile_perawat")

        cert_numbers = request.POST.getlist("certificate_number[]")
        cert_names = request.POST.getlist("certificate_name[]")
        
        if not cert_numbers or not cert_names or not cert_numbers[0] or not cert_names[0]:
            messages.error(request, "Minimal satu sertifikat kompetensi wajib diisi.")
            return redirect("dashboard:update_profile_perawat")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PETCLINIC.USERS
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, telepon, user_email])

            if akhir_kerja:
                cursor.execute("""
                    UPDATE PETCLINIC.PEGAWAI
                    SET tanggal_akhir_kerja = %s
                    WHERE no_pegawai = %s
                """, [akhir_kerja, no_perawat])
            else:
                cursor.execute("""
                    UPDATE PETCLINIC.PEGAWAI
                    SET tanggal_akhir_kerja = NULL
                    WHERE no_pegawai = %s
                """, [no_perawat])

            cursor.execute("""
                DELETE FROM PETCLINIC.SERTIFIKAT_KOMPETENSI
                WHERE no_tenaga_medis = %s
            """, [no_perawat])
            
            for cert_num, cert_name in zip(cert_numbers, cert_names):
                if cert_num.strip() and cert_name.strip():
                    cursor.execute("""
                        INSERT INTO PETCLINIC.SERTIFIKAT_KOMPETENSI (no_sertifikat_kompetensi, nama_sertifikat, no_tenaga_medis)
                        VALUES (%s, %s, %s)
                    """, [cert_num.strip(), cert_name.strip(), no_perawat])

        messages.success(request, "Profil perawat berhasil diperbarui.")
        return redirect("dashboard:dashboard_perawat")

    return render(request, "dashboard/update_profile_perawat.html", {
        "alamat": alamat_awal,
        "telepon": telepon_awal,
        "akhir_kerja": akhir_kerja_awal,
        "sertifikat_list": sertifikat_list,
    })

@role_required('klien')
def update_profile_klien_individu(request):
    user_email = request.session.get("email")
    if not user_email:
        messages.error(request, "Anda belum login.")
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.no_identitas, u.alamat, u.nomor_telepon,
                   i.nama_depan, i.nama_tengah, i.nama_belakang
            FROM PETCLINIC.KLIEN k
            JOIN PETCLINIC.USERS u ON k.email = u.email
            JOIN PETCLINIC.INDIVIDU i ON k.no_identitas = i.no_identitas_klien
            WHERE k.email = %s
        """, [user_email])
        row = cursor.fetchone()

    if not row:
        messages.error(request, "Data klien individu tidak ditemukan.")
        return redirect("dashboard:dashboard_klien")

    no_identitas, alamat_awal, telepon_awal, nama_depan, nama_tengah, nama_belakang = row

    if request.method == "POST":
        alamat = request.POST.get("alamat", "").strip()
        telepon = request.POST.get("telepon", "").strip()
        depan = request.POST.get("nama_depan", "").strip()
        tengah = request.POST.get("nama_tengah", "").strip()
        belakang = request.POST.get("nama_belakang", "").strip()

        if not all([alamat, telepon, depan, belakang]):
            messages.error(request, "Semua field wajib diisi (kecuali nama tengah).")
            return redirect("dashboard:update_profile_klien_individu")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PETCLINIC.USERS
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, telepon, user_email])

            cursor.execute("""
                UPDATE PETCLINIC.INDIVIDU
                SET nama_depan = %s,
                    nama_tengah = %s,
                    nama_belakang = %s
                WHERE no_identitas_klien = %s
            """, [depan, tengah, belakang, no_identitas])

        messages.success(request, "Profil berhasil diperbarui.")
        return redirect("dashboard:dashboard_klien")

    context = {
        "alamat": alamat_awal,
        "telepon": telepon_awal,
        "nama_depan": nama_depan,
        "nama_tengah": nama_tengah,
        "nama_belakang": nama_belakang,
    }
    return render(request, "dashboard/update_profile_klien_individu.html", context)

@role_required('klien')
def update_profile_klien_perusahaan(request):
    user_email = request.session.get("email")
    if not user_email:
        messages.error(request, "Anda belum login.")
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.no_identitas, u.alamat, u.nomor_telepon, p.nama_perusahaan
            FROM PETCLINIC.KLIEN k
            JOIN PETCLINIC.USERS u ON k.email = u.email
            JOIN PETCLINIC.PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
            WHERE k.email = %s
        """, [user_email])
        row = cursor.fetchone()

    if not row:
        messages.error(request, "Data klien perusahaan tidak ditemukan.")
        return redirect("dashboard:dashboard_klien")

    no_identitas, alamat_awal, telepon_awal, nama_perusahaan_awal = row

    if request.method == "POST":
        alamat = request.POST.get("alamat", "").strip()
        telepon = request.POST.get("telepon", "").strip()
        nama_perusahaan = request.POST.get("nama_perusahaan", "").strip()

        if not all([alamat, telepon, nama_perusahaan]):
            messages.error(request, "Semua field wajib diisi.")
            return redirect("dashboard:update_profile_klien_perusahaan")

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE PETCLINIC.USERS
                SET alamat = %s, nomor_telepon = %s
                WHERE email = %s
            """, [alamat, telepon, user_email])

            cursor.execute("""
                UPDATE PETCLINIC.PERUSAHAAN
                SET nama_perusahaan = %s
                WHERE no_identitas_klien = %s
            """, [nama_perusahaan, no_identitas])

        messages.success(request, "Profil berhasil diperbarui.")
        return redirect("dashboard:dashboard_klien")

    context = {
        "alamat": alamat_awal,
        "telepon": telepon_awal,
        "nama_perusahaan": nama_perusahaan_awal,
    }
    return render(request, "dashboard/update_profile_klien_perusahaan.html", context)
