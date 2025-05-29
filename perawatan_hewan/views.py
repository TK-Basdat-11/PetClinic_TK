from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib import messages
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from authentication.decorators import role_required

@role_required(['fdo', 'dokter', 'perawat', 'klien'])
def list_treatment(request):
    treatments = []
    user_role = request.session.get('user_role')
    user_email = request.session.get('email')
        
    try:
        with connection.cursor() as cursor:
            if user_role == 'klien' and user_email:
                cursor.execute("""
                SELECT 
                    k.id_kunjungan,
                    k.no_identitas_klien,
                    k.nama_hewan,
                    CASE 
                        WHEN u_perawat.email IS NOT NULL 
                        THEN INITCAP(REPLACE(SPLIT_PART(u_perawat.email, '@', 1), '.', ' '))
                        ELSE 'N/A'
                    END as perawat_hewan,
                    CASE 
                        WHEN u_dokter.email IS NOT NULL 
                        THEN CONCAT('dr. ', INITCAP(REPLACE(SPLIT_PART(u_dokter.email, '@', 1), '.', ' ')))
                        ELSE 'N/A'
                    END as dokter_hewan,
                    CASE 
                        WHEN u_front_desk.email IS NOT NULL 
                        THEN INITCAP(REPLACE(SPLIT_PART(u_front_desk.email, '@', 1), '.', ' '))
                        ELSE 'N/A'
                    END as front_desk_officer,
                    p.nama_perawatan as jenis_perawatan,
                    k.catatan as catatan_medis,
                    kk.kode_perawatan
                FROM PETCLINIC.KUNJUNGAN k
                JOIN PETCLINIC.KUNJUNGAN_KEPERAWATAN kk ON k.id_kunjungan = kk.id_kunjungan
                JOIN PETCLINIC.PERAWATAN p ON kk.kode_perawatan = p.kode_perawatan
                JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
                
                -- JOIN untuk Perawat Hewan
                LEFT JOIN PETCLINIC.PERAWAT_HEWAN ph ON k.no_perawat_hewan = ph.no_perawat_hewan
                LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_perawat ON ph.no_perawat_hewan = tm_perawat.no_tenaga_medis
                LEFT JOIN PETCLINIC.PEGAWAI peg_perawat ON tm_perawat.no_tenaga_medis = peg_perawat.no_pegawai
                LEFT JOIN PETCLINIC.USERS u_perawat ON peg_perawat.email = u_perawat.email
                
                -- JOIN untuk Dokter Hewan
                LEFT JOIN PETCLINIC.DOKTER_HEWAN dh ON k.no_dokter_hewan = dh.no_dokter_hewan
                LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_dokter ON dh.no_dokter_hewan = tm_dokter.no_tenaga_medis
                LEFT JOIN PETCLINIC.PEGAWAI peg_dokter ON tm_dokter.no_tenaga_medis = peg_dokter.no_pegawai
                LEFT JOIN PETCLINIC.USERS u_dokter ON peg_dokter.email = u_dokter.email
                
                -- JOIN untuk Front Desk Officer
                LEFT JOIN PETCLINIC.FRONT_DESK fd ON k.no_front_desk = fd.no_front_desk
                LEFT JOIN PETCLINIC.PEGAWAI peg_front_desk ON fd.no_front_desk = peg_front_desk.no_pegawai
                LEFT JOIN PETCLINIC.USERS u_front_desk ON peg_front_desk.email = u_front_desk.email
                
                WHERE kl.email = %s
                ORDER BY k.timestamp_awal DESC
                """, [user_email])
                
                result = cursor.fetchall()
                
            else:
                cursor.execute("""
                SELECT 
                    k.id_kunjungan,
                    k.no_identitas_klien,
                    k.nama_hewan,
                    CASE 
                        WHEN u_perawat.email IS NOT NULL 
                        THEN INITCAP(REPLACE(SPLIT_PART(u_perawat.email, '@', 1), '.', ' '))
                        ELSE 'N/A'
                    END as perawat_hewan,
                    CASE 
                        WHEN u_dokter.email IS NOT NULL 
                        THEN CONCAT('dr. ', INITCAP(REPLACE(SPLIT_PART(u_dokter.email, '@', 1), '.', ' ')))
                        ELSE 'N/A'
                    END as dokter_hewan,
                    CASE 
                        WHEN u_front_desk.email IS NOT NULL 
                        THEN INITCAP(REPLACE(SPLIT_PART(u_front_desk.email, '@', 1), '.', ' '))
                        ELSE 'N/A'
                    END as front_desk_officer,
                    p.nama_perawatan as jenis_perawatan,
                    k.catatan as catatan_medis,
                    kk.kode_perawatan
                FROM PETCLINIC.KUNJUNGAN k
                JOIN PETCLINIC.KUNJUNGAN_KEPERAWATAN kk ON k.id_kunjungan = kk.id_kunjungan
                JOIN PETCLINIC.PERAWATAN p ON kk.kode_perawatan = p.kode_perawatan
                
                -- JOIN untuk Perawat Hewan
                LEFT JOIN PETCLINIC.PERAWAT_HEWAN ph ON k.no_perawat_hewan = ph.no_perawat_hewan
                LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_perawat ON ph.no_perawat_hewan = tm_perawat.no_tenaga_medis
                LEFT JOIN PETCLINIC.PEGAWAI peg_perawat ON tm_perawat.no_tenaga_medis = peg_perawat.no_pegawai
                LEFT JOIN PETCLINIC.USERS u_perawat ON peg_perawat.email = u_perawat.email
                
                -- JOIN untuk Dokter Hewan
                LEFT JOIN PETCLINIC.DOKTER_HEWAN dh ON k.no_dokter_hewan = dh.no_dokter_hewan
                LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_dokter ON dh.no_dokter_hewan = tm_dokter.no_tenaga_medis
                LEFT JOIN PETCLINIC.PEGAWAI peg_dokter ON tm_dokter.no_tenaga_medis = peg_dokter.no_pegawai
                LEFT JOIN PETCLINIC.USERS u_dokter ON peg_dokter.email = u_dokter.email
                
                -- JOIN untuk Front Desk Officer
                LEFT JOIN PETCLINIC.FRONT_DESK fd ON k.no_front_desk = fd.no_front_desk
                LEFT JOIN PETCLINIC.PEGAWAI peg_front_desk ON fd.no_front_desk = peg_front_desk.no_pegawai
                LEFT JOIN PETCLINIC.USERS u_front_desk ON peg_front_desk.email = u_front_desk.email
                
                ORDER BY k.timestamp_awal DESC
                """)
                result = cursor.fetchall()
            
            treatments = result
            
    except Exception as e:
        messages.error(request, f'Terjadi kesalahan saat mengambil data treatment: {str(e)}')
        treatments = []
    
    context = {
        'treatments': treatments,
        'user_role': user_role,
        'user_email': user_email,
    }
    return render(request, 'perawatan_hewan/list_treatment.html', context)

