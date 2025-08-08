from typing import Dict
import pytest
from wt_authlib.errors import UserApiException
from wt_authlib.user_validator import AWSTokenValidator
from wt_authlib.user_api_client import UserApiClient
from wt_authlib.user_api_settings import UserApiSettings
from .config.fixtures import initialized_user_api_client, login_response  # noqa: F401
from .config.settings import settings


@pytest.mark.asyncio
async def test_login_and_validate_real_token(login_response: Dict) -> None:  # noqa: F811
    """Test la connexion avec de vrais credentials et validation du token obtenu."""
    
    assert login_response['token'] is not None
    token = login_response['token']
    
    # Test de la validation du token obtenu
    try:
        validator = AWSTokenValidator(token)
        assert validator.token == token
        assert validator.required_token_use == "access"
    except UserApiException as e:
        print(f"Erreur de validation du token: {e.status_code}")
        raise

def test_validate_empty_token() -> None:  # noqa: F811
    """Test la validation avec un token vide."""
    with pytest.raises(UserApiException) as exc_info:
        AWSTokenValidator("")
    assert exc_info.value.status_code == 401
    

def test_validate_invalid_token_format() -> None:
    """Test la validation avec un token de format invalide."""
    with pytest.raises(UserApiException) as exc_info:
        AWSTokenValidator("invalid_token_format")
    assert exc_info.value.status_code == 401
    