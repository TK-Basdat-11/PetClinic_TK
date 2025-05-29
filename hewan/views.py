import json
from django.shortcuts import redirect, render
from django.db import connection, DatabaseError
from django.http import JsonResponse
from django.contrib import messages
from jenis_hewan.views import get_jenis_hewan_logic,get_nama_jenis_from_id
from authentication.views import get_nama_klien_from_individu
import uuid
from authentication.decorators import role_required
import logging

# Create your views here.
@role_required(['fdo'])
def hewan(request):
    context = {
        "jenis_list": get_jenis_hewan_logic(),
        "hewan_list": get_all_hewan_logic(),
        "pemilik_list": get_all_individu()
    }

    if request.method == 'POST':
        context.update(create_hewan(request))

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            logging.warning(f"FDO PUT data received: {data}")
            context.update(update_hewan(request, data))
        except json.JSONDecodeError:
            context['error'] = 'Invalid JSON data'
            return render(request, 'hewan.html', context)

    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            result = delete_hewan(request, data)
            
            # For AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                if 'error' in result:
                    return JsonResponse(result, status=400)
                return JsonResponse(result)
            
            # For regular requests
            if 'error' in result:
                messages.error(request, result['error'])
            else:
                messages.success(request, result['success'])
            return redirect('hewan:index')

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return render(request, "hewan.html", context)

@role_required(['klien'])
def show_hewan_client(request):

    no_identitas_klien = request.session.get('user_id')

    context = {
        "jenis_list": get_jenis_hewan_logic(),
        "hewan_list": get_client_hewan_logic(no_identitas_klien),
        "pemilik_list": get_one_individu(no_identitas_klien),
        "user_role": request.session.get("user_role"),
    }

    if request.method == 'POST':

        if request.POST.get('_method') == 'PUT':
            data = {
                'nama': request.POST.get('nama'),
                'no_identitas_klien': request.POST.get('no_identitas_klien', no_identitas_klien),
                'tanggal_lahir': request.POST.get('tanggal_lahir'),
                'id_jenis': request.POST.get('jenis_id'),
                'url_foto': request.POST.get('foto_url'),
                'original_nama': request.POST.get('original_nama'),
                'original_owner_id': request.POST.get('original_owner_id', no_identitas_klien)
            }
            context.update(update_hewan(request, data, is_client=True))
        else:
            context.update(create_hewan(request, is_client=True))

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            context.update(update_hewan(request, data, is_client=True))
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON data: {str(e)}"
            context['error'] = error_msg
            return render(request, 'hewanClient.html', context)
        except Exception as e:
            error_msg = f"Error processing update: {str(e)}"
            context['error'] = error_msg
            return render(request, 'hewanClient.html', context)

    return render(request, "hewanClient.html", context)

