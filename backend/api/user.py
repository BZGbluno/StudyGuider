from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
import os
import asyncpg
from fastapi.responses import JSONResponse
from fastapi import status
from typing import Annotated
import bcrypt
from fastapi.encoders import jsonable_encoder
# from .securityHelper import create_access_token

router = APIRouter()

class User(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=150)]
    email: Annotated[EmailStr, Field(...)]
    password: str
    first_name: Annotated[str | None, Field(default=None)]
    last_name: Annotated[str | None, Field(default=None)]
    provider: Annotated[str | None, Field(default=None)]
    provider_id: Annotated[str | None, Field(default=None)]


@router.post("/api/createUser")
async def createUser(userData: User):
    '''
    This endpoint will create a user with user level privledges.
    Input:

        json = {
        "username": "firerazor420Blazer",
        "email": "minecrafter8@icloud.com",
        "password": "alibutt",
        "first_name": "Niv",
        "last_name": "Butt",
        "provider": None,
        "provider_id": None
        }

    '''


    username = userData.username
    email = userData.email
    password = userData.password
    firstName = userData.first_name
    lastName = userData.last_name
    provider = userData.provider
    providerID = userData.provider_id


    # hash the password
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

        try :
            
            row = await conn.fetchrow(
            """
            INSERT INTO users
              (username, email, password_hash,
               first_name, last_name,
               provider, provider_id)
            VALUES
              ($1, $2, $3, $4, $5, $6, $7)
            RETURNING
              id, username, email,
              first_name, last_name,
              created_at, provider,
              provider_id, auth_level;
            """,
            username,
            email,
            password_hash,
            firstName,
            lastName,
            provider,
            providerID,
        )
            
        except Exception as e:
            raise HTTPException(500, "Error in make a user")

        user_dict = dict(row)
        # token = create_access_token(subject=user_dict["username"])

        response_content = {
            "id":          user_dict["id"],
            "username":    user_dict["username"],
            "email":       user_dict["email"],
            "first_name":  user_dict["first_name"],
            "last_name":   user_dict["last_name"],
            "created_at":  user_dict["created_at"],
            "provider":    user_dict["provider"],
            "provider_id": user_dict["provider_id"],
            "auth_level":  user_dict["auth_level"],
            # "access_token": token,
            # "token_type":   "bearer"
        }

        try:
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=jsonable_encoder({"response": response_content})
            )
        except Exception as e:
            print("Serialization error:", e)
            raise
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        await conn.close()




class UserBasic(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=150)]
    password: str


@router.post("/api/getUser")
async def retrieveUser(userIdentity: UserBasic):

    username = userIdentity.username
    password = userIdentity.password.encode('utf-8')


    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

            
        user = await conn.fetchrow(
        """
        SELECT id, username, email,
                password_hash, first_name,
                last_name,
                provider, provider_id,
                auth_level
        FROM users
        WHERE username = $1
        """, username
        )


        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username"
            )
        
        
        stored_hash = user["password_hash"]
        stored_hash = stored_hash.encode("utf-8")

        if not bcrypt.checkpw(password, stored_hash):
            print("🔒 Password check failed!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        
        user_dict = dict(user)
        user_dict.pop("password_hash")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": user_dict}
        )
    

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        await conn.close()



@router.post("/api/deleteUser")
async def retrieveDeleteUser(userIdentity: UserBasic):


    username = userIdentity.username
    password = userIdentity.password.encode('utf-8')


    try:
        conn = await asyncpg.connect(
        host=os.getenv("DATABASE_HOST"),
        database=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
        )

            
        user = await conn.fetchrow(
        """
        SELECT id, username, email,
                password_hash, first_name,
                last_name,
                provider, provider_id,
                auth_level
        FROM users
        WHERE username = $1
        """, username
        )


        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username"
            )
        
        
        stored_hash = user["password_hash"]
        stored_hash = stored_hash.encode("utf-8")

        if not bcrypt.checkpw(password, stored_hash):
            print("🔒 Password check failed!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        

        # remove the user
        user_dict = dict(user)
        user_dict.pop("password_hash")

        user = await conn.execute(
        """
        DELETE FROM users
        WHERE id = $1
        """, user_dict['id']
        )


        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"response": user_dict}
        )
    

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    finally:
        await conn.close()