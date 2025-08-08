from typing import Dict, Set
from .config.fixtures import initialized_user_api_client
from wt_authlib.user_api_settings import UserApiSettings


def test_get_endpoint(initialized_user_api_client):  # noqa: F811
    """ Test la récupération de l'url de l'endpoint """
    user_api_settings: UserApiSettings = initialized_user_api_client.get_user_api_settings()
    endpoint: str = user_api_settings.get_endpoint("login")
    assert len(endpoint) > 0

def test_get_aws_keys(initialized_user_api_client) : # noqa: F811
    """ Test la présence des clés attendues dans le dictionnaire retourné par get_aws_keys """
    user_api_settings: UserApiSettings = initialized_user_api_client.get_user_api_settings()
    aws_keys: Dict = user_api_settings.get_aws_keys()
    keys: Set = {'AWS_REGION_NAME', 'AWS_COGNITO_USER_POOL_ID', 'AWS_COGNITO_APP_CLIENT_ID'}
    assert keys.issubset(set(aws_keys.keys()))
    