from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages

def vaksin_dokter(request):
    return render(request, "dokter/vaksin_dokter.html")

def create_vaksin_dokter(request):
    return render(request, "dokter/create_vaksin_dokter.html")

def update_vaksin_dokter(request):
    return render(request, "dokter/update_vaksin_dokter.html")

def delete_vaksin_dokter(request):
    return render(request, "dokter/delete_vaksin_dokter.html")

def vaksin_perawat(request):
    list_vaksin_perawat = []
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT kode, nama, harga, stok
        FROM PETCLINIC.VAKSIN
        ORDER BY kode
        """)
        list_vaksin_perawat = cursor.fetchall()
    
    user_role = request.session.get('user_role', 'perawat')
    print(request.session)
    context = {
        'list_vaksin_perawat': list_vaksin_perawat,
        'user_role': user_role,
    }
    return render(request, "perawat/vaksin_perawat.html", context)

def create_vaksin_perawat(request):
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
        except ValueError:
            errors['price'] = 'Harga harus berupa angka'
        
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
                'stock': stock,
                'user_role': user_role,
            }
            return render(request, "perawat/create_vaksin_perawat.html", context)
    
        with connection.cursor() as cursor:
            
            cursor.execute("""
            SELECT MAX(CAST(SUBSTRING(kode, 4) AS INTEGER))
            FROM PETCLINIC.VAKSIN
            WHERE kode LIKE 'VAC%'
            """)
            result = cursor.fetchone()[0]
            print("Max vaccine number result:", result)
            
            next_num = 1
            if result is not None:
                try:
                    next_num = int(result) + 1
                except ValueError:
                    next_num = 1
            
            vaccine_code = f'VAC{next_num:03d}'
            print("Generated vaccine code:", vaccine_code)
            
            cursor.execute("""
            INSERT INTO PETCLINIC.VAKSIN (kode, nama, harga, stok)
            VALUES (%s, %s, %s, %s)
            """, [vaccine_code, name, price, stock])
            
            return redirect('vaksin:vaksin_perawat')

    user_role = request.session.get('user_role', 'perawat')

    context = {
        'user_role': user_role,
    }

    return render(request, "perawat/create_vaksin_perawat.html", context)


def update_vaksin_perawat(request, vaccine_code):
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
            errors['name'] = 'Nama obat tidak boleh kosong'
        
        try:
            price = int(price)
            if price <= 0:
                errors['price'] = 'Harga harus lebih dari 0'
        except ValueError:
            errors['price'] = 'Harga harus berupa angka'
        
        if errors:
            user_role = request.session.get('user_role', 'perawat')
            
            context = {
                'vaksin': vaksin,
                'errors': errors,
                'name': name,
                'price': price,
                'user_role': user_role,
            }
            return render(request, 'perawat/update_vaksin_perawat.html', context)
        
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE PETCLINIC.VAKSIN
            SET nama = %s, harga = %s
            WHERE kode = %s
            """, [name, price, vaccine_code])
        
        return redirect('vaksin:vaksin_perawat')
    
    user_role = request.session.get('user_role', 'perawat')
    
    context = {
        'vaksin': vaksin,
        'is_update': True,
        'user_role': user_role,
    }
    return render(request, "perawat/update_vaksin_perawat.html", context)

def update_stok(request):
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

    return render(request, "perawat/update_stok.html", context)

def delete_vaksin_perawat(request):
    return render(request, "perawat/delete_vaksin_perawat.html")