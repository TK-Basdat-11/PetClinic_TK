from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from datetime import datetime

def vaksin_dokter(request):
    # Pastikan dokter sudah login
    dokter_id = request.session.get('dokter_id')
    if not dokter_id:
        messages.error(request, 'Anda harus login sebagai dokter!')
        return redirect('login')  # Sesuaikan dengan URL login Anda
    
    list_vaksin_dokter = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT k.id_kunjungan, k.nama_hewan, k.no_identitas_klien, 
               TO_CHAR(k.timestamp_awal, 'Dy, DD Month YYYY') as tanggal_kunjungan,
               v.kode, v.nama
        FROM PETCLINIC.KUNJUNGAN k
        JOIN PETCLINIC.VAKSIN v ON k.kode_vaksin = v.kode
        WHERE k.no_dokter_hewan = %s AND k.kode_vaksin IS NOT NULL
        ORDER BY k.timestamp_awal DESC
        """, [dokter_id])
        list_vaksin_dokter = cursor.fetchall()

    context = {
        'list_vaksin_dokter': list_vaksin_dokter,
        'user_role': 'dokter',
    }
    return render(request, "dokter/vaksin_dokter.html", context)

def create_vaksin_dokter(request):
    dokter_id = request.session.get('dokter_id')
    if not dokter_id:
        messages.error(request, 'Anda harus login sebagai dokter!')
        return redirect('login')
    
    if request.method == 'POST':
        kunjungan_id = request.POST.get('kunjungan')
        vaksin_kode = request.POST.get('vaksin')
        
        errors = {}
        if not kunjungan_id:
            errors['kunjungan'] = 'Kunjungan harus dipilih'
        if not vaksin_kode:
            errors['vaksin'] = 'Vaksin harus dipilih'
        
        # Jika ada error, tampilkan kembali form dengan pesan error
        if errors:
            # Ambil daftar kunjungan untuk dropdown
            kunjungan_list = []
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT k.id_kunjungan, k.nama_hewan, TO_CHAR(k.timestamp_awal, 'Dy, DD Month YYYY')
                FROM PETCLINIC.KUNJUNGAN k
                WHERE k.no_dokter_hewan = %s 
                  AND k.timestamp_akhir IS NULL
                  AND k.kode_vaksin IS NULL
                ORDER BY k.timestamp_awal DESC
                """, [dokter_id])
                kunjungan_list = cursor.fetchall()
            
            # Ambil daftar vaksin untuk dropdown
            vaksin_list = []
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT kode, nama, stok
                FROM PETCLINIC.VAKSIN
                WHERE stok > 0
                ORDER BY kode
                """)
                vaksin_list = cursor.fetchall()
            
            context = {
                'errors': errors,
                'kunjungan_list': kunjungan_list,
                'vaksin_list': vaksin_list,
                'selected_kunjungan': kunjungan_id,
                'selected_vaksin': vaksin_kode,
                'user_role': 'dokter',
            }
            return render(request, "dokter/create_vaksin_dokter.html", context)
        
        # Validasi stok vaksin
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT stok FROM PETCLINIC.VAKSIN WHERE kode = %s
            """, [vaksin_kode])
            result = cursor.fetchone()
            
            if not result or result[0] <= 0:
                messages.error(request, 'Stok Vaksin yang dipilih sudah habis!')
                return redirect('vaksin:create_vaksin_dokter')
            
            # Update kunjungan dengan vaksin yang dipilih dan kurangi stok
            cursor.execute("""
            UPDATE PETCLINIC.KUNJUNGAN
            SET kode_vaksin = %s
            WHERE id_kunjungan = %s AND no_dokter_hewan = %s
            """, [vaksin_kode, kunjungan_id, dokter_id])
            
            # Kurangi stok vaksin
            cursor.execute("""
            UPDATE PETCLINIC.VAKSIN
            SET stok = stok - 1
            WHERE kode = %s
            """, [vaksin_kode])
        
        messages.success(request, 'Vaksinasi berhasil dicatat!')
        return redirect('vaksin:vaksin_dokter')
    
    # Menampilkan form untuk CREATE
    kunjungan_list = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT k.id_kunjungan, k.nama_hewan, TO_CHAR(k.timestamp_awal, 'Dy, DD Month YYYY')
        FROM PETCLINIC.KUNJUNGAN k
        WHERE k.no_dokter_hewan = %s 
          AND k.timestamp_akhir IS NULL
          AND k.kode_vaksin IS NULL
        ORDER BY k.timestamp_awal DESC
        """, [dokter_id])
        kunjungan_list = cursor.fetchall()
    
    vaksin_list = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, stok
        FROM PETCLINIC.VAKSIN
        WHERE stok > 0
        ORDER BY kode
        """)
        vaksin_list = cursor.fetchall()
    
    context = {
        'kunjungan_list': kunjungan_list,
        'vaksin_list': vaksin_list,
        'user_role': 'dokter',
    }
    return render(request, "dokter/create_vaksin_dokter.html", context)

