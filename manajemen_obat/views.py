from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib import messages
from django.template import TemplateDoesNotExist
from django.http import HttpResponse
from authentication.decorators import role_required

@role_required(['dokter', 'perawat'])
def list_obat(request):
    medicines = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, harga, stok, dosis
        FROM PETCLINIC.OBAT
        ORDER BY kode
        """)
        medicines = cursor.fetchall()
    
    user_role = request.session.get('user_role', 'perawat')
    print(request.session)
    context = {
        'medicines': medicines,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/list_obat.html', context)

@role_required(['dokter', 'perawat'])
def create_obat(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        dosage = request.POST.get('dosage')
        stock = request.POST.get('stock')
        
        errors = {}
        if not name:
            errors['name'] = 'Nama obat tidak boleh kosong'
        
        try:
            price = int(price)
            if price <= 0:
                errors['price'] = 'Harga harus lebih dari 0'
        except ValueError:
            errors['price'] = 'Harga harus berupa angka'
        
        if not dosage:
            errors['dosage'] = 'Dosis tidak boleh kosong'
        
        try:
            stock = int(stock)
            if stock < 0:
                errors['stock'] = 'Stok tidak boleh negatif'
        except ValueError:
            errors['stock'] = 'Stok harus berupa angka'
        
        if errors:
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'errors': errors,
                'name': name,
                'price': price,
                'dosage': dosage,
                'stock': stock,
                'user_role': user_role,
            }
            return render(request, 'manajemen_obat/form_obat.html', context)
        
        with connection.cursor() as cursor:
            
            cursor.execute("""
            SELECT MAX(CAST(SUBSTRING(kode, 4) AS INTEGER))
            FROM PETCLINIC.OBAT
            WHERE kode LIKE 'MED%'
            """)
            result = cursor.fetchone()[0]
            print("Max medicine number result:", result)
            
            next_num = 1
            if result is not None:
                try:
                    next_num = int(result) + 1
                except ValueError:
                    next_num = 1
            
            med_code = f'MED{next_num:03d}'
            print("Generated medicine code:", med_code)
            
            cursor.execute("""
            INSERT INTO PETCLINIC.OBAT (kode, nama, harga, dosis, stok)
            VALUES (%s, %s, %s, %s, %s)
            """, [med_code, name, price, dosage, stock])
            
        messages.success(request, f'Obat {med_code} berhasil ditambahkan!')
        return redirect('obat:list_obat')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/form_obat.html', context)

@role_required(['dokter', 'perawat'])
def update_obat(request, med_code):
    medicine = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, harga, dosis, stok
        FROM PETCLINIC.OBAT
        WHERE kode = %s
        """, [med_code])
        result = cursor.fetchone()
        
        if result:
            medicine = {
                'code': result[0],
                'name': result[1],
                'price': result[2],
                'dosage': result[3],
                'stock': result[4]
            }
    
    if not medicine:
        messages.error(request, 'Obat tidak ditemukan!')
        return redirect('obat:list_obat')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        dosage = request.POST.get('dosage')
        
        errors = {}
        if not name:
            errors['name'] = 'Nama obat tidak boleh kosong'
        
        try:
            price = int(price)
            if price <= 0:
                errors['price'] = 'Harga harus lebih dari 0'
        except ValueError:
            errors['price'] = 'Harga harus berupa angka'
        
        if not dosage:
            errors['dosage'] = 'Dosis tidak boleh kosong'
        
        if errors:
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'medicine': medicine,
                'errors': errors,
                'name': name,
                'price': price,
                'dosage': dosage,
                'user_role': user_role,
            }
            return render(request, 'manajemen_obat/form_obat.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.OBAT
            SET nama = %s, harga = %s, dosis = %s
            WHERE kode = %s
            """, [name, price, dosage, med_code])
        
        messages.success(request, f'Obat {med_code} berhasil diperbarui!')
        return redirect('obat:list_obat')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'medicine': medicine,
        'is_update': True,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/form_obat.html', context)

@role_required(['dokter', 'perawat'])
def update_stock(request):
    medicines = []
    selected_medicine = request.GET.get('medicine', '')
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama
        FROM PETCLINIC.OBAT
        ORDER BY kode
        """)
        medicines = cursor.fetchall()
    
    if request.method == 'POST':
        med_code = request.POST.get('medicine')
        stock = request.POST.get('stock')
        
        errors = {}
        if not med_code:
            errors['medicine'] = 'Silakan pilih obat'
        
        try:
            stock = int(stock)
            if stock < 0:
                errors['stock'] = 'Stok tidak boleh negatif'
        except ValueError:
            errors['stock'] = 'Stok harus berupa angka'
        
        if errors:
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'medicines': medicines,
                'errors': errors,
                'selected_medicine': med_code,
                'stock': stock,
                'user_role': user_role,
            }
            return render(request, 'manajemen_obat/form_stock.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.OBAT
            SET stok = %s
            WHERE kode = %s
            """, [stock, med_code])
        
        messages.success(request, f'Stok obat berhasil diperbarui!')
        return redirect('obat:list_obat')
    
    current_stock = 0
    if selected_medicine:
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT stok FROM PETCLINIC.OBAT WHERE kode = %s
            """, [selected_medicine])
            result = cursor.fetchone()
            if result:
                current_stock = result[0]
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'medicines': medicines,
        'selected_medicine': selected_medicine,
        'stock': current_stock,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/form_stock.html', context)

