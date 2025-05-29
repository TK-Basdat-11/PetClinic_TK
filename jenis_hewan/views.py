import json
from django.shortcuts import render
from django.db import IntegrityError, connection
from django.http import JsonResponse 

import uuid

# Create your views here.


def jenis_hewan(request):
    context = dict()
    user_role = request.session.get("user_role")
    context["user_role"] = user_role
    
    # Dokter hanya bisa read
    if user_role == "dokter":
        context["jenis_hewan"] = get_jenis_hewan_logic()
        return render(request, "jenis_hewan.html", context)
    
    if request.POST:
        nama_jenis = request.POST["nama_jenis"]
        create = create_jenis_hewan_logic(nama_jenis)
        context.update(create)
    elif request.method == 'PUT':
        data = json.loads(request.body)
        update = update_jenis_hewan(data)
        return JsonResponse(update)
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        delete = delete_jenis_hewan(data)
        return JsonResponse(delete)

    context["jenis_hewan"] = get_jenis_hewan_logic()
    return render(request, "jenis_hewan.html", context)


def get_jenis_hewan_logic():

    all_jenis_hewan = []

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PETCLINIC.JENIS_HEWAN;")
        jenis = cursor.fetchall()

        
        for i,j in jenis:
            jenis_hewan_dto = {
                "id" : i,
                "nama_jenis" : j
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

    context["jenis_hewan"] = get_jenis_hewan_logic()

    with connection.cursor() as cursor:

        ANIMAL_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, 'jenis_hewan.animal_types')

        id_jenis = str(uuid.uuid5(ANIMAL_NAMESPACE, nama_jenis))
        try:
            cursor.execute(
            """
            INSERT INTO PETCLINIC.jenis_hewan (id, nama_jenis)     
            VALUES (%s, %s)
            """,
            [id_jenis,nama_jenis,])

            context['success'] = "Berhasil menambahkan jenis hewan"
        except IntegrityError as e:
            context["error"] = f"Gagal menambahkan jenis hewan karena: {e}"
    
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
