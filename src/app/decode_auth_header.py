import jwt
from fastapi import HTTPException, status
from app.config import SECRET_KEY


def decode_auth_header(auth_header: str):
    """
    Проверяет Authorization header и возвращает user_id из токена.
    Пример: Authorization: Bearer <access_token>
    """
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    token = auth_header.split(" ")[1]

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], verify=False)
        user_id = decoded_token.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
