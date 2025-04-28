from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib import messages
from django.template import TemplateDoesNotExist
from django.http import HttpResponse

def list_medicine(request):
    medicines = []
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
        cursor.execute("""
        SELECT kode, nama, harga, stok, dosis
        FROM PETCLINIC.OBAT
        ORDER BY kode
        """)
        medicines = cursor.fetchall()
    
    context = {
        'medicines': medicines,
    }
    return render(request, 'manajemen_obat/list_medicine.html', context)

def create_medicine(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        dosage = request.POST.get('dosage')
        stock = request.POST.get('stock')
        
        # Validate inputs
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
            context = {
                'errors': errors,
                'name': name,
                'price': price,
                'dosage': dosage,
                'stock': stock
            }
            return render(request, 'manajemen_obat/form_medicine.html', context)
        
        # Generate new medicine code (MEDXXX)
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            SELECT MAX(SUBSTRING(kode, 4, 3))
            FROM PETCLINIC.OBAT
            WHERE kode LIKE 'MED%'
            """)
            result = cursor.fetchone()[0]
            
            next_num = 1
            if result is not None:
                try:
                    next_num = int(result) + 1
                except ValueError:
                    # If the existing values can't be parsed as integers
                    next_num = 1
            
            med_code = f'MED{next_num}'
            
            # Insert new medicine
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            INSERT INTO PETCLINIC.OBAT (kode, nama, harga, dosis, stok)
            VALUES (%s, %s, %s, %s, %s)
            """, [med_code, name, price, dosage, stock])
            
        messages.success(request, f'Obat {med_code} berhasil ditambahkan!')
        return redirect('obat:list_medicine')
    
    return render(request, 'manajemen_obat/form_medicine.html')

def update_medicine(request, med_code):
    medicine = None
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
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
        return redirect('obat:list_medicine')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        dosage = request.POST.get('dosage')
        
        # Validate inputs
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
            context = {
                'medicine': medicine,
                'errors': errors,
                'name': name,
                'price': price,
                'dosage': dosage
            }
            return render(request, 'manajemen_obat/form_medicine.html', context)
        
        # Update medicine
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            UPDATE PETCLINIC.OBAT
            SET nama = %s, harga = %s, dosis = %s
            WHERE kode = %s
            """, [name, price, dosage, med_code])
        
        messages.success(request, f'Obat {med_code} berhasil diperbarui!')
        return redirect('obat:list_medicine')
    
    context = {
        'medicine': medicine,
        'is_update': True
    }
    return render(request, 'manajemen_obat/form_medicine.html', context)

def update_stock(request):
    # Get all medicines for dropdown
    medicines = []
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
        cursor.execute("""
        SELECT kode, nama
        FROM PETCLINIC.OBAT
        ORDER BY kode
        """)
        medicines = cursor.fetchall()
    
    if request.method == 'POST':
        med_code = request.POST.get('medicine')
        stock = request.POST.get('stock')
        
        # Validate inputs
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
            context = {
                'medicines': medicines,
                'errors': errors,
                'selected_medicine': med_code,
                'stock': stock
            }
            return render(request, 'manajemen_obat/form_stock.html', context)
        
        # Update stock
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            UPDATE PETCLINIC.OBAT
            SET stok = %s
            WHERE kode = %s
            """, [stock, med_code])
        
        messages.success(request, f'Stok obat berhasil diperbarui!')
        return redirect('obat:list_medicine')
    
    context = {
        'medicines': medicines
    }
    return render(request, 'manajemen_obat/form_stock.html', context)

def delete_medicine(request, med_code):
    medicine = None
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
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
        return redirect('obat:list_medicine')
    
    if request.method == 'POST':
        # Delete medicine
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            DELETE FROM PETCLINIC.OBAT
            WHERE kode = %s
            """, [med_code])
        
        messages.success(request, f'Obat {med_code} berhasil dihapus!')
        return redirect('obat:list_medicine')
    
    context = {
        'medicine': medicine
    }
    return render(request, 'manajemen_obat/confirm_delete.html', context)

def list_treatment(request):
    treatments = []
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan, biaya_perawatan
        FROM PETCLINIC.PERAWATAN
        ORDER BY kode_perawatan
        """)
        treatments = cursor.fetchall()
    
    context = {
        'treatments': treatments,
    }
    return render(request, 'manajemen_obat/list_treatment.html', context)