@role_required(['fdo', 'klien'])
def create_hewan(request, is_client=False):
    data = request.POST
    no_identitas_klien = request.session.get('user_id') if is_client else None
    
    context = {}
    
    try:
        nama = data["nama"]
        pemilik_id = data["pemilik_id"] if not is_client else no_identitas_klien
        tanggal_lahir_str = data["tanggal_lahir"]
        jenis_id = data["jenis_id"]
        foto_url = data["foto_url"]
        
        if not all([nama, pemilik_id, tanggal_lahir_str, jenis_id, foto_url]):
            context['error'] = 'Semua field harus diisi'
            return context
        
        try:
            uuid.UUID(pemilik_id)
            uuid.UUID(jenis_id)
        except ValueError:
            context['error'] = 'ID pemilik atau jenis hewan tidak valid'
            return context
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT no_identitas FROM PETCLINIC.KLIEN WHERE no_identitas = %s", [pemilik_id])
            if not cursor.fetchone():
                context['error'] = 'Pemilik tidak ditemukan'
                return context
            

            cursor.execute("SELECT id FROM PETCLINIC.JENIS_HEWAN WHERE id = %s", [jenis_id])
            if not cursor.fetchone():
                context['error'] = 'Jenis hewan tidak ditemukan'
                return context
            
            cursor.execute(
                "SELECT nama FROM PETCLINIC.HEWAN WHERE nama = %s AND no_identitas_klien = %s", 
                [nama, pemilik_id]
            )
            if cursor.fetchone():
                context['error'] = 'Hewan dengan nama tersebut sudah ada untuk pemilik ini'
                return context
            
            cursor.execute(
                """
                INSERT INTO PETCLINIC.HEWAN (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [nama, pemilik_id, tanggal_lahir_str, jenis_id, foto_url]
            )
        
        context['success'] = 'Hewan berhasil ditambahkan'
        
        if is_client:
            context['hewan_list'] = get_client_hewan_logic(no_identitas_klien)
            context['pemilik_list'] = get_one_individu(no_identitas_klien)
            context['jenis_list'] = get_jenis_hewan_logic()
        else:
            context['hewan_list'] = get_all_hewan_logic()
            context['pemilik_list'] = get_all_individu()
            context['jenis_list'] = get_jenis_hewan_logic()
            
        return context
    
    except Exception as e:
        logging.error(f"Error creating hewan: {str(e)}")
        context['error'] = f'Terjadi kesalahan: {str(e)}'
        return context
    
@role_required(['fdo', 'klien'])
def update_hewan(request, data, is_client=False):
    
    context = {}
    client_id = request.session.get('user_id') if is_client else False
    
    try:
        
        nama = data.get("nama")
        no_identitas_klien = data.get("no_identitas_klien", client_id)
        
        if is_client:
            no_identitas_klien = client_id
            
        tanggal_lahir = data.get("tanggal_lahir")
        id_jenis = data.get("id_jenis")
        url_foto = data.get("url_foto")
        
        original_nama = data.get("original_nama", nama)
        original_owner_id = data.get("original_owner_id", no_identitas_klien)
        
        if is_client:
            original_owner_id = client_id
            
        
        if not all([nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto]):
            missing = []
            if not nama: missing.append("nama")
            if not no_identitas_klien: missing.append("no_identitas_klien")
            if not tanggal_lahir: missing.append("tanggal_lahir")
            if not id_jenis: missing.append("id_jenis")
            if not url_foto: missing.append("url_foto")
            
            context['error'] = f'Semua field harus diisi. Missing: {", ".join(missing)}'
            return context
        
        try:
            uuid.UUID(no_identitas_klien)
            uuid.UUID(id_jenis)
            uuid.UUID(original_owner_id)
        except ValueError as ve:
            context['error'] = f'ID pemilik atau jenis hewan tidak valid: {str(ve)}'
            return context
        
        with connection.cursor() as cursor:
            query = "SELECT nama FROM PETCLINIC.HEWAN WHERE no_identitas_klien = %s AND nama = %s;"
            params = [original_owner_id, original_nama]
            cursor.execute(query, params)
            result = cursor.fetchone()
            if not result:
                context['error'] = f'Hewan tidak ditemukan: {original_nama} for owner {original_owner_id}'
                return context
                
            query = "SELECT no_identitas FROM PETCLINIC.KLIEN WHERE no_identitas = %s;"
            params = [no_identitas_klien]
            cursor.execute(query, params)
            result = cursor.fetchone()
            if not result:
                context['error'] = 'Pemilik tidak ditemukan'
                return context
            
            
            query = "SELECT id FROM PETCLINIC.JENIS_HEWAN WHERE id = %s;"
            params = [id_jenis]
            cursor.execute(query, params)
            result = cursor.fetchone()
            if not result:
                context['error'] = 'Jenis hewan tidak ditemukan'
                return context
            
            
            if nama != original_nama:
                query = "SELECT nama FROM PETCLINIC.HEWAN WHERE no_identitas_klien = %s AND nama = %s AND nama != %s;"
                params = [no_identitas_klien, nama, original_nama]
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    context['error'] = 'Hewan dengan nama tersebut sudah ada untuk pemilik ini'
                    return context
            
            
            query = """
                UPDATE PETCLINIC.HEWAN 
                SET nama = %s, 
                    no_identitas_klien = %s, 
                    tanggal_lahir = %s, 
                    id_jenis = %s, 
                    url_foto = %s
                WHERE nama = %s AND no_identitas_klien = %s;
                """
            params = [nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto, original_nama, original_owner_id]
            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            
            if rows_affected == 0:
                context['error'] = f'Gagal memperbarui hewan. Pastikan hewan {original_nama} milik pemilik {original_owner_id} ada.'
                return context
        
        context['success'] = 'Hewan berhasil diperbarui'
        
        if is_client:
            context['hewan_list'] = get_client_hewan_logic(client_id)
            context['pemilik_list'] = get_one_individu(client_id)
            context['jenis_list'] = get_jenis_hewan_logic()
        else:
            context['hewan_list'] = get_all_hewan_logic()
            context['pemilik_list'] = get_all_individu()
            context['jenis_list'] = get_jenis_hewan_logic()
            
        return context
    
    except Exception as e:
        context['error'] = f'Terjadi kesalahan: {str(e)}'
        return context

@role_required(['fdo'])
def delete_hewan(request, data):
    try:
        nama = data.get("nama")
        no_identitas_klien = data.get("no_identitas_klien")
        
        if not all([nama, no_identitas_klien]):
            raise ValueError("Data tidak lengkap")

        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM PETCLINIC.hewan WHERE nama = %s AND no_identitas_klien = %s",
                [nama, no_identitas_klien]
            )
            
            if cursor.rowcount == 0:
                raise ValueError(f"Gagal menghapus hewan: {nama}")

            return {'success': f"Hewan {nama} berhasil dihapus!"}

    except DatabaseError as e:
        # Get the error message directly from the database error
        full_msg = str(e)
        err_msg = full_msg.split('CONTEXT:')[0].strip()
        return {'error': err_msg}
        
    except Exception as e:
        return {'error': str(e)}

def get_all_hewan_logic():
    list_all_hewan = []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.*, 
                   (SELECT COUNT(*) 
                    FROM PETCLINIC.KUNJUNGAN k 
                    WHERE k.nama_hewan = h.nama 
                    AND k.no_identitas_klien = h.no_identitas_klien 
                    AND k.timestamp_akhir IS NULL) as active_visits
            FROM PETCLINIC.HEWAN h
        """)

        tuple_all_hewan = cursor.fetchall()

        for i,j,k,l,m,active_visits in tuple_all_hewan:
            nama_jenis = get_nama_jenis_from_id(l)
            klien = get_nama_klien_from_individu(j)

            dto_hewan = {
                "no_identitas": j,
                "nama" : i,
                "pemilik" : klien,
                "tanggal_lahir" : k,
                "nama_jenis" : nama_jenis,
                "jenis" : l,
                "url_foto" : m,
                "can_delete": active_visits == 0
            }

            list_all_hewan.append(dto_hewan)

    return list_all_hewan


