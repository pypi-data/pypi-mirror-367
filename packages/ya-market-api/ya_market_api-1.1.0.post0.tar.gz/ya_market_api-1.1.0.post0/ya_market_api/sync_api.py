from ya_market_api.const import Header, BASE_URL
from ya_market_api.generic.requests.auth import APIKeyAuth
from ya_market_api.guide.sync_api import SyncGuideAPI
from ya_market_api.feedback.sync_api import SyncFeedbackAPI
from ya_market_api.offer.sync_api import SyncOfferAPI
from ya_market_api.base.sync_config import SyncConfig

from typing import Optional

from requests.sessions import Session


class SyncAPI:
	guide: SyncGuideAPI
	feedback: SyncFeedbackAPI
	offer: SyncOfferAPI
	config: SyncConfig

	def __init__(self, config: SyncConfig) -> None:
		self.config = config
		self.guide = SyncGuideAPI(config)
		self.feedback = SyncFeedbackAPI(config)
		self.offer = SyncOfferAPI(config)

	@classmethod
	def build(cls, api_key: str, *, business_id: Optional[int] = None, base_url: str = BASE_URL) -> "SyncAPI":
		config = SyncConfig(
			cls.make_session(api_key),
			business_id,
			base_url,
		)

		return cls(config)

	@staticmethod
	def make_session(api_key: str) -> Session:
		session = Session()
		session.auth = APIKeyAuth(api_key, Header.API_KEY.value)

		return session
