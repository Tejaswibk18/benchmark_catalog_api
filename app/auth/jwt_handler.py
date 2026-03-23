from jose import jwt
from datetime import datetime, timedelta
from app.utils.config import SECRET_KEY, ALGORITHM, TOKEN_EXPIRE_HOURS


def create_token(data: dict):

    payload = data.copy()

    payload.update({
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }) 

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):

    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])