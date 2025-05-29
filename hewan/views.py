import json
from django.shortcuts import render
from django.db import connection
from jenis_hewan.views import get_jenis_hewan_logic,get_nama_jenis_from_id
from authentication.views import get_nama_klien_from_individu
import uuid
import datetime


# Create your views here.
def hewan(request):
    context = {
        "jenis_list": get_jenis_hewan_logic(),
        "hewan_list": get_all_hewan_logic(),
        "pemilik_list": get_all_individu()
    }

    if request.method == 'POST':
        context.update(create_hewan(request.POST))

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            context['error'] = 'Invalid JSON data'
            return render(request, 'hewan.html', context)
            
        
        result_context = update_hewan(request, data)

        context.update(result_context)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            context.update(delete_hewan(request, data))

        except json.JSONDecodeError:
            context['error'] = 'Invalid JSON data'
            return render(request, 'hewan.html', context)

    return render(request, "hewan.html", context)

def show_hewan_client(request):

    no_identitas_klien = request.session['user_id']

    context = {
        "jenis_list": get_jenis_hewan_logic(),
        "hewan_list": get_client_hewan_logic(no_identitas_klien),
        "pemilik_list": get_one_individu(no_identitas_klien)
    }

    if request.method == 'POST':
        context.update(create_hewan(request.POST, no_identitas_klien))

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            context['error'] = 'Invalid JSON data'
            return render(request, 'hewanClient.html', context)
            
        
        result_context = update_hewan(data, no_identitas_klien)

        context.update(result_context)


    return render(request,"hewanClient.html",context)