def update_vaksin_dokter(request, kunjungan_id=None):
    dokter_id = request.session.get('dokter_id')
    if not dokter_id:
        messages.error(request, 'Anda harus login sebagai dokter!')
        return redirect('login')
    
    # Jika tidak ada kunjungan_id, ambil dari POST
    if not kunjungan_id and request.method == 'POST':
        kunjungan_id = request.POST.get('kunjungan_id')
    
    if not kunjungan_id:
        messages.error(request, 'Kunjungan ID tidak valid!')
        return redirect('vaksin:vaksin_dokter')
    
    # Cek apakah kunjungan tersebut milik dokter yang login
    kunjungan_detail = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT k.id_kunjungan, k.nama_hewan, TO_CHAR(k.timestamp_awal, 'Dy, DD Month YYYY'), 
               k.kode_vaksin, v.nama, v.stok
        FROM PETCLINIC.KUNJUNGAN k
        LEFT JOIN PETCLINIC.VAKSIN v ON k.kode_vaksin = v.kode
        WHERE k.id_kunjungan = %s AND k.no_dokter_hewan = %s
        """, [kunjungan_id, dokter_id])
        result = cursor.fetchone()
        
        if result:
            kunjungan_detail = {
                'id': result[0],
                'nama_hewan': result[1],
                'tanggal': result[2],
                'kode_vaksin': result[3],
                'nama_vaksin': result[4],
                'stok_vaksin': result[5] if result[5] else 0
            }
    
    if not kunjungan_detail:
        messages.error(request, 'Kunjungan tidak ditemukan atau bukan milik dokter ini!')
        return redirect('vaksin:vaksin_dokter')
    
    if request.method == 'POST':
        vaksin_kode_baru = request.POST.get('vaksin')
        vaksin_kode_lama = kunjungan_detail['kode_vaksin']
        
        if not vaksin_kode_baru:
            messages.error(request, 'Vaksin harus dipilih!')
            return redirect('vaksin:update_vaksin_dokter', kunjungan_id=kunjungan_id)
        
        # Validasi stok vaksin baru
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT stok FROM PETCLINIC.VAKSIN WHERE kode = %s
            """, [vaksin_kode_baru])
            result = cursor.fetchone()
            
            if not result or result[0] <= 0:
                messages.error(request, 'Stok Vaksin yang dipilih sudah habis!')
                return redirect('vaksin:update_vaksin_dokter', kunjungan_id=kunjungan_id)
            
            # Update kunjungan dengan vaksin baru
            cursor.execute("""
            UPDATE PETCLINIC.KUNJUNGAN
            SET kode_vaksin = %s
            WHERE id_kunjungan = %s AND no_dokter_hewan = %s
            """, [vaksin_kode_baru, kunjungan_id, dokter_id])
            
            # Kembalikan stok vaksin lama jika ada
            if vaksin_kode_lama:
                cursor.execute("""
                UPDATE PETCLINIC.VAKSIN
                SET stok = stok + 1
                WHERE kode = %s
                """, [vaksin_kode_lama])
            
            # Kurangi stok vaksin baru
            cursor.execute("""
            UPDATE PETCLINIC.VAKSIN
            SET stok = stok - 1
            WHERE kode = %s
            """, [vaksin_kode_baru])
        
        messages.success(request, 'Vaksinasi berhasil diperbarui!')
        return redirect('vaksin:vaksin_dokter')
    
    # Ambil daftar vaksin untuk dropdown
    vaksin_list = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, stok
        FROM PETCLINIC.VAKSIN
        WHERE stok > 0 OR kode = %s
        ORDER BY kode
        """, [kunjungan_detail['kode_vaksin']])
        vaksin_list = cursor.fetchall()
    
    context = {
        'kunjungan': kunjungan_detail,
        'vaksin_list': vaksin_list,
        'user_role': 'dokter',
    }
    return render(request, "dokter/update_vaksin_dokter.html", context)

def delete_vaksin_dokter(request, kunjungan_id=None):
    dokter_id = request.session.get('dokter_id')
    if not dokter_id:
        messages.error(request, 'Anda harus login sebagai dokter!')
        return redirect('login')
    
    # Jika tidak ada kunjungan_id, ambil dari POST
    if not kunjungan_id and request.method == 'POST':
        kunjungan_id = request.POST.get('kunjungan_id')
        
    if not kunjungan_id:
        messages.error(request, 'Kunjungan ID tidak valid!')
        return redirect('vaksin:vaksin_dokter')
    
    # Cek apakah kunjungan tersebut milik dokter yang login dan ada vaksinnya
    kunjungan_detail = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT k.id_kunjungan, k.nama_hewan, TO_CHAR(k.timestamp_awal, 'Dy, DD Month YYYY'), 
               k.kode_vaksin, v.nama
        FROM PETCLINIC.KUNJUNGAN k
        JOIN PETCLINIC.VAKSIN v ON k.kode_vaksin = v.kode
        WHERE k.id_kunjungan = %s AND k.no_dokter_hewan = %s AND k.kode_vaksin IS NOT NULL
        """, [kunjungan_id, dokter_id])
        result = cursor.fetchone()
        
        if result:
            kunjungan_detail = {
                'id': result[0],
                'nama_hewan': result[1],
                'tanggal': result[2],
                'kode_vaksin': result[3],
                'nama_vaksin': result[4]
            }
    
    if not kunjungan_detail:
        messages.error(request, 'Kunjungan tidak ditemukan, bukan milik dokter ini, atau tidak ada vaksinasi!')
        return redirect('vaksin:vaksin_dokter')
    
    if request.method == 'POST' and 'confirm_delete' in request.POST:
        vaksin_kode = kunjungan_detail['kode_vaksin']
        
        with connection.cursor() as cursor:
            # Set kode_vaksin menjadi NULL di tabel KUNJUNGAN
            cursor.execute("""
            UPDATE PETCLINIC.KUNJUNGAN
            SET kode_vaksin = NULL
            WHERE id_kunjungan = %s AND no_dokter_hewan = %s
            """, [kunjungan_id, dokter_id])
            
            # Kembalikan stok vaksin
            cursor.execute("""
            UPDATE PETCLINIC.VAKSIN
            SET stok = stok + 1
            WHERE kode = %s
            """, [vaksin_kode])
        
        messages.success(request, 'Vaksinasi berhasil dihapus!')
        return redirect('vaksin:vaksin_dokter')
    
    context = {
        'kunjungan': kunjungan_detail,
        'user_role': 'dokter',
    }
    return render(request, "dokter/delete_vaksin_dokter.html", context)

