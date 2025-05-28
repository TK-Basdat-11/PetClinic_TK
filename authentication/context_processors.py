def user_role(request):
    return {
        "user_role": request.session.get("user_role"),
        "email": request.session.get("email"),
        "is_auth":   request.session.get("is_auth", False),
        "user_id": request.session.get("user_id"),
    }