def get_client_hewan_logic(no_identitas_klien):
    list_client_hewan = []

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.*, 
                   (SELECT COUNT(*) 
                    FROM PETCLINIC.KUNJUNGAN k 
                    WHERE k.nama_hewan = h.nama 
                    AND k.no_identitas_klien = h.no_identitas_klien 
                    AND k.timestamp_akhir IS NULL) as active_visits
            FROM PETCLINIC.HEWAN h
            WHERE h.no_identitas_klien = %s
        """, [no_identitas_klien])

        tuple_all_hewan = cursor.fetchall()

        for i,j,k,l,m,active_visits in tuple_all_hewan:
            nama_jenis = get_nama_jenis_from_id(l)
            klien = get_nama_klien_from_individu(j)

            dto_hewan = {
                "no_identitas": j,
                "nama" : i,
                "pemilik" : klien,
                "tanggal_lahir" : k,
                "nama_jenis" : nama_jenis,
                "jenis" : l,
                "url_foto" : m,
                "can_delete": active_visits == 0
            }
            
            logging.warning(f"Client Hewan DTO: {dto_hewan}")
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

    print(f"Getting individu for client ID: {no_identitas_klien}")
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PETCLINIC.INDIVIDU WHERE no_identitas_klien = %s",
                       [no_identitas_klien])

        all_data_raw = cursor.fetchall()
        print(f"Found {len(all_data_raw)} individu records")

        if len(all_data_raw) == 0:
            print(f"No records found in INDIVIDU, trying KLIEN table")
            cursor.execute("SELECT no_identitas, nama, '', '' FROM PETCLINIC.KLIEN WHERE no_identitas = %s",
                          [no_identitas_klien])
            all_data_raw = cursor.fetchall()
            print(f"Found {len(all_data_raw)} klien records")

        for data_raw in all_data_raw:
            if data_raw[2] == '' and data_raw[3] == '':
                nama = data_raw[1]
            else:
                nama = f"{data_raw[1]} {data_raw[2]} {data_raw[3]}".strip()

            dto_individu = {
                "no_identitas": data_raw[0],
                "nama": nama
            }

            list_individu.append(dto_individu)
            print(f"Added individu: {dto_individu}")

    if len(list_individu) == 0:
        dummy_individu = {
            "no_identitas": no_identitas_klien,
            "nama": f"Klien {no_identitas_klien}"
        }
        list_individu.append(dummy_individu)
        print(f"Added fallback dummy individu: {dummy_individu}")

    return list_individu