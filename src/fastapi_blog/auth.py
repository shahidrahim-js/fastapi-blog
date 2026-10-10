from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from fastapi_blog.config import settings

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

# Password hashing function
# This takes a plain password and returns a hashed password.
def hash_password(password: str) -> str:
  return password_hash.hash(password)

# Verify password function
# It takes plain password and hashed password, it returns true if they match else returns false
def verify_password(plain_password: str, hashed_password: str) -> bool:
  return   password_hash.verify(plain_password, hashed_password)

# Create access token function, that returns a JWT token.
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
  """Create a JWT access token."""
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(UTC) + expires_delta
  else:
    expire = datetime.now(UTC) + timedelta(
      minutes=settings.access_token_expire_minutes
    )
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(
    to_encode,
    settings.secret_key.get_secret_value(),
    algorithm=settings.algorithm
  )
  return encoded_jwt

# Verify access token function
def verify_access_token(token: str) -> str | None:
  """Verify a JWT access token and return the subject (user id) if valid."""
  try:
    payload = jwt.decode(
      token,
      settings.secret_key.get_secret_value(),
      algorithms=[settings.algorithm],
      options={"require": ["exp", "sub"]}
    )
  except jwt.InvalidTokenError:
    return None
  else:
    return payload.get("sub") # Stored the user id in sub field when we create the token and extracting from there
