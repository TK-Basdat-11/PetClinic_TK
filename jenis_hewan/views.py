import json
from django.shortcuts import render, redirect
from django.db import IntegrityError, connection, DatabaseError
from django.http import JsonResponse 
from authentication.decorators import role_required
from django.contrib import messages
import uuid

# Create your views here.


@role_required(['fdo', 'dokter', 'perawat', 'klien'])
def jenis_hewan(request):
    context = dict()
    user_role = request.session.get("user_role")
    context["user_role"] = user_role
    
    # Only FDO can modify, others can only read
    if user_role != "fdo":
        context["jenis_hewan"] = get_jenis_hewan_logic()
        return render(request, "jenis_hewan.html", context)
    
    if request.method == 'POST':
        response_data = {}
        try:
            nama_jenis = request.POST.get("nama_jenis")
            if not nama_jenis:
                response_data['error'] = "Nama jenis hewan tidak boleh kosong"
            else:
                create_result = create_jenis_hewan_logic(nama_jenis)
                response_data = create_result

        except DatabaseError as e:
            # Get the error message directly from the database error
            full_msg = str(e)
            err_msg = full_msg.split('CONTEXT:')[0].strip()
            
            # For AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': err_msg}, status=400)
            
            # For regular requests
            messages.error(request, err_msg)
            return redirect('jenis_hewan:index')
            
        except Exception as e:
            response_data['error'] = f"Terjadi kesalahan: {str(e)}"
            
        # Handle response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if 'error' in response_data:
                return JsonResponse(response_data, status=400)
            return JsonResponse(response_data)
        
        if 'error' in response_data:
            messages.error(request, response_data['error'])
        elif 'success' in response_data:
            messages.success(request, response_data['success'])
        
        return redirect('jenis_hewan:index')

    # Refresh the list after any operation
    context["jenis_hewan"] = get_jenis_hewan_logic()
    return render(request, "jenis_hewan.html", context)


def get_jenis_hewan_logic():

    all_jenis_hewan = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nama_jenis FROM PETCLINIC.JENIS_HEWAN;")
        jenis = cursor.fetchall()

        
        for i,j in jenis:
            # Cek apakah jenis hewan ini di-assign ke hewan manapun
            cursor.execute("SELECT COUNT(*) FROM PETCLINIC.HEWAN WHERE id_jenis = %s;", [i])
            count = cursor.fetchone()[0]
            jenis_hewan_dto = {
                "id" : i,
                "nama_jenis" : j,
                "can_delete" : count == 0
            }

            all_jenis_hewan.append(jenis_hewan_dto)

    return all_jenis_hewan

def get_nama_jenis_from_id(id):
    
    nama_jenis = ""

    with connection.cursor() as cursor:
        cursor.execute("SELECT nama_jenis FROM PETCLINIC.JENIS_HEWAN WHERE id = %s;", (id,))

        nama_jenis = cursor.fetchone()[0]

    return nama_jenis

def create_jenis_hewan_logic(nama_jenis):
    context = dict()

    if not nama_jenis or not nama_jenis.strip():
        context["error"] = "Nama jenis hewan tidak boleh kosong"
        context["jenis_hewan"] = get_jenis_hewan_logic()
        return context

    with connection.cursor() as cursor:
        # Check if name already exists
        cursor.execute(
            """
            SELECT nama_jenis FROM PETCLINIC.JENIS_HEWAN 
            WHERE LOWER(nama_jenis) = LOWER(%s)
            """, 
            [nama_jenis.strip()]
        )
        if cursor.fetchone():
            context["error"] = "Jenis hewan dengan nama tersebut sudah ada"
            context["jenis_hewan"] = get_jenis_hewan_logic()
            return context

        ANIMAL_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, 'jenis_hewan.animal_types')
        id_jenis = str(uuid.uuid5(ANIMAL_NAMESPACE, nama_jenis.strip()))

        try:
            cursor.execute(
                """
                INSERT INTO PETCLINIC.JENIS_HEWAN (id, nama_jenis)     
                VALUES (%s, %s)
                """,
                [id_jenis, nama_jenis.strip()]
            )
            context['success'] = "Berhasil menambahkan jenis hewan"
        except IntegrityError as e:
            if "duplicate key" in str(e).lower():
                context["error"] = "Jenis hewan dengan nama tersebut sudah ada"
            else:
                context["error"] = f"Gagal menambahkan jenis hewan: {str(e)}"
        except Exception as e:
            context["error"] = f"Terjadi kesalahan: {str(e)}"
    
    context["jenis_hewan"] = get_jenis_hewan_logic()
    return context

def update_jenis_hewan(data):
    context = dict()

    nama = data["nama_jenis"]
    id_jenis = data["id_jenis"]

    context["jenis_hewan"] = get_jenis_hewan_logic()

    with connection.cursor() as cursor:

        try:
            cursor.execute(
                    """
                    UPDATE PETCLINIC.JENIS_HEWAN 
                    SET nama_jenis = %s
                    WHERE id = %s;
                    """,
                    [nama, id_jenis]
                )
            context['success'] = "Berhasil menambahkan jenis hewan"
        except Exception as e:
            context["error"] = f"Gagal mengupdate jenis hewan karena: {e}"

    return context
        
def delete_jenis_hewan(data):
    context = dict()

    context["jenis_hewan"] = get_jenis_hewan_logic()

    id_jenis = data["id_jenis"]

    with connection.cursor() as cursor:

        try:
            cursor.execute(
                    """
                    DELETE FROM PETCLINIC.JENIS_HEWAN 
                    WHERE id = %s;
                    """,
                    [id_jenis]
                )
            context['success'] = "Berhasil menghapus jenis hewan"
        except Exception as e:
            context["error"] = f"Gagal menghapus jenis hewan karena: {e}"

    return context
