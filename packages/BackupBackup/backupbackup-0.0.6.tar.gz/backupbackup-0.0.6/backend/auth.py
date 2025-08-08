import base64
import json
import random
import secrets
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Annotated, Optional, Tuple

import jwt
from captcha.image import ImageCaptcha
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.openapi.models import OAuthFlowPassword, OAuthFlows
from fastapi.security import OAuth2, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from jwt import InvalidTokenError
from passlib.context import CryptContext
from redis import Redis
from sqlmodel import Session

from backend.config import Settings
from backend.database import get_db_session
from backend.database_utils import member_by_name
from backend.dependencies import get_settings
from backend.models import Member, TokenData


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str = None,
        scopes: dict = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        password_flow = OAuthFlowPassword(tokenUrl=token_url, scopes=scopes)
        flows = OAuthFlows(password=password_flow)
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        cookie_authorization: str = request.cookies.get("Authorization")

        scheme, param = get_authorization_scheme_param(cookie_authorization)

        if scheme.lower() == "bearer":
            authorization = True
        else:
            authorization = False

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return param


class OAuth2PasswordCaptchaRequestForm(OAuth2PasswordRequestForm):
    def __init__(
        self,
        *,
        grant_type: Annotated[Optional[str], Form(pattern="password")] = "password",
        username: Annotated[str, Form()],
        password: Annotated[str, Form()],
        scope: Annotated[str, Form()] = "",
        client_id: Annotated[Optional[str], Form()] = None,
        client_secret: Annotated[Optional[str], Form()] = None,
        captcha_code: Annotated[str, Form()],
        captcha_token: Annotated[str, Form()],
        wants_news: Annotated[Optional[bool], Form()] = None,
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.captcha_code = captcha_code
        self.captcha_token = captcha_token
        self.wants_news = wants_news


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearerCookie(token_url="membership")


def generate_ssh_keys() -> Tuple[bytes, bytes]:
    """
    The keys do not get saved and that is by design
    :return:
    """
    key = rsa.generate_private_key(
        backend=crypto_default_backend(), public_exponent=65537, key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption(),
    )
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH, crypto_serialization.PublicFormat.OpenSSH
    )
    return private_key, public_key


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def password_hash(password) -> str:
    return pwd_context.hash(password)


def authenticate_member(
    session: Session, username: str, password: str
) -> Member | bool:
    member = member_by_name(session=session, username=username)
    if not member:
        return False
    if not verify_password(password, member.password):
        return False
    return member


def create_captcha(
    settings: Settings,
    redis_client: Redis,
) -> Tuple[str, str]:
    possible_codes = settings.possible_captcha_codes
    random_selection = random.randint(0, len(possible_codes) - 1)
    code = possible_codes[random_selection]
    token = secrets.token_urlsafe(8)
    captcha_data = {
        "code": code,
        "created_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    redis_client.setex(
        name=f"captcha:{token}",
        time=settings.captcha_ttl,
        value=json.dumps(captcha_data),
    )
    image = ImageCaptcha()
    data: BytesIO = image.generate(code)
    data_bytes: bytes = data.getvalue()
    image_base64: str = base64.b64encode(data_bytes).decode("utf-8")
    return token, f"data:image/png;base64,{image_base64}"


def valid_captcha(logger, redis_client, form_data) -> bool:
    captcha_json = redis_client.get(f"captcha:{form_data.captcha_token}")
    if not captcha_json:
        logger.error(
            f"Captcha token not found on the server, username: '{form_data.username}'"
        )
        return False

    input_code = form_data.captcha_code.lower()
    captcha_data = json.loads(captcha_json)
    if not input_code == captcha_data["code"].lower():
        logger.info(f"Captcha not correct, username: '{form_data.username}'")
        return False

    return True


def create_access_token(
    data: dict,
    settings: Settings,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        payload=to_encode, key=str(settings.secret_key), algorithm=settings.hashing_algo
    )
    return encoded_jwt


async def get_current_member(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session, Depends(get_db_session)],
):
    """
    To be used only as dependency
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            jwt=token, key=str(settings.secret_key), algorithms=[settings.hashing_algo]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    member = member_by_name(session=session, username=token_data.username)
    if member is None:
        raise credentials_exception
    return member


async def get_current_active_member(
    current_member: Annotated[Member, Depends(get_current_member)],
) -> Member:
    """
    To be used only as dependency
    """
    if current_member.disabled_at_timestamp:
        raise HTTPException(status_code=400, detail="Inactive Member")
    return current_member