@role_required(['dokter', 'perawat'])
def delete_obat(request, med_code):
    medicine = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama
        FROM PETCLINIC.OBAT
        WHERE kode = %s
        """, [med_code])
        result = cursor.fetchone()
        
        if result:
            medicine = {
                'code': result[0],
                'name': result[1]
            }
    
    if not medicine:
        messages.error(request, 'Obat tidak ditemukan!')
        return redirect('obat:list_obat')
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
            DELETE FROM PETCLINIC.OBAT
            WHERE kode = %s
            """, [med_code])
        
        messages.success(request, f'Obat {med_code} berhasil dihapus!')
        return redirect('obat:list_obat')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'medicine': medicine,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/confirm_delete_obat.html', context)

@role_required(['dokter', 'perawat'])
def list_perawatan(request):
    treatments = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan, biaya_perawatan
        FROM PETCLINIC.PERAWATAN
        ORDER BY kode_perawatan
        """)
        treatments = cursor.fetchall()
    
        user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'treatments': treatments,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/list_perawatan.html', context)



@role_required(['klien'])
def list_resep_klien(request):
    prescriptions = []
    user_email = request.session.get('user_email')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT  kp.kode_perawatan,
                    p.nama_perawatan,
                    po.kode_obat,
                    o.nama              AS nama_obat,
                    po.kuantitas_obat
            FROM    PETCLINIC.KLIEN                c
            JOIN    PETCLINIC.KUNJUNGAN            k   ON k.no_identitas_klien = c.no_identitas
            JOIN    PETCLINIC.KUNJUNGAN_KEPERAWATAN kp  ON kp.id_kunjungan      = k.id_kunjungan
                                                        AND kp.nama_hewan      = k.nama_hewan
                                                        AND kp.no_identitas_klien = k.no_identitas_klien
            JOIN    PETCLINIC.PERAWATAN_OBAT       po  ON po.kode_perawatan    = kp.kode_perawatan
            JOIN    PETCLINIC.PERAWATAN            p   ON p.kode_perawatan     = kp.kode_perawatan
            JOIN    PETCLINIC.OBAT                 o   ON o.kode               = po.kode_obat
            WHERE   c.email = %s
            ORDER BY k.timestamp_awal DESC, kp.kode_perawatan, o.nama;
        """, [user_email])
        prescriptions = cursor.fetchall()

    context = {
        'prescriptions': prescriptions,
        'user_role': 'klien',
    }
    return render(request, 'manajemen_obat/list_resep.html', context)

@role_required(['dokter', 'perawat'])
def create_perawatan(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cost = request.POST.get('cost')
        
        errors = {}
        if not name:
            errors['name'] = 'Nama jenis perawatan tidak boleh kosong'
        
        try:
            cost = int(cost)
            if cost <= 0:
                errors['cost'] = 'Biaya harus lebih dari 0'
        except ValueError:
            errors['cost'] = 'Biaya harus berupa angka'
        
        if errors:
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'errors': errors,
                'name': name,
                'cost': cost,
                'user_role': user_role,
            }
            return render(request, 'manajemen_obat/form_perawatan.html', context)
        
        with connection.cursor() as cursor:
        
            cursor.execute("""
            SELECT MAX(CAST(SUBSTRING(kode_perawatan, 4) AS INTEGER))
            FROM PETCLINIC.PERAWATAN
            WHERE kode_perawatan LIKE 'TRM%'
            """)
            result = cursor.fetchone()[0]
            print("Max treatment number result:", result)
            
            next_num = 1
            if result is not None:
                try:
                    next_num = int(result) + 1
                except ValueError:
                    next_num = 1
            
            treatment_code = f'TRM{next_num:03d}'
            print("Generated treatment code:", treatment_code)
            
            cursor.execute("""
            INSERT INTO PETCLINIC.PERAWATAN (kode_perawatan, nama_perawatan, biaya_perawatan)
            VALUES (%s, %s, %s)
            """, [treatment_code, name, cost])
            
        messages.success(request, f'Jenis perawatan {treatment_code} berhasil ditambahkan!')
        return redirect('obat:list_perawatan')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/form_perawatan.html', context)

