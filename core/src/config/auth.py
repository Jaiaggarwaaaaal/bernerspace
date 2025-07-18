from fastapi import HTTPException

def get_current_user_email():
    # TODO: replace with real GitHub OAuth flow
    # For now, return a placeholder email or raise if unauthenticated
    user_email = "test@example.com"
    if not user_email:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_email