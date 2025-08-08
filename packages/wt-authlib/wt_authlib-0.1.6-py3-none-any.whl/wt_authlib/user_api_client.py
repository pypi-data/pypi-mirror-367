
from typing import Dict
import json
import aiohttp
import aiohttp.http_exceptions
from aiohttp import ClientError, ClientResponseError, ClientConnectionError, ServerTimeoutError, ClientPayloadError
from logging import getLogger

from .errors import UserApiException
from .user_api_settings import UserApiSettings


logger = getLogger(__name__)

class UserApiClient:
    """
    Client pour l'API wt_user.
    """
    _user_api_settings: UserApiSettings = None
    _user_api_url: str = ""

    @classmethod
    def init(cls, host: str, port: int, username: str, password: str):
        """
        Initialise UserApi.
        args:
            user_api_url: url de l'api wt_user
            host: host de la base redis
            port: port de la base redis
            username: username de la base redis
            password: password de la base redis
        """
        # global _user_api_settings, _user_api_url
        UserApiClient._user_api_settings = UserApiSettings(host, port, username, password)
        UserApiClient._user_api_url = UserApiClient._user_api_settings.get_user_api_url()

    @classmethod    
    def get_user_api_settings(cls) -> UserApiSettings:
        """
        Retourne l'instance de UserApiSettings.
        """
        if not UserApiClient._user_api_settings:
            raise UserApiException(422, "UserApiClient must be initialized first")
        return UserApiClient._user_api_settings

    # @classmethod
    # def get_user_api_url(cls) -> str:
    #     """
    #     Retourne l'url de l'api wt_user.
    #     """
    #     if not UserApiClient._user_api_url:
    #         raise UserApiException(422, "UserApiClient must be initialized first")
    #     return UserApiClient._user_api_url

    @classmethod
    async def login(cls, username: str, password: str) -> Dict:
        """
        Login user.
        args:
            username: username de l'utilisateur
            password: password de l'utilisateur
        """
        try:
            url_login = UserApiClient._user_api_settings.get_endpoint("login")
            async with aiohttp.ClientSession(
                headers={
                    'accept': 'application/vnd.api+json',
                    'content-Type': 'application/vnd.api+json'
                }
            ) as session:
                async with session.request(
                    method="POST",
                    url=url_login,
                    json={'username': username, 'password': password}
                ) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        try:
                            error_json = json.loads(error_text)
                            detail = error_json.get("detail", error_text)
                        except json.JSONDecodeError:
                            detail = error_text
                        logger.error(f"Erreur API wt_user: {response.status} - {detail}")
                        raise UserApiException(response.status, detail)

                    token = response.headers.get('Authorization')
                    return {"token": token.split(' ')[1] if token else None}
        except ServerTimeoutError:
            logger.error("Timeout lors de la connexion à wt_user")
            raise UserApiException(504, "Timeout de l'API wt_user")
        except ClientConnectionError:
            logger.error("Erreur de connexion à wt_user")
            raise UserApiException(503, "Connexion impossible à l'API wt_user")
        except ClientResponseError as cre:
            logger.error(f"Erreur réponse client: {cre}")
            raise UserApiException(cre.status, cre.message)
        except ClientPayloadError as cpe:
            logger.error(f"Erreur de payload: {cpe}")
            raise UserApiException(400, "Erreur de payload envoyé à wt_user")
        except ClientError as ce:
            logger.error(f"Erreur client générique: {ce}")
            raise UserApiException(500, "Erreur client aiohttp")
        except UserApiException as usex:
            raise usex
        except Exception as exc:
            logger.error(f"Erreur inattendue: {exc}")
            raise UserApiException(500, "Erreur interne lors de l'appel à wt_user")
