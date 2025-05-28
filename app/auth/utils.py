import jwt
import bcrypt
from app.core.config import settings
import datetime


def encode_jwt(
        payload: dict,
        private_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: datetime.timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.datetime.now(datetime.UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + datetime.timedelta(minutes=expire_minutes)
    to_encode.update(
        iat=now,
        exp=expire
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm,
    )
    return encoded


def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm
):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def create_cookie(
        token: str,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: datetime.timedelta | None = None,
) -> dict:
    now = datetime.datetime.now(datetime.UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + datetime.timedelta(minutes=expire_minutes)
    d = dict(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.auth_jwt.access_token_expire_minutes * 60,
        expires=expire,
        path="/",
        secure=False,  # ставь True, если работает через HTTPS
        samesite="Lax"
    )
    return d
