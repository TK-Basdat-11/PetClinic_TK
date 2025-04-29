from django.shortcuts import render
from django.db import connection
import uuid
import datetime


# Create your views here.
def hewan(request):
    return render(request, "hewan.html")

def create_hewan(request):
    """View for creating a new pet (hewan) record"""
    context = {}
    
    if request.method == 'POST':
        try:
            # Get form data
            data = request.POST
            nama = data['nama']
            pemilik_id = data['pemilik_id'] # This will be the no_identitas_klien
            tanggal_lahir_str = data['tanggal_lahir']  # Format: DD-MM-YYYY
            jenis_id = data['jenis_id']
            foto_url = data['foto_url']
            
            # Validate required fields
            if not all([nama, pemilik_id, tanggal_lahir_str, jenis_id, foto_url]):
                context['error'] = 'Semua field harus diisi'
                return render(request, 'hewan.html', context)
            
            # Parse date (DD-MM-YYYY to YYYY-MM-DD for database)
            try:
                day, month, year = map(int, tanggal_lahir_str.split('-'))
                tanggal_lahir = datetime.date(year, month, day)
                tanggal_lahir_formatted = tanggal_lahir.strftime('%Y-%m-%d')
            except ValueError:
                context['error'] = 'Format tanggal tidak valid. Gunakan DD-MM-YYYY'
                return render(request, 'hewan.html', context)
            
            # Convert string IDs to UUID objects
            try:
                pemilik_uuid = uuid.UUID(pemilik_id)
                jenis_uuid = uuid.UUID(jenis_id)
            except ValueError:
                context['error'] = 'ID pemilik atau jenis hewan tidak valid'
                return render(request, 'hewan.html', context)
            
            # Save to database using cursor
            with connection.cursor() as cursor:
                # Check if pemilik exists
                cursor.execute("SELECT no_identitas FROM KLIEN WHERE no_identitas = %s", [pemilik_uuid])
                if not cursor.fetchone():
                    context['error'] = 'Pemilik tidak ditemukan'
                    return render(request, 'hewan.html', context)
                
                # Check if jenis_hewan exists
                cursor.execute("SELECT id FROM JENIS_HEWAN WHERE id = %s", [jenis_uuid])
                if not cursor.fetchone():
                    context['error'] = 'Jenis hewan tidak ditemukan'
                    return render(request, 'hewan.html', context)
                
                # Check if hewan with same name already exists for this owner
                cursor.execute(
                    "SELECT nama FROM HEWAN WHERE nama = %s AND no_identitas_klien = %s", 
                    [nama, pemilik_uuid]
                )
                if cursor.fetchone():
                    context['error'] = 'Hewan dengan nama tersebut sudah ada untuk pemilik ini'
                    return render(request, 'hewan.html', context)
                
                # Insert new hewan
                cursor.execute(
                    """
                    INSERT INTO HEWAN (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [nama, pemilik_uuid, tanggal_lahir_formatted, jenis_uuid, foto_url]
                )
            
            # Add success message to context
            context['success'] = 'Hewan berhasil ditambahkan'
            
            # Get all hewan for display
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT h.nama, k.nama as pemilik, jh.nama as jenis, h.tanggal_lahir, h.url_foto 
                    FROM HEWAN h
                    JOIN KLIEN k ON h.no_identitas_klien = k.no_identitas
                    JOIN JENIS_HEWAN jh ON h.id_jenis = jh.id
                    ORDER BY h.nama
                """)
                columns = [col[0] for col in cursor.description]
                hewan_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
                context['hewan_list'] = hewan_list
                
            # Also fetch pemilik and jenis data for the dropdowns
            with connection.cursor() as cursor:
                cursor.execute("SELECT no_identitas as id, nama FROM KLIEN ORDER BY nama")
                columns = [col[0] for col in cursor.description]
                pemilik_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
                context['pemilik_list'] = pemilik_list
                
                cursor.execute("SELECT id, nama FROM JENIS_HEWAN ORDER BY nama")
                columns = [col[0] for col in cursor.description]
                jenis_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
                context['jenis_list'] = jenis_list
                
            return render(request, 'hewan.html', context)
        
        except Exception as e:
            # Log the error (in a production app)
            print(f"Error creating hewan: {str(e)}")
            context['error'] = f'Terjadi kesalahan: {str(e)}'
            return render(request, 'hewan.html', context)
    
    # If GET request, fetch data for the template
    with connection.cursor() as cursor:
        # Get all hewan for display
        cursor.execute("""
            SELECT h.nama, k.nama as pemilik, jh.nama as jenis, h.tanggal_lahir, h.url_foto 
            FROM HEWAN h
            JOIN KLIEN k ON h.no_identitas_klien = k.no_identitas
            JOIN JENIS_HEWAN jh ON h.id_jenis = jh.id
            ORDER BY h.nama
        """)
        columns = [col[0] for col in cursor.description]
        hewan_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        context['hewan_list'] = hewan_list
        
        # Get pemilik and jenis data for the dropdowns
        cursor.execute("SELECT no_identitas as id, nama FROM KLIEN ORDER BY nama")
        columns = [col[0] for col in cursor.description]
        pemilik_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        context['pemilik_list'] = pemilik_list
        
        cursor.execute("SELECT id, nama FROM JENIS_HEWAN ORDER BY nama")
        columns = [col[0] for col in cursor.description]
        jenis_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        context['jenis_list'] = jenis_list
    
    return render(request, 'hewan.html', context)


def update_hewan(request):

    return render(request,"hewan.html")

def delete_hewan(request):

    return render(request, "hewan.html")

def show_hewan_client(request):

    return render(request,"hewanClient.html")