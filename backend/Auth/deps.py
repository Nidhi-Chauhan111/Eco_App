# backend/Auth/deps.py
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import InvalidHeaderError, JWTDecodeError, RevokedTokenError

def get_current_user(Authorize: AuthJWT = Depends()):
    """
    Dependency that requires a valid JWT and returns the subject (user id).
    Raises HTTPException with appropriate status codes/messages on failure.
    """
    try:
        Authorize.jwt_required()
    except InvalidHeaderError as e:
        msg = getattr(e, "message", None) or str(e) or "Invalid or missing Authorization header"
        raise HTTPException(status_code=422, detail=msg)
    except (JWTDecodeError, RevokedTokenError) as e:
        msg = getattr(e, "message", None) or str(e) or "Invalid or expired token"
        raise HTTPException(status_code=401, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e) or "JWT error")

    try:
        user_id = Authorize.get_jwt_subject()
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to extract user from token")
    try:
        return int(user_id)
    except Exception:
        return user_id