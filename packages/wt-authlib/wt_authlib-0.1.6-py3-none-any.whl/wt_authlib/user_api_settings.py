
import redis
from logging import getLogger
from typing import Dict
from urllib.parse import urljoin
from .errors import UserApiException

logger = getLogger(__name__)


class UserApiSettings:
	"""
	Cette classe gère l'acces au repository redis pour l'api wt_user.
	Les informations sont mises dans redis par l'API wt_user.
	Permet de récupérer les endpoints et les clés AWS.
	
	Args:
		host: host de la base redis
		port: port de la base redis
		username: username de la base redis
		password: password de la base redis
	"""
	def __init__(self, host: str, port: int, username: str, password: str):
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.user_api_url = None
		self.redis_client: redis.Redis = redis.Redis(
			host=host,
			port=port,
			decode_responses=True,
			username=username,
			password=password,
		)

	def get_user_api_url(self) -> str:
		"""
		Retourne l'url de l'api wt_user qui se trouve dans la base de données wt_user.
		"""
		try:
			if not self.user_api_url:
				self.user_api_url = self.get_endpoint('base_url').strip().rstrip('/')
			return self.user_api_url
		except UserApiException as exc:
			logger.error(exc)
			raise UserApiException(exc.status_code, exc.message)
		except Exception as exc:
			logger.error(exc)
			raise UserApiException(500, "Error while getting user api url")

	def get_endpoint(self, key: str) -> str:
		"""
		Retourne l'url de l'api en fonction de la clé passée en paramètre.
		"""
		try:
			endpoint:str = self.redis_client.get(key)
			endpoint = endpoint.strip().rstrip('/')
			if endpoint:
				return urljoin(self.user_api_url, endpoint)
			else:
				raise UserApiException(422, "Endpoint not found")
		except Exception as exc:
			logger.error(exc)
			raise UserApiException(500, "Error while getting endpoint")

	def get_aws_keys(self) -> Dict[str, str]:
		try:
			keys = ['AWS_REGION_NAME', 'AWS_COGNITO_USER_POOL_ID', 'AWS_COGNITO_APP_CLIENT_ID']
			values = self.redis_client.mget(keys)
			return dict(zip(keys, values))
		except Exception as exc:
			logger.error(exc)
			raise exc