def create_treatment(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        cost = request.POST.get('cost')
        
        # Validate inputs
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
            context = {
                'errors': errors,
                'name': name,
                'cost': cost
            }
            return render(request, 'manajemen_obat/form_treatment.html', context)
        
        # Generate new treatment code (TRMXXX)
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            SELECT MAX(SUBSTRING(kode_perawatan, 4, 3))
            FROM PETCLINIC.PERAWATAN
            WHERE kode_perawatan LIKE 'TRM%'
            """)
            result = cursor.fetchone()[0]
            
            next_num = 1
            if result is not None:
                try:
                    next_num = int(result) + 1
                except ValueError:
                    # If the existing values can't be parsed as integers
                    next_num = 1
            
            treatment_code = f'TRM{next_num}'
            
            # Insert new treatment
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            INSERT INTO PETCLINIC.PERAWATAN (kode_perawatan, nama_perawatan, biaya_perawatan)
            VALUES (%s, %s, %s)
            """, [treatment_code, name, cost])
            
        messages.success(request, f'Jenis perawatan {treatment_code} berhasil ditambahkan!')
        return redirect('obat:list_treatment')
    
    return render(request, 'manajemen_obat/form_treatment.html')

def update_treatment(request, treatment_code):
    treatment = None
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
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
        return redirect('obat:list_treatment')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        cost = request.POST.get('cost')
        
        # Validate inputs
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
            context = {
                'treatment': treatment,
                'errors': errors,
                'name': name,
                'cost': cost
            }
            return render(request, 'manajemen_obat/form_treatment.html', context)
        
        # Update treatment
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            UPDATE PETCLINIC.PERAWATAN
            SET nama_perawatan = %s, biaya_perawatan = %s
            WHERE kode_perawatan = %s
            """, [name, cost, treatment_code])
        
        messages.success(request, f'Jenis perawatan {treatment_code} berhasil diperbarui!')
        return redirect('obat:list_treatment')
    
    context = {
        'treatment': treatment,
        'is_update': True
    }
    return render(request, 'manajemen_obat/form_treatment.html', context)

def delete_treatment(request, treatment_code):
    treatment = None
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
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
        return redirect('obat:list_treatment')
    
    if request.method == 'POST':
        # Delete treatment
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            cursor.execute("""
            DELETE FROM PETCLINIC.PERAWATAN
            WHERE kode_perawatan = %s
            """, [treatment_code])
        
        messages.success(request, f'Jenis perawatan {treatment_code} berhasil dihapus!')
        return redirect('obat:list_treatment')
    
    context = {
        'treatment': treatment
    }
    return render(request, 'manajemen_obat/confirm_delete_treatment.html', context)

def list_prescriptions(request):
    prescriptions = []
    
    # Check if user has a role (simple approach to simulate user roles)
    is_client = request.GET.get('role') == 'client'
    client_id = request.GET.get('client_id')
    
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
        if is_client and client_id:
            # Filter prescriptions for specific client if client role
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
            # Show all prescriptions for staff
            cursor.execute("""
            SELECT p.kode_perawatan, per.nama_perawatan, p.kode_obat, o.nama, p.kuantitas_obat,
                   o.harga * p.kuantitas_obat as total_price
            FROM PETCLINIC.PERAWATAN_OBAT p
            JOIN PETCLINIC.PERAWATAN per ON p.kode_perawatan = per.kode_perawatan
            JOIN PETCLINIC.OBAT o ON p.kode_obat = o.kode
            ORDER BY p.kode_perawatan, p.kode_obat
            """)
        
        prescriptions = cursor.fetchall()
    
    context = {
        'prescriptions': prescriptions,
        'is_client': is_client
    }
    return render(request, 'manajemen_obat/list_prescriptions.html', context)

def create_prescription(request):
    treatments = []
    medicines = []
    
    with connection.cursor() as cursor:
        # Get all treatments for dropdown
        # TODO: tulis raw SQL di sini
        cursor.execute("""
        SELECT kode_perawatan, nama_perawatan
        FROM PETCLINIC.PERAWATAN
        ORDER BY kode_perawatan
        """)
        treatments = cursor.fetchall()
        
        # Get all medicines for dropdown
        # TODO: tulis raw SQL di sini
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
        
        # Validate inputs
        errors = {}
        
        if not treatment_code:
            errors['treatment'] = 'Silakan pilih jenis perawatan'
        
        if not med_code:
            errors['medicine'] = 'Silakan pilih obat'
        
        med_stock = 0
        # Check current stock
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
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
            elif quantity > med_stock:
                errors['quantity'] = f'Stok obat tidak mencukupi (tersedia: {med_stock})'
        except ValueError:
            errors['quantity'] = 'Kuantitas harus berupa angka'
            
        # Check if prescription already exists
        if not errors:
            with connection.cursor() as cursor:
                # TODO: tulis raw SQL di sini
                cursor.execute("""
                SELECT 1 FROM PETCLINIC.PERAWATAN_OBAT 
                WHERE kode_perawatan = %s AND kode_obat = %s
                """, [treatment_code, med_code])
                if cursor.fetchone():
                    errors['duplicate'] = 'Obat ini sudah terdaftar untuk jenis perawatan tersebut'
        
        if errors:
            context = {
                'treatments': treatments,
                'medicines': medicines,
                'errors': errors,
                'selected_treatment': treatment_code,
                'selected_medicine': med_code,
                'quantity': quantity
            }
            return render(request, 'manajemen_obat/form_prescription.html', context)
        
        # Add prescription and update stock
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            # 1. Insert prescription
            cursor.execute("""
            INSERT INTO PETCLINIC.PERAWATAN_OBAT (kode_perawatan, kode_obat, kuantitas_obat)
            VALUES (%s, %s, %s)
            """, [treatment_code, med_code, quantity])
            
            # 2. Update medicine stock
            cursor.execute("""
            UPDATE PETCLINIC.OBAT
            SET stok = stok - %s
            WHERE kode = %s
            """, [quantity, med_code])
        
        messages.success(request, 'Resep obat berhasil ditambahkan!')
        return redirect('obat:list_prescriptions')
    
    context = {
        'treatments': treatments,
        'medicines': medicines,
    }
    return render(request, 'manajemen_obat/form_prescription.html', context)

def delete_prescription(request, treatment_code, med_code):
    prescription = None
    
    with connection.cursor() as cursor:
        # TODO: tulis raw SQL di sini
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
        return redirect('obat:list_prescriptions')
    
    if request.method == 'POST':
        quantity = prescription['quantity']
        
        with connection.cursor() as cursor:
            # TODO: tulis raw SQL di sini
            # 1. Delete prescription
            cursor.execute("""
            DELETE FROM PETCLINIC.PERAWATAN_OBAT
            WHERE kode_perawatan = %s AND kode_obat = %s
            """, [treatment_code, med_code])
            
            # 2. Restore medicine stock
            cursor.execute("""
            UPDATE PETCLINIC.OBAT
            SET stok = stok + %s
            WHERE kode = %s
            """, [quantity, med_code])
        
        messages.success(request, 'Resep obat berhasil dihapus!')
        return redirect('obat:list_prescriptions')
    
    context = {
        'prescription': prescription
    }
    return render(request, 'manajemen_obat/confirm_delete_prescription.html', context)

def demo_view(request):
    # MOCK DATA
    # 1. Medicine mock data
    medicines = [
        ('MED001', 'Paracetamol', 5000, 100, '500mg / 3x sehari'),
        ('MED002', 'Amoxicillin', 15000, 50, '250mg / 2x sehari'),
        ('MED003', 'Ibuprofen', 8000, 75, '400mg / sesuai kebutuhan'),
        ('MED004', 'Dexamethasone', 12000, 30, '0.5mg / 1x sehari'),
        ('MED005', 'Antacid', 6500, 60, '10ml / setelah makan')
    ]
    
    # 2. Treatment mock data
    treatments = [
        ('TRM001', 'Pemeriksaan Umum', 50000),
        ('TRM002', 'Vaksinasi Rabies', 150000),
        ('TRM003', 'Sterilisasi', 500000),
        ('TRM004', 'Rawat Luka', 75000),
        ('TRM005', 'Bedah Minor', 250000)
    ]
    
    # 3. Prescription mock data
    prescriptions = [
        # kode_perawatan, nama_perawatan, kode_obat, nama_obat, kuantitas, total_harga
        ('TRM001', 'Pemeriksaan Umum', 'MED001', 'Paracetamol', 2, 10000),
        ('TRM002', 'Vaksinasi Rabies', 'MED002', 'Amoxicillin', 3, 45000),
        ('TRM003', 'Sterilisasi', 'MED004', 'Dexamethasone', 5, 60000),
        ('TRM001', 'Pemeriksaan Umum', 'MED003', 'Ibuprofen', 1, 8000),
        ('TRM004', 'Rawat Luka', 'MED005', 'Antacid', 2, 13000)
    ]
    
    # Choose which mock data to display based on the 'view' parameter
    view_type = request.GET.get('view', 'medicine')
    is_client = request.GET.get('role') == 'client'
    
    try:
        if view_type == 'medicine':
            context = {
                'medicines': medicines,
                'demo': True
            }
            return render(request, 'manajemen_obat/list_medicine.html', context)
        
        elif view_type == 'treatment':
            context = {
                'treatments': treatments,
                'demo': True
            }
            return render(request, 'manajemen_obat/list_treatment.html', context)
        
        elif view_type == 'prescription':
            context = {
                'prescriptions': prescriptions,
                'is_client': is_client,
                'demo': True
            }
            return render(request, 'manajemen_obat/list_prescriptions.html', context)
        
        elif view_type == 'create_medicine':
            context = {
                'demo': True
            }
            return render(request, 'manajemen_obat/form_medicine.html', context)
        
        elif view_type == 'create_treatment':
            context = {
                'demo': True
            }
            return render(request, 'manajemen_obat/form_treatment.html', context)
        
        elif view_type == 'create_prescription':
            context = {
                'treatments': [(t[0], t[1]) for t in treatments],
                'medicines': [(m[0], m[1], m[3]) for m in medicines],
                'demo': True
            }
            return render(request, 'manajemen_obat/form_prescription.html', context)
        
        elif view_type == 'delete_medicine':
            context = {
                'medicine': {
                    'code': 'MED001',
                    'name': 'Paracetamol'
                },
                'demo': True
            }
            return render(request, 'manajemen_obat/confirm_delete.html', context)
        
        elif view_type == 'delete_treatment':
            context = {
                'treatment': {
                    'code': 'TRM001',
                    'name': 'Pemeriksaan Umum'
                },
                'demo': True
            }
            return render(request, 'manajemen_obat/confirm_delete_treatment.html', context)
        
        elif view_type == 'delete_prescription':
            context = {
                'prescription': {
                    'treatment_code': 'TRM001',
                    'treatment_name': 'Pemeriksaan Umum',
                    'med_code': 'MED001',
                    'med_name': 'Paracetamol',
                    'quantity': 2
                },
                'demo': True
            }
            return render(request, 'manajemen_obat/confirm_delete_prescription.html', context)
        
        else:
            # Index page with links to all demo views
            return render(request, 'manajemen_obat/demo_index.html')
            
    except TemplateDoesNotExist:
        # Fallback to direct HTML response if template doesn't exist
        html_content = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PetClinic Demo</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 p-8">
            <div class="max-w-4xl mx-auto bg-white p-8 rounded-lg shadow-md">
                <h1 class="text-3xl font-bold text-red-600 mb-6">Template Error</h1>
                <p class="text-lg mb-4">
                    Template for view <span class="font-semibold">{view_type}</span> could not be found. 
                    This may be because <span class="font-mono bg-gray-100 px-1">base.html</span> is missing 
                    or not configured correctly.
                </p>
                <div class="bg-yellow-50 p-4 border-l-4 border-yellow-500 mb-6">
                    <p class="text-yellow-700">
                        Make sure <span class="font-mono">base.html</span> exists in your templates directory 
                        and that <span class="font-mono">TEMPLATES</span> setting in 
                        <span class="font-mono">settings.py</span> is configured correctly.
                    </p>
                </div>
                <h2 class="text-xl font-bold mb-3">Available Data:</h2>
                <div class="bg-gray-50 p-4 rounded overflow-auto">
                    <pre class="text-sm">{medicines if view_type == 'medicine' else treatments if view_type == 'treatment' else prescriptions}</pre>
                </div>
                <div class="mt-6">
                    <a href="/obat/demo/" class="inline-block bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded">
                        Return to Demo Index
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content)