@role_required(['dokter', 'perawat'])
def update_perawatan(request, treatment_code):
    treatment = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan, biaya_perawatan
        FROM PETCLINIC.PERAWATAN
        WHERE kode_perawatan = %s
        """, [treatment_code])
        result = cursor.fetchone()
        
        if result:
            treatment = {
                'code': result[0],
                'name': result[1],
                'cost': result[2]
            }
    
    if not treatment:
        messages.error(request, 'Jenis perawatan tidak ditemukan!')
        return redirect('obat:list_perawatan')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        cost = request.POST.get('cost')
        
        errors = {}
        if not name:
            errors['name'] = 'Nama jenis perawatan tidak boleh kosong'
        
        try:
            cost = int(cost)
            if cost <= 0:
                errors['cost'] = 'Biaya harus lebih dari 0'
        except ValueError:
            errors['cost'] = 'Biaya harus berupa angka'
        
        if errors:
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'treatment': treatment,
                'errors': errors,
                'name': name,
                'cost': cost,
                'user_role': user_role,
            }
            return render(request, 'manajemen_obat/form_perawatan.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.PERAWATAN
            SET nama_perawatan = %s, biaya_perawatan = %s
            WHERE kode_perawatan = %s
            """, [name, cost, treatment_code])
        
        messages.success(request, f'Jenis perawatan {treatment_code} berhasil diperbarui!')
        return redirect('obat:list_perawatan')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'treatment': treatment,
        'is_update': True,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/form_perawatan.html', context)

@role_required(['dokter', 'perawat'])
def delete_perawatan(request, treatment_code):
    treatment = None
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan
        FROM PETCLINIC.PERAWATAN
        WHERE kode_perawatan = %s
        """, [treatment_code])
        result = cursor.fetchone()
        
        if result:
            treatment = {
                'code': result[0],
                'name': result[1]
            }
    
    if not treatment:
        messages.error(request, 'Jenis perawatan tidak ditemukan!')
        return redirect('obat:list_perawatan')
    
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
            DELETE FROM PETCLINIC.PERAWATAN
            WHERE kode_perawatan = %s
            """, [treatment_code])
        
        messages.success(request, f'Jenis perawatan {treatment_code} berhasil dihapus!')
        return redirect('obat:list_perawatan')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'treatment': treatment,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/confirm_delete_perawatan.html', context)

@role_required('dokter')
def list_resep(request):
    prescriptions = []
    
    is_client = request.GET.get('role') == 'client'
    client_id = request.GET.get('client_id')
    
    with connection.cursor() as cursor:
        if is_client and client_id:
            cursor.execute("""
            SELECT p.kode_perawatan, per.nama_perawatan, p.kode_obat, o.nama, p.kuantitas_obat,
                   o.harga * p.kuantitas_obat as total_price
            FROM PETCLINIC.PERAWATAN_OBAT p
            JOIN PETCLINIC.PERAWATAN per ON p.kode_perawatan = per.kode_perawatan
            JOIN PETCLINIC.OBAT o ON p.kode_obat = o.kode
            JOIN PETCLINIC.KUNJUNGAN_KEPERAWATAN kk ON p.kode_perawatan = kk.kode_perawatan
            JOIN PETCLINIC.KUNJUNGAN k ON kk.id_kunjungan = k.id_kunjungan
            WHERE k.no_identitas_klien = %s
            ORDER BY p.kode_perawatan, p.kode_obat
            """, [client_id])
        else:
            cursor.execute("""
            SELECT p.kode_perawatan, per.nama_perawatan, p.kode_obat, o.nama, p.kuantitas_obat,
                   o.harga * p.kuantitas_obat as total_price
            FROM PETCLINIC.PERAWATAN_OBAT p
            JOIN PETCLINIC.PERAWATAN per ON p.kode_perawatan = per.kode_perawatan
            JOIN PETCLINIC.OBAT o ON p.kode_obat = o.kode
            ORDER BY p.kode_perawatan, p.kode_obat
            """)
        
        prescriptions = cursor.fetchall()
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'prescriptions': prescriptions,
        'is_client': is_client,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/list_resep.html', context)

