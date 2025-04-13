# import os
# from datetime import datetime, timedelta
# from jose import jwt
# from fastapi import HTTPException, status

# SECRET_KEY = os.getenv("JWT_SECRET")
# ALGORITHM  = os.getenv("JWT_ALGORITHM")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
#     '''
#     This will handle the creation of auth tokens
#     '''

#     to_encode = {"sub": subject}
#     expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})

#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
