from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from .user_validator import AWSTokenValidator


def validate_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    Methode à ajouter dans les dépendances des routes ou des endpoints.
    Exemple:
        ```python
        router = APIRouter()
        @router.get("/protected", dependencies=[Depends(validate_user)])
        async def protected_route(user: AWSTokenValidator = Depends(validate_user)):
            return {"message": "This is a protected route"}
        ou
        router.include_router(router, dependencies=[Depends(validate_user)])
        ```
    args:
        credentials: credentials de l'utilisateur
    """
    return AWSTokenValidator(credentials.credentials)
