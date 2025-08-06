from ya_market_api.const import Header, BASE_URL
from ya_market_api.guide.async_api import AsyncGuideAPI
from ya_market_api.feedback.async_api import AsyncFeedbackAPI
from ya_market_api.offer.async_api import AsyncOfferAPI
from ya_market_api.base.async_config import AsyncConfig

from typing import Optional

from aiohttp.client import ClientSession


class AsyncAPI:
	guide: AsyncGuideAPI
	feedback: AsyncFeedbackAPI
	offer: AsyncOfferAPI
	config: AsyncConfig

	def __init__(self, config: AsyncConfig) -> None:
		self.config = config
		self.guide = AsyncGuideAPI(config)
		self.feedback = AsyncFeedbackAPI(config)
		self.offer = AsyncOfferAPI(config)

	async def close(self) -> None:
		await self.config.session.close()

	@classmethod
	async def build(cls, api_key: str, *, business_id: Optional[int] = None, base_url: str = BASE_URL) -> "AsyncAPI":
		config = AsyncConfig(
			await cls.make_session(api_key),
			business_id,
			base_url,
		)

		return cls(config)

	@staticmethod
	async def make_session(api_key: str) -> ClientSession:
		session = ClientSession(headers={Header.API_KEY.value: api_key})
		return session
