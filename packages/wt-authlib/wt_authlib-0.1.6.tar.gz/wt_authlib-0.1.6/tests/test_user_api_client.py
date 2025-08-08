from typing import Tuple
import pytest
from .config.fixtures import initialized_user_api_client  # noqa: F401
from .config.settings import settings
from wt_authlib.errors import UserApiException
from wt_authlib.user_api_client import UserApiClient
from wt_authlib.user_api_settings import UserApiSettings

def get_user_api_tools(user_api_client:UserApiClient)->Tuple[UserApiClient, UserApiSettings]:
    """ Retourne l'instance du UserApiClient et de UserApiSettings """
    api_client: UserApiClient = user_api_client
    api_settings: UserApiSettings = api_client.get_user_api_settings()
    return api_client, api_settings


def test_not_initialized_user_api_client():
    """ Test le retour d'erreur si le UserApiClient n'est pas initialise """
    with pytest.raises(UserApiException) as exc_info:
        UserApiClient.get_user_api_settings()
    assert exc_info.value.status_code == 422
    assert str(exc_info.value) == "UserApiClient must be initialized first"


def test_initialized_user_api_client(initialized_user_api_client):  # noqa: F811
    """ Test le l'initialisation du UserApiClient """
    api_client, api_settings = get_user_api_tools(initialized_user_api_client)
    assert api_settings.host == settings.host
    assert api_settings.port == settings.port
    assert api_settings.username == settings.settings_username
    assert api_settings.password == settings.settings_password
    assert "https" in api_settings.get_user_api_url()
   

@pytest.mark.asyncio
async def test_bad_login(initialized_user_api_client):  # noqa: F811
    """ Test la connexion à l'api """
    api_client, api_settings = get_user_api_tools(initialized_user_api_client)
    with pytest.raises(UserApiException) as exc_info:
        await api_client.login(username="not_existing_user", password="not_existing_password")
    assert exc_info.value.status_code == 401
    

@pytest.mark.asyncio
async def test_good_login(initialized_user_api_client):  # noqa: F811
    """ Test la connexion à l'api """
    api_client, api_settings = get_user_api_tools(initialized_user_api_client)
    response = await api_client.login(username=settings.api_username, password=settings.api_password)
    assert response['token'] is not None
    