@role_required(['fdo', 'dokter'])
def create_treatment(request):
    kunjungan_list = []
    perawatan_list = []
    selected_kunjungan = request.GET.get('kunjungan', '')
    selected_perawatan = request.GET.get('perawatan', '')
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            k.id_kunjungan,
            k.nama_hewan,
            k.no_identitas_klien,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien,
            CASE 
                WHEN u_front_desk.email IS NOT NULL 
                THEN INITCAP(REPLACE(SPLIT_PART(u_front_desk.email, '@', 1), '.', ' '))
                ELSE 'N/A'
            END as front_desk_officer,
            CASE 
                WHEN u_dokter.email IS NOT NULL 
                THEN CONCAT('dr. ', INITCAP(REPLACE(SPLIT_PART(u_dokter.email, '@', 1), '.', ' ')))
                ELSE 'N/A'
            END as dokter_hewan,
            CASE 
                WHEN u_perawat.email IS NOT NULL 
                THEN INITCAP(REPLACE(SPLIT_PART(u_perawat.email, '@', 1), '.', ' '))
                ELSE 'N/A'
            END as perawat_hewan,
            k.catatan,
            k.tipe_kunjungan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') as waktu_kunjungan
        FROM PETCLINIC.KUNJUNGAN k
        
        -- JOIN untuk Klien
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        
        -- JOIN untuk Front Desk Officer
        LEFT JOIN PETCLINIC.FRONT_DESK fd ON k.no_front_desk = fd.no_front_desk
        LEFT JOIN PETCLINIC.PEGAWAI peg_front_desk ON fd.no_front_desk = peg_front_desk.no_pegawai
        LEFT JOIN PETCLINIC.USERS u_front_desk ON peg_front_desk.email = u_front_desk.email
        
        -- JOIN untuk Dokter Hewan
        LEFT JOIN PETCLINIC.DOKTER_HEWAN dh ON k.no_dokter_hewan = dh.no_dokter_hewan
        LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_dokter ON dh.no_dokter_hewan = tm_dokter.no_tenaga_medis
        LEFT JOIN PETCLINIC.PEGAWAI peg_dokter ON tm_dokter.no_tenaga_medis = peg_dokter.no_pegawai
        LEFT JOIN PETCLINIC.USERS u_dokter ON peg_dokter.email = u_dokter.email
        
        -- JOIN untuk Perawat Hewan
        LEFT JOIN PETCLINIC.PERAWAT_HEWAN ph ON k.no_perawat_hewan = ph.no_perawat_hewan
        LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_perawat ON ph.no_perawat_hewan = tm_perawat.no_tenaga_medis
        LEFT JOIN PETCLINIC.PEGAWAI peg_perawat ON tm_perawat.no_tenaga_medis = peg_perawat.no_pegawai
        LEFT JOIN PETCLINIC.USERS u_perawat ON peg_perawat.email = u_perawat.email
        
        ORDER BY k.timestamp_awal DESC
        """)
        kunjungan_list = cursor.fetchall()
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan, biaya_perawatan
        FROM PETCLINIC.PERAWATAN
        ORDER BY kode_perawatan
        """)
        perawatan_list = cursor.fetchall()
    
    if request.method == 'POST':
        kunjungan_id = request.POST.get('kunjungan')
        perawatan_code = request.POST.get('perawatan')
        
        errors = {}
        
        if not kunjungan_id:
            errors['kunjungan'] = 'Silakan pilih kunjungan'
        
        if not perawatan_code:
            errors['perawatan'] = 'Silakan pilih jenis perawatan'

        if kunjungan_id and perawatan_code:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT k.nama_hewan, k.no_identitas_klien, k.no_front_desk, 
                       k.no_perawat_hewan, k.no_dokter_hewan
                FROM PETCLINIC.KUNJUNGAN k 
                WHERE k.id_kunjungan = %s
                """, [kunjungan_id])
                kunjungan_data = cursor.fetchone()
                
                if not kunjungan_data:
                    errors['kunjungan'] = 'Kunjungan tidak ditemukan'
                else:
                    cursor.execute("""
                    SELECT 1 FROM PETCLINIC.KUNJUNGAN_KEPERAWATAN 
                    WHERE id_kunjungan = %s AND kode_perawatan = %s
                    """, [kunjungan_id, perawatan_code])
                    if cursor.fetchone():
                        errors['duplicate'] = 'Perawatan ini sudah pernah ditambahkan untuk kunjungan tersebut'
        
        if errors:
            user_role = request.session.get('user_role')
            
            context = {
                'kunjungan_list': kunjungan_list,
                'perawatan_list': perawatan_list,
                'errors': errors,
                'selected_kunjungan': kunjungan_id,
                'selected_perawatan': perawatan_code,
                'user_role': user_role,
            }
            return render(request, 'perawatan_hewan/create_treatment.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT nama_hewan, no_identitas_klien, no_front_desk, 
                   no_perawat_hewan, no_dokter_hewan
            FROM PETCLINIC.KUNJUNGAN 
            WHERE id_kunjungan = %s
            """, [kunjungan_id])
            kunjungan_data = cursor.fetchone()
            
            cursor.execute("""
            INSERT INTO PETCLINIC.KUNJUNGAN_KEPERAWATAN (
                id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk,
                no_perawat_hewan, no_dokter_hewan, kode_perawatan
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, [
                kunjungan_id, kunjungan_data[0], kunjungan_data[1], 
                kunjungan_data[2], kunjungan_data[3], kunjungan_data[4], 
                perawatan_code
            ])
        
        messages.success(request, 'Perawatan berhasil ditambahkan ke kunjungan!')
        return redirect('perawatan_hewan:list_treatment')
    
    user_role = request.session.get('user_role')
    
    context = {
        'kunjungan_list': kunjungan_list,
        'perawatan_list': perawatan_list,
        'selected_kunjungan': selected_kunjungan,
        'selected_perawatan': selected_perawatan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/create_treatment.html', context)

@role_required(['fdo', 'dokter']) 
def update_treatment(request, id_kunjungan, kode_perawatan):
    perawatan_list = []
    treatment_data = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            kk.id_kunjungan,
            kk.kode_perawatan,
            k.nama_hewan,
            k.no_identitas_klien,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien,
            CASE 
                WHEN u_front_desk.email IS NOT NULL 
                THEN INITCAP(REPLACE(SPLIT_PART(u_front_desk.email, '@', 1), '.', ' '))
                ELSE 'N/A'
            END as front_desk_officer,
            CASE 
                WHEN u_dokter.email IS NOT NULL 
                THEN CONCAT('dr. ', INITCAP(REPLACE(SPLIT_PART(u_dokter.email, '@', 1), '.', ' ')))
                ELSE 'N/A'
            END as dokter_hewan,
            CASE 
                WHEN u_perawat.email IS NOT NULL 
                THEN INITCAP(REPLACE(SPLIT_PART(u_perawat.email, '@', 1), '.', ' '))
                ELSE 'N/A'
            END as perawat_hewan,
            k.catatan,
            k.tipe_kunjungan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') as waktu_kunjungan,
            per.nama_perawatan
        FROM PETCLINIC.KUNJUNGAN_KEPERAWATAN kk
        JOIN PETCLINIC.KUNJUNGAN k ON kk.id_kunjungan = k.id_kunjungan
        JOIN PETCLINIC.PERAWATAN per ON kk.kode_perawatan = per.kode_perawatan
        
        -- JOIN untuk Klien
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        
        -- JOIN untuk Front Desk Officer
        LEFT JOIN PETCLINIC.FRONT_DESK fd ON k.no_front_desk = fd.no_front_desk
        LEFT JOIN PETCLINIC.PEGAWAI peg_front_desk ON fd.no_front_desk = peg_front_desk.no_pegawai
        LEFT JOIN PETCLINIC.USERS u_front_desk ON peg_front_desk.email = u_front_desk.email
        
        -- JOIN untuk Dokter Hewan
        LEFT JOIN PETCLINIC.DOKTER_HEWAN dh ON k.no_dokter_hewan = dh.no_dokter_hewan
        LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_dokter ON dh.no_dokter_hewan = tm_dokter.no_tenaga_medis
        LEFT JOIN PETCLINIC.PEGAWAI peg_dokter ON tm_dokter.no_tenaga_medis = peg_dokter.no_pegawai
        LEFT JOIN PETCLINIC.USERS u_dokter ON peg_dokter.email = u_dokter.email
        
        -- JOIN untuk Perawat Hewan
        LEFT JOIN PETCLINIC.PERAWAT_HEWAN ph ON k.no_perawat_hewan = ph.no_perawat_hewan
        LEFT JOIN PETCLINIC.TENAGA_MEDIS tm_perawat ON ph.no_perawat_hewan = tm_perawat.no_tenaga_medis
        LEFT JOIN PETCLINIC.PEGAWAI peg_perawat ON tm_perawat.no_tenaga_medis = peg_perawat.no_pegawai
        LEFT JOIN PETCLINIC.USERS u_perawat ON peg_perawat.email = u_perawat.email
        
        WHERE kk.id_kunjungan = %s AND kk.kode_perawatan = %s
        """, [id_kunjungan, kode_perawatan])
        treatment_data = cursor.fetchone()
    
    if not treatment_data:
        messages.error(request, 'Treatment tidak ditemukan')
        return redirect('perawatan_hewan:list_treatment')
    
    selected_perawatan = kode_perawatan
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan, biaya_perawatan
        FROM PETCLINIC.PERAWATAN
        ORDER BY kode_perawatan
        """)
        perawatan_list = cursor.fetchall()
    
    if request.method == 'POST':
        new_kunjungan_id = request.POST.get('kunjungan') 
        new_perawatan_code = request.POST.get('perawatan')
        
        errors = {}
        
        if not new_perawatan_code:
            errors['perawatan'] = 'Silakan pilih jenis perawatan'
        
        if new_perawatan_code == kode_perawatan:
            errors['perawatan'] = 'Pilih jenis perawatan yang berbeda dari sebelumnya'
        
        if new_perawatan_code and new_perawatan_code != kode_perawatan:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT 1 FROM PETCLINIC.KUNJUNGAN_KEPERAWATAN 
                WHERE id_kunjungan = %s AND kode_perawatan = %s
                """, [id_kunjungan, new_perawatan_code])
                if cursor.fetchone():
                    errors['duplicate'] = 'Perawatan ini sudah pernah ditambahkan untuk kunjungan tersebut'
        
        if errors:
            user_role = request.session.get('user_role')
            
            context = {
                'perawatan_list': perawatan_list,
                'errors': errors,
                'selected_perawatan': new_perawatan_code,
                'user_role': user_role,
                'treatment_data': treatment_data,
                'id_kunjungan': id_kunjungan,
                'kode_perawatan': kode_perawatan,
            }
            return render(request, 'perawatan_hewan/update_treatment.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.KUNJUNGAN_KEPERAWATAN 
            SET kode_perawatan = %s
            WHERE id_kunjungan = %s AND kode_perawatan = %s
            """, [new_perawatan_code, id_kunjungan, kode_perawatan])
        
        messages.success(request, 'Treatment berhasil diupdate!')
        return redirect('perawatan_hewan:list_treatment')
    
    user_role = request.session.get('user_role')
    
    context = {
        'perawatan_list': perawatan_list,
        'selected_perawatan': selected_perawatan,
        'user_role': user_role,
        'treatment_data': treatment_data,
        'id_kunjungan': id_kunjungan,
        'kode_perawatan': kode_perawatan,
    }
    return render(request, 'perawatan_hewan/update_treatment.html', context)

@role_required(['fdo', 'dokter'])
def delete_treatment(request, id_kunjungan, kode_perawatan):
    treatment_data = None

    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            kk.id_kunjungan,
            kk.kode_perawatan,
            k.nama_hewan,
            k.no_identitas_klien,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien,
            per.nama_perawatan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') as waktu_kunjungan
        FROM PETCLINIC.KUNJUNGAN_KEPERAWATAN kk
        JOIN PETCLINIC.KUNJUNGAN k ON kk.id_kunjungan = k.id_kunjungan
        JOIN PETCLINIC.PERAWATAN per ON kk.kode_perawatan = per.kode_perawatan
        
        -- JOIN untuk Klien
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        
        WHERE kk.id_kunjungan = %s AND kk.kode_perawatan = %s
        """, [id_kunjungan, kode_perawatan])
        treatment_data = cursor.fetchone()
    
    if not treatment_data:
        messages.error(request, 'Treatment tidak ditemukan')
        return redirect('perawatan_hewan:list_treatment')
    
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                DELETE FROM PETCLINIC.KUNJUNGAN_KEPERAWATAN 
                WHERE id_kunjungan = %s AND kode_perawatan = %s
                """, [id_kunjungan, kode_perawatan])
            
            messages.success(request, f'Perawatan {kode_perawatan} untuk Kunjungan {id_kunjungan} berhasil dihapus!')
            return redirect('perawatan_hewan:list_treatment')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat menghapus treatment: {str(e)}')
            return redirect('perawatan_hewan:list_treatment')
    
    user_role = request.session.get('user_role')
    
    context = {
        'treatment_data': treatment_data,
        'id_kunjungan': id_kunjungan,
        'kode_perawatan': kode_perawatan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/delete_treatment.html', context)

@role_required(['fdo', 'dokter', 'perawat', 'klien'])
def list_kunjungan(request):
    kunjungan = []
    user_role = request.session.get('user_role')
    user_email = request.session.get('email')
    
    with connection.cursor() as cursor:
        base_query = """
        SELECT 
            k.id_kunjungan,
            k.no_identitas_klien,
            k.nama_hewan,
            k.tipe_kunjungan as metode_kunjungan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI:SS') as waktu_mulai,
            TO_CHAR(k.timestamp_akhir, 'DD-MM-YYYY HH24:MI:SS') as waktu_selesai,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien
        FROM PETCLINIC.KUNJUNGAN k
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        """
        
        if user_role == 'klien':
            cursor.execute(base_query + """
            WHERE kl.email = %s
            ORDER BY k.timestamp_awal DESC
            """, [user_email])
        else:
            cursor.execute(base_query + """
            ORDER BY k.timestamp_awal DESC
            """)
        
        kunjungan = cursor.fetchall()
    
    context = {
        'kunjungan': kunjungan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/list_kunjungan.html', context)

@role_required(['fdo'])
def create_kunjungan(request):
    klien_list = []
    dokter_list = []
    perawat_list = []
    hewan_list = []
    selected_klien = request.GET.get('klien', '')
    selected_dokter = request.GET.get('dokter', '')
    selected_perawat = request.GET.get('perawat', '')
    selected_tipe = request.GET.get('tipe', '')
    waktu_mulai = request.GET.get('waktu_mulai', '')
    waktu_akhir = request.GET.get('waktu_akhir', '')
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT k.no_identitas, 
               CASE 
                   WHEN i.nama_depan IS NOT NULL 
                   THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                   WHEN p.nama_perusahaan IS NOT NULL 
                   THEN p.nama_perusahaan
               END as nama,
               k.no_identitas
        FROM PETCLINIC.KLIEN k
        LEFT JOIN PETCLINIC.INDIVIDU i ON k.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
        ORDER BY nama
        """)
        klien_list = cursor.fetchall()
        
        cursor.execute("""
        SELECT dh.no_dokter_hewan, u.email
        FROM PETCLINIC.DOKTER_HEWAN dh
        JOIN PETCLINIC.TENAGA_MEDIS tm ON dh.no_dokter_hewan = tm.no_tenaga_medis
        JOIN PETCLINIC.PEGAWAI peg ON tm.no_tenaga_medis = peg.no_pegawai
        JOIN PETCLINIC.USERS u ON peg.email = u.email
        ORDER BY u.email
        """)
        dokter_list = cursor.fetchall()
        
        cursor.execute("""
        SELECT ph.no_perawat_hewan, u.email
        FROM PETCLINIC.PERAWAT_HEWAN ph
        JOIN PETCLINIC.TENAGA_MEDIS tm ON ph.no_perawat_hewan = tm.no_tenaga_medis
        JOIN PETCLINIC.PEGAWAI peg ON tm.no_tenaga_medis = peg.no_pegawai
        JOIN PETCLINIC.USERS u ON peg.email = u.email
        ORDER BY u.email
        """)
        perawat_list = cursor.fetchall()
        
        if selected_klien:
            cursor.execute("""
            SELECT nama
            FROM PETCLINIC.HEWAN
            WHERE no_identitas_klien = %s
            ORDER BY nama
            """, [selected_klien])
            hewan_list = cursor.fetchall()
    
    if request.method == 'POST':
        klien_id = request.POST.get('klien')
        nama_hewan = request.POST.get('nama_hewan')
        dokter_id = request.POST.get('dokter')
        perawat_id = request.POST.get('perawat')
        tipe_kunjungan = request.POST.get('tipe_kunjungan')
        waktu_mulai = request.POST.get('waktu_mulai')
        waktu_akhir = request.POST.get('waktu_akhir')
        
        errors = {}
        
        if not klien_id:
            errors['klien'] = 'Silakan pilih klien'
        
        if not nama_hewan:
            errors['nama_hewan'] = 'Silakan pilih nama hewan'
        
        if not dokter_id:
            errors['dokter'] = 'Silakan pilih dokter hewan'
        
        if not perawat_id:
            errors['perawat'] = 'Silakan pilih perawat hewan'
        
        if not tipe_kunjungan:
            errors['tipe_kunjungan'] = 'Silakan pilih tipe kunjungan'
        elif tipe_kunjungan not in ['Janji Temu', 'Walk-In', 'Darurat']:
            errors['tipe_kunjungan'] = 'Tipe kunjungan tidak valid'
        
        if not waktu_mulai:
            errors['waktu_mulai'] = 'Silakan isi waktu mulai penanganan'

        if errors:
            user_role = request.session.get('user_role')
            
            context = {
                'klien_list': klien_list,
                'dokter_list': dokter_list,
                'perawat_list': perawat_list,
                'hewan_list': hewan_list,
                'errors': errors,
                'selected_klien': klien_id,
                'selected_hewan': nama_hewan,
                'selected_dokter': dokter_id,
                'selected_perawat': perawat_id,
                'selected_tipe': tipe_kunjungan,
                'waktu_mulai': waktu_mulai,
                'waktu_akhir': waktu_akhir,
                'user_role': user_role,
                'tipe_kunjungan_choices': [
                    ('Janji Temu', 'Janji Temu'),
                    ('Walk-In', 'Walk-In'),
                    ('Darurat', 'Darurat')
                ]
            }
            return render(request, 'perawatan_hewan/create_kunjungan.html', context)
        
        try:
            with connection.cursor() as cursor:
                import uuid
                kunjungan_id = str(uuid.uuid4())
                
                user_email = request.session.get('user_email')
                cursor.execute("""
                SELECT fd.no_front_desk
                FROM PETCLINIC.FRONT_DESK fd
                JOIN PETCLINIC.PEGAWAI peg ON fd.no_front_desk = peg.no_pegawai
                JOIN PETCLINIC.USERS u ON peg.email = u.email
                WHERE u.email = %s
                """, [user_email])
                front_desk_result = cursor.fetchone()
                
                if not front_desk_result:
                    cursor.execute("""
                    SELECT no_front_desk FROM PETCLINIC.FRONT_DESK LIMIT 1
                    """)
                    front_desk_result = cursor.fetchone()
                
                front_desk_id = front_desk_result[0] if front_desk_result else None
                
                if not front_desk_id:
                    errors['general'] = 'Tidak ada Front Desk Officer yang tersedia'
                    user_role = request.session.get('user_role')
                    
                    context = {
                        'klien_list': klien_list,
                        'dokter_list': dokter_list,
                        'perawat_list': perawat_list,
                        'hewan_list': hewan_list,
                        'errors': errors,
                        'selected_klien': klien_id,
                        'selected_hewan': nama_hewan,
                        'selected_dokter': dokter_id,
                        'selected_perawat': perawat_id,
                        'selected_tipe': tipe_kunjungan,
                        'waktu_mulai': waktu_mulai,
                        'waktu_akhir': waktu_akhir,
                        'user_role': user_role,
                        'tipe_kunjungan_choices': [
                            ('Janji Temu', 'Janji Temu'),
                            ('Walk-In', 'Walk-In'),
                            ('Darurat', 'Darurat')
                        ]
                    }
                    return render(request, 'perawatan_hewan/create_kunjungan.html', context)
                
                waktu_akhir_value = waktu_akhir if waktu_akhir and waktu_akhir.strip() else None
                
                cursor.execute("""
                INSERT INTO PETCLINIC.KUNJUNGAN (
                    id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk,
                    no_perawat_hewan, no_dokter_hewan, tipe_kunjungan,
                    timestamp_awal, timestamp_akhir
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    kunjungan_id, nama_hewan, klien_id, front_desk_id,
                    perawat_id, dokter_id, tipe_kunjungan,
                    waktu_mulai, waktu_akhir_value
                ])
                
            
            messages.success(request, f'Kunjungan berhasil dibuat!')
            return redirect('perawatan_hewan:list_kunjungan')
            
        except Exception as e:
            error_message = str(e)
            
            if "ERROR:" in error_message:
                try:
                    error_parts = error_message.split("ERROR: ")[1]
                    if "CONTEXT:" in error_parts:
                        user_message = error_parts.split("CONTEXT:")[0].strip()
                    elif "DETAIL:" in error_parts:
                        user_message = error_parts.split("DETAIL:")[0].strip()
                    else:
                        user_message = error_parts.split("\n")[0].strip()
                    
                    user_message = user_message.replace('"', '').strip()
                    
                    
                    if "Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal" in user_message:
                        errors['waktu_akhir'] = 'Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal.'
                    elif "tidak terdaftar atas nama pemilik" in user_message:
                        errors['nama_hewan'] = user_message
                    else:
                        errors['general'] = user_message
                        
                except (IndexError, AttributeError) as parse_error:
                    errors['general'] = f'Terjadi kesalahan: {error_message}'
            else:
                if any(keyword in error_message.lower() for keyword in [
                    'timestamp akhir kunjungan tidak boleh lebih awal',
                    'timestamp_akhir',
                    'check constraint'
                ]):
                    errors['waktu_akhir'] = 'Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal.'
                elif "foreign key" in error_message.lower():
                    if "nama_hewan" in error_message.lower() or "no_identitas_klien" in error_message.lower():
                        errors['nama_hewan'] = 'Data hewan atau klien tidak valid'
                    else:
                        errors['general'] = 'Data referensi tidak valid'
                else:
                    errors['general'] = f'Terjadi kesalahan: {error_message}'
            
            user_role = request.session.get('user_role')
            
            context = {
                'klien_list': klien_list,
                'dokter_list': dokter_list,
                'perawat_list': perawat_list,
                'hewan_list': hewan_list,
                'errors': errors,
                'selected_klien': klien_id,
                'selected_hewan': nama_hewan,
                'selected_dokter': dokter_id,
                'selected_perawat': perawat_id,
                'selected_tipe': tipe_kunjungan,
                'waktu_mulai': waktu_mulai,
                'waktu_akhir': waktu_akhir,
                'user_role': user_role,
                'tipe_kunjungan_choices': [
                    ('Janji Temu', 'Janji Temu'),
                    ('Walk-In', 'Walk-In'),
                    ('Darurat', 'Darurat')
                ]
            }
            return render(request, 'perawatan_hewan/create_kunjungan.html', context)
    
    user_role = request.session.get('user_role')
    
    context = {
        'klien_list': klien_list,
        'dokter_list': dokter_list,
        'perawat_list': perawat_list,
        'hewan_list': hewan_list,
        'selected_klien': selected_klien,
        'selected_dokter': selected_dokter,
        'selected_perawat': selected_perawat,
        'selected_tipe': selected_tipe,
        'waktu_mulai': waktu_mulai,
        'waktu_akhir': waktu_akhir,
        'user_role': user_role,
        'tipe_kunjungan_choices': [
            ('Janji Temu', 'Janji Temu'),
            ('Walk-In', 'Walk-In'),
            ('Darurat', 'Darurat')
        ]
    }
    return render(request, 'perawatan_hewan/create_kunjungan.html', context)

@role_required(['fdo'])
def update_kunjungan(request, id_kunjungan):
    klien_list = []
    dokter_list = []
    perawat_list = []
    hewan_list = []
    kunjungan_data = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            k.id_kunjungan,
            k.nama_hewan,
            k.no_identitas_klien,
            k.no_dokter_hewan,
            k.no_perawat_hewan,
            k.tipe_kunjungan,
            TO_CHAR(k.timestamp_awal, 'YYYY-MM-DD"T"HH24:MI') as waktu_mulai,
            TO_CHAR(k.timestamp_akhir, 'YYYY-MM-DD"T"HH24:MI') as waktu_akhir
        FROM PETCLINIC.KUNJUNGAN k
        WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()
    
    if not kunjungan_data:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('perawatan_hewan:list_kunjungan')
    
    selected_klien = request.GET.get('klien', str(kunjungan_data[2]))
    selected_hewan = request.GET.get('nama_hewan', kunjungan_data[1])
    selected_dokter = request.GET.get('dokter', str(kunjungan_data[3]))
    selected_perawat = request.GET.get('perawat', str(kunjungan_data[4]))
    selected_tipe = request.GET.get('tipe', kunjungan_data[5])
    waktu_mulai = request.GET.get('waktu_mulai', kunjungan_data[6])
    waktu_akhir = request.GET.get('waktu_akhir', kunjungan_data[7] if kunjungan_data[7] else '')
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT k.no_identitas, 
               CASE 
                   WHEN i.nama_depan IS NOT NULL 
                   THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                   WHEN p.nama_perusahaan IS NOT NULL 
                   THEN p.nama_perusahaan
               END as nama,
               k.no_identitas
        FROM PETCLINIC.KLIEN k
        LEFT JOIN PETCLINIC.INDIVIDU i ON k.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
        ORDER BY nama
        """)
        klien_list = cursor.fetchall()
        
        cursor.execute("""
        SELECT dh.no_dokter_hewan, u.email
        FROM PETCLINIC.DOKTER_HEWAN dh
        JOIN PETCLINIC.TENAGA_MEDIS tm ON dh.no_dokter_hewan = tm.no_tenaga_medis
        JOIN PETCLINIC.PEGAWAI peg ON tm.no_tenaga_medis = peg.no_pegawai
        JOIN PETCLINIC.USERS u ON peg.email = u.email
        ORDER BY u.email
        """)
        dokter_list = cursor.fetchall()
        
        cursor.execute("""
        SELECT ph.no_perawat_hewan, u.email
        FROM PETCLINIC.PERAWAT_HEWAN ph
        JOIN PETCLINIC.TENAGA_MEDIS tm ON ph.no_perawat_hewan = tm.no_tenaga_medis
        JOIN PETCLINIC.PEGAWAI peg ON tm.no_tenaga_medis = peg.no_pegawai
        JOIN PETCLINIC.USERS u ON peg.email = u.email
        ORDER BY u.email
        """)
        perawat_list = cursor.fetchall()
        
        if selected_klien:
            cursor.execute("""
            SELECT nama, 
                   CASE 
                       WHEN i.nama_depan IS NOT NULL 
                       THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                       WHEN p.nama_perusahaan IS NOT NULL 
                       THEN p.nama_perusahaan
                   END as nama_klien
            FROM PETCLINIC.HEWAN h
            JOIN PETCLINIC.KLIEN k ON h.no_identitas_klien = k.no_identitas
            LEFT JOIN PETCLINIC.INDIVIDU i ON k.no_identitas = i.no_identitas_klien
            LEFT JOIN PETCLINIC.PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
            WHERE h.no_identitas_klien = %s
            ORDER BY h.nama
            """, [selected_klien])
        else:
            cursor.execute("""
            SELECT h.nama, 
                   CASE 
                       WHEN i.nama_depan IS NOT NULL 
                       THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                       WHEN p.nama_perusahaan IS NOT NULL 
                       THEN p.nama_perusahaan
                   END as nama_klien
            FROM PETCLINIC.HEWAN h
            JOIN PETCLINIC.KLIEN k ON h.no_identitas_klien = k.no_identitas
            LEFT JOIN PETCLINIC.INDIVIDU i ON k.no_identitas = i.no_identitas_klien
            LEFT JOIN PETCLINIC.PERUSAHAAN p ON k.no_identitas = p.no_identitas_klien
            ORDER BY h.nama
            """)
        hewan_list = cursor.fetchall()
    
    if request.method == 'POST':
        klien_id = request.POST.get('klien')
        nama_hewan = request.POST.get('nama_hewan')
        dokter_id = request.POST.get('dokter')
        perawat_id = request.POST.get('perawat')
        tipe_kunjungan = request.POST.get('tipe_kunjungan')
        waktu_mulai = request.POST.get('waktu_mulai')
        waktu_akhir = request.POST.get('waktu_akhir')
        
        errors = {}
        
        if not klien_id:
            errors['klien'] = 'Silakan pilih klien'
        
        if not nama_hewan:
            errors['nama_hewan'] = 'Silakan pilih nama hewan'
        
        if not dokter_id:
            errors['dokter'] = 'Silakan pilih dokter hewan'
        
        if not perawat_id:
            errors['perawat'] = 'Silakan pilih perawat hewan'
        
        if not tipe_kunjungan:
            errors['tipe_kunjungan'] = 'Silakan pilih tipe kunjungan'
        elif tipe_kunjungan not in ['Janji Temu', 'Walk-In', 'Darurat']:
            errors['tipe_kunjungan'] = 'Tipe kunjungan tidak valid'
        
        if not waktu_mulai:
            errors['waktu_mulai'] = 'Silakan isi waktu mulai penanganan'

        if waktu_mulai and waktu_akhir and waktu_akhir.strip():
            from datetime import datetime
            try:
                waktu_mulai_dt = datetime.fromisoformat(waktu_mulai.replace('T', ' '))
                waktu_akhir_dt = datetime.fromisoformat(waktu_akhir.replace('T', ' '))
                if waktu_akhir_dt < waktu_mulai_dt:
                    errors['waktu_akhir'] = 'Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal.'
            except ValueError as ve:
                errors['waktu_mulai'] = 'Format waktu tidak valid'

        if klien_id and nama_hewan:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT 1 FROM PETCLINIC.HEWAN 
                WHERE nama = %s AND no_identitas_klien = %s
                """, [nama_hewan, klien_id])
                if not cursor.fetchone():
                    cursor.execute("""
                    SELECT COALESCE(
                        (SELECT CONCAT(nama_depan, ' ', COALESCE(nama_tengah || ' ', ''), nama_belakang) 
                         FROM PETCLINIC.INDIVIDU WHERE no_identitas_klien = %s),
                        (SELECT nama_perusahaan 
                         FROM PETCLINIC.PERUSAHAAN WHERE no_identitas_klien = %s),
                        %s
                    ) AS nama_pemilik
                    """, [klien_id, klien_id, klien_id])
                    nama_pemilik_result = cursor.fetchone()
                    nama_pemilik = nama_pemilik_result[0] if nama_pemilik_result else klien_id
                    
                    errors['nama_hewan'] = f'Hewan "{nama_hewan}" tidak terdaftar atas nama pemilik "{nama_pemilik}".'

        if errors:
            user_role = request.session.get('user_role')
            
            context = {
                'klien_list': klien_list,
                'dokter_list': dokter_list,
                'perawat_list': perawat_list,
                'hewan_list': hewan_list,
                'errors': errors,
                'selected_klien': klien_id,
                'selected_hewan': nama_hewan,
                'selected_dokter': dokter_id,
                'selected_perawat': perawat_id,
                'selected_tipe': tipe_kunjungan,
                'waktu_mulai': waktu_mulai,
                'waktu_akhir': waktu_akhir,
                'user_role': user_role,
                'id_kunjungan': id_kunjungan,
                'tipe_kunjungan_choices': [
                    ('Janji Temu', 'Janji Temu'),
                    ('Walk-In', 'Walk-In'),
                    ('Darurat', 'Darurat')
                ]
            }
            return render(request, 'perawatan_hewan/update_kunjungan.html', context)
        
        waktu_akhir_value = waktu_akhir if waktu_akhir and waktu_akhir.strip() else None
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                UPDATE PETCLINIC.KUNJUNGAN 
                SET nama_hewan = %s,
                    no_identitas_klien = %s,
                    no_dokter_hewan = %s,
                    no_perawat_hewan = %s,
                    tipe_kunjungan = %s,
                    timestamp_awal = %s,
                    timestamp_akhir = %s
                WHERE id_kunjungan = %s
                """, [
                    nama_hewan, klien_id, dokter_id, perawat_id,
                    tipe_kunjungan, waktu_mulai, waktu_akhir_value, id_kunjungan
                ])
                
            
            messages.success(request, 'Kunjungan berhasil diupdate!')
            return redirect('perawatan_hewan:list_kunjungan')
            
        except Exception as e:
            error_message = str(e)
            
            if "ERROR:" in error_message:
                try:
                    error_parts = error_message.split("ERROR: ")[1]
                    if "CONTEXT:" in error_parts:
                        user_message = error_parts.split("CONTEXT:")[0].strip()
                    elif "DETAIL:" in error_parts:
                        user_message = error_parts.split("DETAIL:")[0].strip()
                    else:
                        user_message = error_parts.split("\n")[0].strip()
                    
                    user_message = user_message.replace('"', '').strip()
                    
                    
                    if "Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal" in user_message:
                        errors['waktu_akhir'] = 'Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal.'
                    elif "tidak terdaftar atas nama pemilik" in user_message:
                        errors['nama_hewan'] = user_message
                    else:
                        errors['general'] = user_message
                        
                except (IndexError, AttributeError) as parse_error:
                    errors['general'] = f'Terjadi kesalahan: {error_message}'
            else:
                if any(keyword in error_message.lower() for keyword in [
                    'timestamp akhir kunjungan tidak boleh lebih awal',
                    'timestamp_akhir',
                    'check constraint'
                ]):
                    errors['waktu_akhir'] = 'Timestamp akhir kunjungan tidak boleh lebih awal dari timestamp awal.'
                elif "foreign key" in error_message.lower():
                    if "nama_hewan" in error_message.lower() or "no_identitas_klien" in error_message.lower():
                        errors['nama_hewan'] = 'Data hewan atau klien tidak valid'
                    else:
                        errors['general'] = 'Data referensi tidak valid'
                else:
                    errors['general'] = f'Terjadi kesalahan: {error_message}'
            
            
            user_role = request.session.get('user_role')
            
            context = {
                'klien_list': klien_list,
                'dokter_list': dokter_list,
                'perawat_list': perawat_list,
                'hewan_list': hewan_list,
                'errors': errors,
                'selected_klien': klien_id,
                'selected_hewan': nama_hewan,
                'selected_dokter': dokter_id,
                'selected_perawat': perawat_id,
                'selected_tipe': tipe_kunjungan,
                'waktu_mulai': waktu_mulai,
                'waktu_akhir': waktu_akhir,
                'user_role': user_role,
                'id_kunjungan': id_kunjungan,
                'tipe_kunjungan_choices': [
                    ('Janji Temu', 'Janji Temu'),
                    ('Walk-In', 'Walk-In'),
                    ('Darurat', 'Darurat')
                ]
            }
            return render(request, 'perawatan_hewan/update_kunjungan.html', context)
    
    user_role = request.session.get('user_role')
    
    context = {
        'klien_list': klien_list,
        'dokter_list': dokter_list,
        'perawat_list': perawat_list,
        'hewan_list': hewan_list,
        'selected_klien': selected_klien,
        'selected_hewan': selected_hewan,
        'selected_dokter': selected_dokter,
        'selected_perawat': selected_perawat,
        'selected_tipe': selected_tipe,
        'waktu_mulai': waktu_mulai,
        'waktu_akhir': waktu_akhir,
        'user_role': user_role,
        'id_kunjungan': id_kunjungan,
        'tipe_kunjungan_choices': [
            ('Janji Temu', 'Janji Temu'),
            ('Walk-In', 'Walk-In'),
            ('Darurat', 'Darurat')
        ]
    }
    return render(request, 'perawatan_hewan/update_kunjungan.html', context)

