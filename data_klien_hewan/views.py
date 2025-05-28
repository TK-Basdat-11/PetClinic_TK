from datetime import date, datetime
from pyexpat.errors import messages
from django.shortcuts import redirect, render

from django.db import connection

def list_klien(request):
    search_query = request.GET.get('q', '')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.no_identitas, u.email,
                   i.nama_depan, i.nama_tengah, i.nama_belakang,
                   p.nama_perusahaan,
                   CASE 
                       WHEN i.no_identitas_klien IS NOT NULL THEN 'Individu'
                       WHEN p.no_identitas_klien IS NOT NULL THEN 'Perusahaan'
                       ELSE 'Tidak Diketahui'
                   END AS jenis
            FROM PETCLINIC.KLIEN k
            JOIN PETCLINIC.USERS u ON u.email = k.email
            LEFT JOIN PETCLINIC.INDIVIDU i ON k.no_identitas = i.no_identitas_klien
            LEFT JOIN PETCLINIC.PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
            WHERE (
                TRIM(CONCAT_WS(' ', i.nama_depan, i.nama_tengah, i.nama_belakang)) ILIKE %s
                OR p.nama_perusahaan ILIKE %s
            )
            ORDER BY u.email
        """, [f"%{search_query}%", f"%{search_query}%"])
        rows = cursor.fetchall()

    clients = []
    for row in rows:
        no_identitas = row[0]
        email = row[1]
        nama_individu = ' '.join(filter(None, [row[2], row[3], row[4]])).strip()
        nama_perusahaan = row[5]
        jenis = row[6]
        nama = nama_individu if jenis == 'Individu' else nama_perusahaan
        clients.append((no_identitas, email, nama, jenis))

    context = {
        'clients': clients,
        'search_query': search_query,
    }
    return render(request, "list_klien.html", context)

def detail_klien(request, identitas):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.no_identitas, u.email, u.alamat, u.nomor_telepon,
                   i.nama_depan, i.nama_tengah, i.nama_belakang,
                   p.nama_perusahaan
            FROM PETCLINIC.KLIEN k
            JOIN PETCLINIC.USERS u ON u.email = k.email
            LEFT JOIN PETCLINIC.INDIVIDU i ON i.no_identitas_klien = k.no_identitas
            LEFT JOIN PETCLINIC.PERUSAHAAN p ON p.no_identitas_klien = k.no_identitas
            WHERE k.no_identitas = %s
        """, [identitas])
        row = cursor.fetchone()

    if not row:
        messages.error(request, "Klien tidak ditemukan.")
        return redirect('list_klien')

    nama_lengkap = " ".join(filter(None, [row[4], row[5], row[6]])).strip()
    is_perusahaan = row[7] is not None

    profile = {
        "id": row[0],
        "email": row[1],
        "alamat": row[2],
        "telepon": row[3],
        "jenis": "Perusahaan" if is_perusahaan else "Individu",
        "nama": row[7] if is_perusahaan else nama_lengkap
    }

def detail_klien(request, identitas):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.no_identitas, u.email, u.alamat, u.nomor_telepon,
                   i.nama_depan, i.nama_tengah, i.nama_belakang,
                   p.nama_perusahaan
            FROM PETCLINIC.KLIEN k
            JOIN PETCLINIC.USERS u ON u.email = k.email
            LEFT JOIN PETCLINIC.INDIVIDU i ON i.no_identitas_klien = k.no_identitas
            LEFT JOIN PETCLINIC.PERUSAHAAN p ON p.no_identitas_klien = k.no_identitas
            WHERE k.no_identitas = %s
        """, [identitas])
        row = cursor.fetchone()

    if not row:
        messages.error(request, "Klien tidak ditemukan.")
        return redirect('list_klien')

    nama_lengkap = " ".join(filter(None, [row[4], row[5], row[6]])).strip()
    is_perusahaan = row[7] is not None

    profile = {
        "id": row[0],
        "email": row[1],
        "alamat": row[2],
        "telepon": row[3],
        "jenis": "Perusahaan" if is_perusahaan else "Individu",
        "nama": row[7] if is_perusahaan else nama_lengkap
    }

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.nama, j.nama_jenis, h.tanggal_lahir
            FROM PETCLINIC.HEWAN h
            JOIN PETCLINIC.JENIS_HEWAN j ON h.id_jenis = j.id
            WHERE h.no_identitas_klien = %s
        """, [identitas])
        rows = cursor.fetchall()

        hewan_list = [
            (nama, jenis, tanggal.strftime('%Y-%m-%d') if isinstance(tanggal, (datetime, date)) else tanggal)
            for nama, jenis, tanggal in rows
        ]


    return render(request, "detail_klien.html", {
        "profile": profile,
        "hewan_list": hewan_list
    })