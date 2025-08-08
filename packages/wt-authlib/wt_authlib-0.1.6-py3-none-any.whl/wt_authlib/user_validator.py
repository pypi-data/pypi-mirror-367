from typing import Dict
import jwt
from logging import getLogger
from .errors import UserApiException
from .user_api_client import UserApiClient

logger = getLogger(__name__)

# -----------------------------------------------------------------------------------------------
#  		   Classe permettant de valider un token JWT avec api wt_user
# 		Il faut ajouter une dépendance de la methode depuis fastapi_depends.py 
# 		dans les router ou les endpoints.
# 		IL EST NECESSAIRE D'INSTALLER ET PARAMETRER REDIS
# -----------------------------------------------------------------------------------------------

class AWSTokenValidator:
	"""
	Valide le token JWT de l'utilisateur en utilisant l'api wt_user et les cles aws pour un traitement local
	l'api wt_user permet de creer et valider les comptes user en utilisant aws_cognito.
	"""
	def __init__(self, token: str) -> None:
		self.token = token
		self.required_token_use = "access"
		self.user_api_settings = UserApiClient().get_user_api_settings()
		self.aws_keys: Dict = self.user_api_settings.get_aws_keys()
		self.__validate_token()


	def __validate_token(self) -> None:
		"""Processus complet de validation du token JWT"""
		try:
			print(f"------------------ Token: {self.token}")
			if not self.token:
				raise UserApiException(status_code=401, message="Invalid or missing token")
			signing_key = self.__get_signing_key(self.token)
			claims = self.__decode_token(signing_key, self.token)
			self.__validate_audience(claims)
		except UserApiException as e:
			raise UserApiException(status_code=e.status_code, message=e.message)
		except Exception as e:
			raise UserApiException(status_code=500, message="Erreur lors de la validation du token") from e


	def __get_signing_key(self, token: str) -> jwt.PyJWK:
		"""Le client PyJWK est instancié a partir des clés AWS 
		   il permet ensuite de résoudre la clé de signature à partir du token.
		   les clés sont mises en cache pour 10 minutes.
		"""
		try:
			url_aws_key = (
				f"https://cognito-idp.{self.aws_keys['AWS_REGION_NAME']}.amazonaws.com/"
				f"{self.aws_keys['AWS_COGNITO_USER_POOL_ID']}/.well-known/jwks.json"
			)
			jwks_client = jwt.PyJWKClient(url_aws_key, cache_keys=True, lifespan=600)
			return jwks_client.get_signing_key_from_jwt(token)
		except jwt.exceptions.InvalidTokenError as e:
			raise UserApiException(status_code=401, message="Unauthorized") from e
		except Exception as e:
			raise UserApiException(status_code=500, message="Erreur lors de la récupération de la clé de signature") from e


	def __decode_token(self, signing_key: jwt.PyJWK, token: str) -> Dict:
		"""Décode le token JWT."""
		try:
			issuer = (
				f"https://cognito-idp.{self.aws_keys['AWS_REGION_NAME']}.amazonaws.com/"
				f"{self.aws_keys['AWS_COGNITO_USER_POOL_ID']}"
			)
			return jwt.decode(
				token,
				signing_key.key,
				algorithms=["RS256"],
				issuer=issuer,
				options={
					"verify_aud": False,
					"verify_signature": True,
					"verify_exp": False,
					"verify_iss": True,
					"require": ["token_use", "exp", "iss", "sub"],
				},
			)
			
		except jwt.exceptions.ExpiredSignatureError:
			raise UserApiException(status_code=401, message="Session expirée")
		except jwt.exceptions.InvalidTokenError:
			raise UserApiException(status_code=401, message="Unauthorized")
		except Exception as e:
			raise UserApiException(status_code=500, message="Erreur lors de la décodage du token") from e


	def __validate_audience(self, claims: Dict) -> None:
		"""Valide l'audience ou le client_id selon le type de token."""
		try:
			expected_value = self.aws_keys['AWS_COGNITO_APP_CLIENT_ID']
			token_use = self.required_token_use

			key = "aud" if token_use == "id" else "client_id"
			if claims.get(key) != expected_value:
					raise UserApiException(status_code=401, message="Unauthorized")
		except jwt.exceptions.InvalidTokenError:
			raise UserApiException(status_code=401, message="Unauthorized")
		except Exception as e:
			raise UserApiException(status_code=500, message="Erreur lors de la validation de l'audience") from e