def vaksin_perawat(request):
    # Pastikan perawat sudah login
    perawat_id = request.session.get('perawat_id')
    if not perawat_id:
        messages.error(request, 'Anda harus login sebagai perawat!')
        return redirect('login')  # Sesuaikan dengan URL login Anda
    
    list_vaksin_perawat = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, harga, stok
        FROM PETCLINIC.VAKSIN
        ORDER BY kode
        """)
        list_vaksin_perawat = cursor.fetchall()
    
    context = {
        'list_vaksin_perawat': list_vaksin_perawat,
        'user_role': 'perawat',
    }
    return render(request, "perawat/vaksin_perawat.html", context)

def create_vaksin_perawat(request):
    # Pastikan perawat sudah login
    perawat_id = request.session.get('perawat_id')
    if not perawat_id:
        messages.error(request, 'Anda harus login sebagai perawat!')
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
    
        errors = {}
        if not name:
            errors['name'] = 'Nama vaksin tidak boleh kosong'
        
        try:
            price = int(price)
            if price <= 0:
                errors['price'] = 'Harga harus lebih dari 0'
        except (ValueError, TypeError):
            errors['price'] = 'Harga harus berupa angka'
        
        try:
            stock = int(stock)
            if stock < 0:
                errors['stock'] = 'Stok tidak boleh negatif'
        except (ValueError, TypeError):
            errors['stock'] = 'Stok harus berupa angka'
        
        if errors:
            context = {
                'errors': errors,
                'name': name,
                'price': price,
                'stock': stock,
                'user_role': 'perawat',
            }
            return render(request, "perawat/create_vaksin_perawat.html", context)
    
        with connection.cursor() as cursor:
            # Generate kode vaksin baru
            cursor.execute("""
            SELECT MAX(CAST(SUBSTRING(kode FROM 4) AS INTEGER))
            FROM PETCLINIC.VAKSIN
            WHERE kode LIKE 'VAC%'
            """)
            result = cursor.fetchone()[0]
            
            next_num = 1
            if result is not None:
                next_num = int(result) + 1
            
            vaccine_code = f'VAC{next_num:03d}'
            
            # Insert vaksin baru
            cursor.execute("""
            INSERT INTO PETCLINIC.VAKSIN (kode, nama, harga, stok)
            VALUES (%s, %s, %s, %s)
            """, [vaccine_code, name, price, stock])
            
        messages.success(request, f'Vaksin {name} berhasil ditambahkan dengan kode {vaccine_code}!')
        return redirect('vaksin:vaksin_perawat')

    context = {
        'user_role': 'perawat',
    }
    return render(request, "perawat/create_vaksin_perawat.html", context)

def update_vaksin_perawat(request, vaccine_code):
    # Pastikan perawat sudah login
    perawat_id = request.session.get('perawat_id')
    if not perawat_id:
        messages.error(request, 'Anda harus login sebagai perawat!')
        return redirect('login')
    
    # Cek apakah vaksin ada
    vaksin = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, harga, stok
        FROM PETCLINIC.VAKSIN
        WHERE kode = %s
        """, [vaccine_code])
        result = cursor.fetchone()
        
        if result:
            vaksin = {
                'code': result[0],
                'name': result[1],
                'price': result[2],
                'stock': result[3]
            }
    
    if not vaksin:
        messages.error(request, 'Vaksin tidak ditemukan!')
        return redirect('vaksin:vaksin_perawat')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        
        errors = {}
        if not name:
            errors['name'] = 'Nama vaksin tidak boleh kosong'
        
        try:
            price = int(price)
            if price <= 0:
                errors['price'] = 'Harga harus lebih dari 0'
        except (ValueError, TypeError):
            errors['price'] = 'Harga harus berupa angka'
        
        if errors:
            context = {
                'vaksin': vaksin,
                'errors': errors,
                'name': name,
                'price': price,
                'user_role': 'perawat',
            }
            return render(request, 'perawat/update_vaksin_perawat.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.VAKSIN
            SET nama = %s, harga = %s
            WHERE kode = %s
            """, [name, price, vaccine_code])
        
        messages.success(request, f'Vaksin {name} berhasil diperbarui!')
        return redirect('vaksin:vaksin_perawat')
    
    context = {
        'vaksin': vaksin,
        'user_role': 'perawat',
    }
    return render(request, "perawat/update_vaksin_perawat.html", context)

def update_stok(request, vaccine_code):
    # Pastikan perawat sudah login
    perawat_id = request.session.get('perawat_id')
    if not perawat_id:
        messages.error(request, 'Anda harus login sebagai perawat!')
        return redirect('login')
    
    # Cek apakah vaksin ada
    vaksin = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, harga, stok
        FROM PETCLINIC.VAKSIN
        WHERE kode = %s
        """, [vaccine_code])
        result = cursor.fetchone()
        
        if result:
            vaksin = {
                'code': result[0],
                'name': result[1],
                'price': result[2],
                'stock': result[3]
            }
    
    if not vaksin:
        messages.error(request, 'Vaksin tidak ditemukan!')
        return redirect('vaksin:vaksin_perawat')
    
    if request.method == 'POST':
        stock = request.POST.get('stock')
        
        errors = {}
        try:
            stock = int(stock)
            if stock < 0:
                errors['stock'] = 'Stok tidak boleh negatif'
        except (ValueError, TypeError):
            errors['stock'] = 'Stok harus berupa angka'
        
        if errors:
            context = {
                'vaksin': vaksin,
                'errors': errors,
                'stock': stock,
                'user_role': 'perawat',
            }
            return render(request, 'perawat/update_stok.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.VAKSIN
            SET stok = %s
            WHERE kode = %s
            """, [stock, vaccine_code])
        
        messages.success(request, f'Stok vaksin {vaksin["name"]} berhasil diperbarui menjadi {stock}!')
        return redirect('vaksin:vaksin_perawat')
    
    context = {
        'vaksin': vaksin,
        'user_role': 'perawat',
    }
    return render(request, "perawat/update_stok.html", context)

def delete_vaksin_perawat(request, vaccine_code=None):
    # Pastikan perawat sudah login
    perawat_id = request.session.get('perawat_id')
    if not perawat_id:
        messages.error(request, 'Anda harus login sebagai perawat!')
        return redirect('login')
    
    # Jika tidak ada vaccine_code, ambil dari POST
    if not vaccine_code and request.method == 'POST':
        vaccine_code = request.POST.get('vaccine_code')
    
    if not vaccine_code:
        messages.error(request, 'Kode vaksin tidak valid!')
        return redirect('vaksin:vaksin_perawat')
    
    # Cek apakah vaksin ada
    vaksin = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, harga, stok
        FROM PETCLINIC.VAKSIN
        WHERE kode = %s
        """, [vaccine_code])
        result = cursor.fetchone()
        
        if result:
            vaksin = {
                'code': result[0],
                'name': result[1],
                'price': result[2],
                'stock': result[3]
            }
    
    if not vaksin:
        messages.error(request, 'Vaksin tidak ditemukan!')
        return redirect('vaksin:vaksin_perawat')
    
    # Cek apakah vaksin sudah digunakan dalam kunjungan
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT COUNT(*)
        FROM PETCLINIC.KUNJUNGAN
        WHERE kode_vaksin = %s
        """, [vaccine_code])
        used_count = cursor.fetchone()[0]
    
    if used_count > 0:
        messages.error(request, f'Vaksin {vaksin["name"]} tidak dapat dihapus karena sudah digunakan dalam {used_count} kunjungan!')
        return redirect('vaksin:vaksin_perawat')
    
    if request.method == 'POST' and 'confirm_delete' in request.POST:
        with connection.cursor() as cursor:
            cursor.execute("""
            DELETE FROM PETCLINIC.VAKSIN
            WHERE kode = %s
            """, [vaccine_code])
        
        messages.success(request, f'Vaksin {vaksin["name"]} berhasil dihapus!')
        return redirect('vaksin:vaksin_perawat')
    
    context = {
        'vaksin': vaksin,
        'user_role': 'perawat',
    }
    return render(request, "perawat/delete_vaksin_perawat.html", context)