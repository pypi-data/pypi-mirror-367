from ya_market_api.offer.base_api import BaseOfferAPI
from ya_market_api.exception import BusinessIdError
from ya_market_api.base.config import Config

import pytest


class TestBaseOfferAPI:
	def test_business_id(self):
		config = Config(None, None, "")
		api = BaseOfferAPI(config)

		with pytest.raises(BusinessIdError, match=""):
			api.business_id

		config.business_id = 512
		assert api.business_id == 512