@role_required('dokter')
def create_resep(request):
    treatments = []
    medicines = []
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan
        FROM PETCLINIC.PERAWATAN
        ORDER BY kode_perawatan
        """)
        treatments = cursor.fetchall()
        
        cursor.execute("""
        SELECT kode, nama, stok
        FROM PETCLINIC.OBAT
        WHERE stok > 0
        ORDER BY kode
        """)
        medicines = cursor.fetchall()
    
    if request.method == 'POST':
        treatment_code = request.POST.get('treatment')
        med_code = request.POST.get('medicine')
        quantity = request.POST.get('quantity')
        
        errors = {}
        
        if not treatment_code:
            errors['treatment'] = 'Silakan pilih jenis perawatan'
        
        if not med_code:
            errors['medicine'] = 'Silakan pilih obat'
        
        med_stock = 0
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT stok FROM PETCLINIC.OBAT WHERE kode = %s
            """, [med_code])
            result = cursor.fetchone()
            if result:
                med_stock = result[0]
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                errors['quantity'] = 'Kuantitas harus lebih dari 0'
        except ValueError:
            errors['quantity'] = 'Kuantitas harus berupa angka'
            
        if not errors:
            with connection.cursor() as cursor:
                cursor.execute("""
                SELECT 1 FROM PETCLINIC.PERAWATAN_OBAT 
                WHERE kode_perawatan = %s AND kode_obat = %s
                """, [treatment_code, med_code])
                if cursor.fetchone():
                    errors['duplicate'] = 'Obat ini sudah terdaftar untuk jenis perawatan tersebut'
        
        if errors:
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'treatments': treatments,
                'medicines': medicines,
                'errors': errors,
                'selected_treatment': treatment_code,
                'selected_medicine': med_code,
                'quantity': quantity,
                'user_role': user_role,
            }
            return render(request, 'manajemen_obat/form_resep.html', context)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO PETCLINIC.PERAWATAN_OBAT (kode_perawatan, kode_obat, kuantitas_obat)
                VALUES (%s, %s, %s)
                """, [treatment_code, med_code, quantity])
                
                cursor.execute("""
                UPDATE PETCLINIC.OBAT
                SET stok = stok - %s
                WHERE kode = %s
                """, [quantity, med_code])
            
            messages.success(request, 'Resep obat berhasil ditambahkan!')
            return redirect('obat:list_resep')
        except Exception as e:
            error_message = str(e)
            if "CONTEXT:" in error_message:
                error_message = error_message.split("CONTEXT:")[0].strip()
            errors['database'] = error_message
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'treatments': treatments,
                'medicines': medicines,
                'errors': errors,
                'selected_treatment': treatment_code,
                'selected_medicine': med_code,
                'quantity': quantity,
                'user_role': user_role,
            }
            return render(request, 'manajemen_obat/form_resep.html', context)
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'treatments': treatments,
        'medicines': medicines,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/form_resep.html', context)

@role_required('dokter')
def delete_resep(request, treatment_code, med_code):
    prescription = None
    
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT po.kode_perawatan, p.nama_perawatan, po.kode_obat, o.nama, po.kuantitas_obat
        FROM PETCLINIC.PERAWATAN_OBAT po
        JOIN PETCLINIC.PERAWATAN p ON po.kode_perawatan = p.kode_perawatan
        JOIN PETCLINIC.OBAT o ON po.kode_obat = o.kode
        WHERE po.kode_perawatan = %s AND po.kode_obat = %s
        """, [treatment_code, med_code])
        result = cursor.fetchone()
        
        if result:
            prescription = {
                'treatment_code': result[0],
                'treatment_name': result[1],
                'med_code': result[2],
                'med_name': result[3],
                'quantity': result[4]
            }
    
    if not prescription:
        messages.error(request, 'Resep tidak ditemukan!')
        return redirect('obat:list_resep')
    
    if request.method == 'POST':
        quantity = prescription['quantity']
        
        with connection.cursor() as cursor:
            cursor.execute("""
            DELETE FROM PETCLINIC.PERAWATAN_OBAT
            WHERE kode_perawatan = %s AND kode_obat = %s
            """, [treatment_code, med_code])
            
            cursor.execute("""
            UPDATE PETCLINIC.OBAT
            SET stok = stok + %s
            WHERE kode = %s
            """, [quantity, med_code])
        
        messages.success(request, 'Resep obat berhasil dihapus!')
        return redirect('obat:list_resep')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'prescription': prescription,
        'user_role': user_role,
    }
    return render(request, 'manajemen_obat/confirm_delete_resep.html', context)