@role_required(['fdo'])
def delete_kunjungan(request, id_kunjungan):
    kunjungan_data = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            k.id_kunjungan,
            k.nama_hewan,
            k.no_identitas_klien,
            k.tipe_kunjungan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI:SS') as waktu_mulai,
            TO_CHAR(k.timestamp_akhir, 'DD-MM-YYYY HH24:MI:SS') as waktu_selesai
        FROM PETCLINIC.KUNJUNGAN k
        WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()
    
    if not kunjungan_data:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('perawatan_hewan:list_kunjungan')
    
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                DELETE FROM PETCLINIC.KUNJUNGAN_KEPERAWATAN 
                WHERE id_kunjungan = %s
                """, [id_kunjungan])
                
                cursor.execute("""
                DELETE FROM PETCLINIC.KUNJUNGAN 
                WHERE id_kunjungan = %s
                """, [id_kunjungan])
            
            messages.success(request, f'Kunjungan dengan ID {id_kunjungan} berhasil dihapus!')
            return redirect('perawatan_hewan:list_kunjungan')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan saat menghapus kunjungan: {str(e)}')
            return redirect('perawatan_hewan:list_kunjungan')
    
    user_role = request.session.get('user_role')
    
    context = {
        'kunjungan_data': kunjungan_data,
        'id_kunjungan': id_kunjungan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/delete_kunjungan.html', context)

@role_required(['fdo', 'dokter', 'perawat', 'klien'])
def rekam_medis(request, id_kunjungan):
    rekam_medis_data = None
    kunjungan_data = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            k.id_kunjungan,
            k.nama_hewan,
            k.no_identitas_klien,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien,
            k.tipe_kunjungan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') as waktu_kunjungan
        FROM PETCLINIC.KUNJUNGAN k
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()
        
        if not kunjungan_data:
            messages.error(request, 'Kunjungan tidak ditemukan')
            return redirect('perawatan_hewan:list_kunjungan')
        
        cursor.execute("""
        SELECT 
            k.suhu,
            k.berat_badan,
            k.catatan
        FROM PETCLINIC.KUNJUNGAN k
        WHERE k.id_kunjungan = %s AND (k.suhu IS NOT NULL OR k.berat_badan IS NOT NULL OR k.catatan IS NOT NULL)
        """, [id_kunjungan])
        rekam_medis_data = cursor.fetchone()
    
    if not rekam_medis_data:
        return redirect('perawatan_hewan:rekam_medis_unavailable', id_kunjungan=id_kunjungan)
    
    user_role = request.session.get('user_role')
    
    context = {
        'rekam_medis_data': rekam_medis_data,
        'kunjungan_data': kunjungan_data,
        'id_kunjungan': id_kunjungan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/rekam_medis.html', context)

@role_required(["dokter"])
def create_rekam_medis(request, id_kunjungan):
    kunjungan_data = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            k.id_kunjungan,
            k.nama_hewan,
            k.no_identitas_klien,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien,
            k.tipe_kunjungan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') as waktu_kunjungan
        FROM PETCLINIC.KUNJUNGAN k
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()
    
    if not kunjungan_data:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('perawatan_hewan:list_kunjungan')
    
    if request.method == 'POST':
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        catatan_medis = request.POST.get('catatan_medis')
        
        errors = {}
        
        if suhu and not suhu.replace('.', '').isdigit():
            errors['suhu'] = 'Suhu harus berupa angka'
        
        if berat_badan and not berat_badan.replace('.', '').isdigit():
            errors['berat_badan'] = 'Berat badan harus berupa angka'
        
        if not suhu and not berat_badan and not catatan_medis:
            errors['general'] = 'Minimal isi salah satu data rekam medis'
        
        if errors:
            user_role = request.session.get('user_role')
            context = {
                'kunjungan_data': kunjungan_data,
                'id_kunjungan': id_kunjungan,
                'errors': errors,
                'suhu': suhu,
                'berat_badan': berat_badan,
                'catatan_medis': catatan_medis,
                'user_role': user_role,
            }
            return render(request, 'perawatan_hewan/create_rekam_medis.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.KUNJUNGAN 
            SET suhu = %s, berat_badan = %s, catatan = %s
            WHERE id_kunjungan = %s
            """, [
                float(suhu) if suhu else None,
                float(berat_badan) if berat_badan else None,
                catatan_medis if catatan_medis else None,
                id_kunjungan
            ])
        
        messages.success(request, 'Rekam medis berhasil dibuat!')
        return redirect('perawatan_hewan:rekam_medis', id_kunjungan=id_kunjungan)
    
    user_role = request.session.get('user_role')
    
    context = {
        'kunjungan_data': kunjungan_data,
        'id_kunjungan': id_kunjungan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/create_rekam_medis.html', context)

@role_required(["dokter"])
def update_rekam_medis(request, id_kunjungan):
    kunjungan_data = None
    rekam_medis_data = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            k.id_kunjungan,
            k.nama_hewan,
            k.no_identitas_klien,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien,
            k.tipe_kunjungan,
            TO_CHAR(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') as waktu_kunjungan,
            k.suhu,
            k.berat_badan,
            k.catatan
        FROM PETCLINIC.KUNJUNGAN k
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        result = cursor.fetchone()
    
    if not result:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('perawatan_hewan:list_kunjungan')
    
    kunjungan_data = result[:6]  
    rekam_medis_data = result[6:] 
    
    if request.method == 'POST':
        suhu = request.POST.get('suhu')
        berat_badan = request.POST.get('berat_badan')
        catatan_medis = request.POST.get('catatan_medis')
        
        errors = {}
        
        if suhu and not suhu.replace('.', '').isdigit():
            errors['suhu'] = 'Suhu harus berupa angka'
        
        if berat_badan and not berat_badan.replace('.', '').isdigit():
            errors['berat_badan'] = 'Berat badan harus berupa angka'
        
        if errors:
            user_role = request.session.get('user_role')
            context = {
                'kunjungan_data': kunjungan_data,
                'rekam_medis_data': rekam_medis_data,
                'id_kunjungan': id_kunjungan,
                'errors': errors,
                'suhu': suhu,
                'berat_badan': berat_badan,
                'catatan_medis': catatan_medis,
                'user_role': user_role,
            }
            return render(request, 'perawatan_hewan/update_rekam_medis.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.KUNJUNGAN 
            SET suhu = %s, berat_badan = %s, catatan = %s
            WHERE id_kunjungan = %s
            """, [
                float(suhu) if suhu else None,
                float(berat_badan) if berat_badan else None,
                catatan_medis if catatan_medis else None,
                id_kunjungan
            ])
        
        messages.success(request, 'Rekam medis berhasil diupdate!')
        return redirect('perawatan_hewan:rekam_medis', id_kunjungan=id_kunjungan)
    
    user_role = request.session.get('user_role')
    
    context = {
        'kunjungan_data': kunjungan_data,
        'rekam_medis_data': rekam_medis_data,
        'id_kunjungan': id_kunjungan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/update_rekam_medis.html', context)

@role_required(["dokter", "perawat", "klien", "fdo"])
def rekam_medis_unavailable(request, id_kunjungan):
    kunjungan_data = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT 
            k.id_kunjungan,
            k.nama_hewan,
            k.no_identitas_klien,
            CASE 
                WHEN i.nama_depan IS NOT NULL 
                THEN CONCAT(i.nama_depan, ' ', COALESCE(i.nama_tengah || ' ', ''), i.nama_belakang)
                WHEN p.nama_perusahaan IS NOT NULL 
                THEN p.nama_perusahaan
                ELSE 'N/A'
            END as nama_klien
        FROM PETCLINIC.KUNJUNGAN k
        LEFT JOIN PETCLINIC.KLIEN kl ON k.no_identitas_klien = kl.no_identitas
        LEFT JOIN PETCLINIC.INDIVIDU i ON kl.no_identitas = i.no_identitas_klien
        LEFT JOIN PETCLINIC.PERUSAHAAN p ON kl.no_identitas = p.no_identitas_klien
        WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        kunjungan_data = cursor.fetchone()
    
    if not kunjungan_data:
        messages.error(request, 'Kunjungan tidak ditemukan')
        return redirect('perawatan_hewan:list_kunjungan')
    
    user_role = request.session.get('user_role')
    
    context = {
        'kunjungan_data': kunjungan_data,
        'id_kunjungan': id_kunjungan,
        'user_role': user_role,
    }
    return render(request, 'perawatan_hewan/rekam_medis_unavailable.html', context)