def create_hewan(data, no_identitas_klien = False):
    """View for creating a new pet (hewan) record"""
    context = {}
    
    try:
        # Get form data
        nama = data["nama"]
        pemilik_id = data["pemilik_id"]  
        tanggal_lahir_str = data["tanggal_lahir"]  # Format: DD-MM-YYYY
        jenis_id = data["jenis_id"]
        foto_url = data["foto_url"]
        
        # Validate required fields
        if not all([nama, pemilik_id, tanggal_lahir_str, jenis_id, foto_url]):
            context['error'] = 'Semua field harus diisi'
            return context
        
        # Parse date (DD-MM-YYYY to YYYY-MM-DD for database)
        try:
            day, month, year = map(int, tanggal_lahir_str.split('-'))
            tanggal_lahir = datetime.date(year, month, day)
            tanggal_lahir_formatted = tanggal_lahir.strftime('%Y-%m-%d')
        except ValueError:
            context['error'] = 'Format tanggal tidak valid. Gunakan DD-MM-YYYY'
            return context
        
        # Convert string IDs to UUID objects
        try:
            uuid.UUID(pemilik_id)
            uuid.UUID(jenis_id)
        except ValueError:
            context['error'] = 'ID pemilik atau jenis hewan tidak valid'
            return context
        
        # Save to database using cursor
        with connection.cursor() as cursor:
            # Check if pemilik exists
            cursor.execute("SELECT no_identitas FROM PETCLINIC.KLIEN WHERE no_identitas = %s", [pemilik_id])
            if not cursor.fetchone():
                context['error'] = 'Pemilik tidak ditemukan'
                return context
            
            # Check if jenis_hewan exists
            cursor.execute("SELECT id FROM PETCLINIC.JENIS_HEWAN WHERE id = %s", [jenis_id])
            if not cursor.fetchone():
                context['error'] = 'Jenis hewan tidak ditemukan'
                return context
            
            # Check if hewan with same name already exists for this owner
            cursor.execute(
                "SELECT nama FROM PETCLINIC.HEWAN WHERE nama = %s AND no_identitas_klien = %s", 
                [nama, pemilik_id]
            )
            if cursor.fetchone():
                context['error'] = 'Hewan dengan nama tersebut sudah ada untuk pemilik ini'
                return context
            
            # Insert new hewan
            cursor.execute(
                """
                INSERT INTO PETCLINIC.HEWAN (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [nama, pemilik_id, tanggal_lahir_formatted, jenis_id, foto_url]
            )
        
        # Add success message to context
        context['success'] = 'Hewan berhasil ditambahkan'
        
        if no_identitas_klien:
            context['hewan_list'] = get_client_hewan_logic(no_identitas_klien)
            context['pemilik_list'] = get_one_individu(no_identitas_klien)
            context['jenis_list'] = get_jenis_hewan_logic()
        else:
            context['hewan_list'] = get_all_hewan_logic()
            context['pemilik_list'] = get_all_individu()
            context['jenis_list'] = get_jenis_hewan_logic()
            
        return context
    
    except Exception as e:
        import logging
        logging.error(f"Error creating hewan: {str(e)}")
        context['error'] = f'Terjadi kesalahan: {str(e)}'
        return context
    
def update_hewan(data, no_identitas_klien= False):
    context = {}
    
    try:
        nama = data.get("nama")
        no_identitas_klien = data.get("no_identitas_klien")
        tanggal_lahir = data.get("tanggal_lahir")  # Format: DD-MM-YYYY
        id_jenis = data.get("id_jenis")
        url_foto = data.get("url_foto")
        
        original_nama = data.get("original_nama", nama)
        original_owner_id = data.get("original_owner_id", no_identitas_klien)
        
        if not all([nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto]):
            context['error'] = 'Semua field harus diisi'
            return context
        
        # Parse date (DD-MM-YYYY to YYYY-MM-DD for database)
        try:
            day, month, year = map(int, tanggal_lahir.split('-'))
            tanggal_lahir = datetime.date(year, month, day)
            tanggal_lahir_formatted = tanggal_lahir.strftime('%Y-%m-%d')
        except ValueError:
            context['error'] = 'Format tanggal tidak valid. Gunakan DD-MM-YYYY'
            return context
        
        # Convert string IDs to UUID objects (if you're using UUIDs)
        try:
            uuid.UUID(no_identitas_klien)
            uuid.UUID(id_jenis)
        except ValueError:
            context['error'] = 'ID pemilik atau jenis hewan tidak valid'
            return context
        
        # Update database using cursor
        with connection.cursor() as cursor:
            # Check if the original pet exists
            cursor.execute(
                "SELECT nama FROM PETCLINIC.HEWAN WHERE no_identitas_klien = %s AND nama = %s;", 
                [original_owner_id, original_nama]
            )
            if not cursor.fetchone():
                context['error'] = 'Hewan tidak ditemukan'
                return context
                
            # Check if pemilik exists
            cursor.execute("SELECT no_identitas FROM PETCLINIC.KLIEN WHERE no_identitas = %s;", [no_identitas_klien])
            if not cursor.fetchone():
                context['error'] = 'Pemilik tidak ditemukan'
                return context
            
            # Check if jenis_hewan exists
            cursor.execute("SELECT id FROM PETCLINIC.JENIS_HEWAN WHERE id = %s;", [id_jenis])
            if not cursor.fetchone():
                context['error'] = 'Jenis hewan tidak ditemukan'
                return context
            
            # If we're changing the name, check if a pet with the new name already exists for this owner
            if nama != original_nama:
                cursor.execute(
                    "SELECT nama FROM PETCLINIC.HEWAN WHERE no_identitas_klien = %s AND nama = %s AND nama != %s;", 
                    [no_identitas_klien, nama, original_nama]
                )
                if cursor.fetchone():
                    context['error'] = 'Hewan dengan nama tersebut sudah ada untuk pemilik ini'
                    return context
            
            # Update hewan record
            cursor.execute(
                """
                UPDATE PETCLINIC.HEWAN 
                SET nama = %s, 
                    no_identitas_klien = %s, 
                    tanggal_lahir = %s, 
                    id_jenis = %s, 
                    url_foto = %s
                WHERE nama = %s AND no_identitas_klien = %s;
                """,
                [nama, no_identitas_klien, tanggal_lahir_formatted, id_jenis, url_foto, original_nama, original_owner_id]
            )
        
        # Add success message to context
        context['success'] = 'Hewan berhasil diperbarui'
        
        if no_identitas_klien:
            context['hewan_list'] = get_all_hewan_logic()
            context['pemilik_list'] = get_all_individu()
            context['jenis_list'] = get_jenis_hewan_logic()
        else:
            context['hewan_list'] = get_client_hewan_logic(no_identitas_klien)
            context['pemilik_list'] = get_one_individu(no_identitas_klien)
            context['jenis_list'] = get_jenis_hewan_logic()
            
        return context
    
    except Exception as e:
        import logging
        logging.error(f"Error updating hewan: {str(e)}")
        context['error'] = f'Terjadi kesalahan: {str(e)}'
        return context

def delete_hewan(data):
    context = dict()

    context['hewan_list'] = get_all_hewan_logic()
    context['pemilik_list'] = get_all_individu()
    context['jenis_list'] = get_jenis_hewan_logic()
    try:
        nama = data["nama"]
        no_identitas_klien = data["no_identitas_klien"]
    except KeyError as ke:
        context['error'] = f"Data tidak lengkap: {str(ke)}"

        return context

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM PETCLINIC.hewan WHERE nama = %s AND no_identitas_klien = %s",[nama, no_identitas_klien])
            if cursor.rowcount == 0:
                context['error'] = f"Gagal menghapus hewan: {nama}"

                return context
        
    except Exception as db_error:

        error_msg = str(db_error)

        context['error'] = f"Gagal menghapus hewan: {error_msg}"

        return context

    context['success'] = f"Hewan {nama} berhasil dihapus!"


    return context

def get_all_hewan_logic():
    list_all_hewan = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PETCLINIC.HEWAN")

        tuple_all_hewan = cursor.fetchall()

        for i,j,k,l,m in tuple_all_hewan:

            nama_jenis = get_nama_jenis_from_id(l)

            klien = get_nama_klien_from_individu(j)

            dto_hewan = {
                "no_identitas": j,
                "nama" : i,
                "pemilik" : klien,
                "tanggal_lahir" : k,
                "nama_jenis" : nama_jenis,
                "url_foto" : m
            }

            list_all_hewan.append(dto_hewan)

    return list_all_hewan


def get_client_hewan_logic(no_identitas_klien):
    list_client_hewan = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PETCLINIC.HEWAN WHERE no_identitas_klien=%s",
        [no_identitas_klien])

        tuple_all_hewan = cursor.fetchall()

        for i,j,k,l,m in tuple_all_hewan:

            nama_jenis = get_nama_jenis_from_id(l)

            klien = get_nama_klien_from_individu(j)

            dto_hewan = {
                "no_identitas": j,
                "nama" : i,
                "pemilik" : klien,
                "tanggal_lahir" : k,
                "nama_jenis" : nama_jenis,
                "url_foto" : m
            }

            list_client_hewan.append(dto_hewan)

    return list_client_hewan


def get_all_individu():
    list_individu = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PETCLINIC.INDIVIDU;")

        all_data_raw = cursor.fetchall()

        for data_raw in all_data_raw:
            nama = f"{data_raw[1]} {data_raw[2]} {data_raw[3]}"

            dto_individu = {
                "no_identitas": data_raw[0],
                "nama": nama
            }

            list_individu.append(dto_individu)

    return list_individu


def get_one_individu(no_identitas_klien):
    list_individu = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PETCLINIC.INDIVIDU WHERE no_identitas_klien = %s",
                       [no_identitas_klien])

        all_data_raw = cursor.fetchall()

        for data_raw in all_data_raw:
            nama = f"{data_raw[1]} {data_raw[2]} {data_raw[3]}"

            dto_individu = {
                "no_identitas": data_raw[0],
                "nama": nama
            }

            list_individu.append(dto_individu)

    return list_individu
