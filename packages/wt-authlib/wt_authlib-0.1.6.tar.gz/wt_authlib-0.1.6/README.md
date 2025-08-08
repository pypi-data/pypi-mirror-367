# README.md
# wt-authlib

Librairie d'authentification pour l'api wt_user. 
Cette librairie permet de sécuriser un projet FastAPI. Seules les personnes avec un compte WT pourront accéder l'API protégée.
Cette librairie se connecte à la base de donnée associée à wt_user pour récupérer les settings, les endpoints etc

## Fonctionnalités
- Permet de s'identifier à WT et récupérer un Bearer
- Décodage et validation des tokens Bearer pour les endpoints ou routers protégés
- Intégration facile avec FastAPI via `Depends`

## Installation
```bash
uv pip install wt_authlib
```

## Initialisation

Une fois installée, il est essentiel d'initialiser UserApi dans un lifespan FastAPI

```python
from contextlib import asynccontextmanager
from wt_authlib.user_api_client import UserApiClient

@asynccontextmanager
async def lifespan(_: FastAPI):
	UserApiClient.init(
		host="url de la base de données de wt_user",
		port="port la base de données de wt_user",
		username="username admin de la base de données de wt_user",
		password="passwaord admin de la base de données de wt_user",
	)
	yield

app = FastAPI(lifespan=lifespan)

```

## Sécurisation
il faut ajouter la méthode validate_user comme dépendance (Depends) aux endpoints ou routeur

### exemple ajout router

```python

from fastapi import APIRouter, Depends
from wt_authlib.fastapi_depends import validate_user

routeur = APIRouter()
routeur.include_router(
    document.router,
	dependencies=[Depends(validate_user)]
)
```

### exemple ajout endpoint
```python

from wt_authlib import validate_user

app = FastAPI()

@app.get("/private", dependencies=[Depends(validate_user)])
async def private_route():
    return {"message": "Bienvenue, utilisateur authentifié"}
```


## Login 
Une fois l'api sécurisé, il est est nécessaire de se loguer pour recevoir un Bearer token depuis wt_user.
Utilisez la methode UserApiClient.login() avec les credentials pour recevoir un token.


### Exemple avec un endpoint Fastapi
```python

from wt_authlib.user_api_client import UserApiClient
from wt_authlib.errors import UserApiException

@router.post("/login")
async def login(username: str, password: str):
    try:
        return await UserApiClient.login(username, password)
    except UserApiException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

```