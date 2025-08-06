from ya_market_api.base.dataclass import BaseResponse
from ya_market_api.offer.const import (
	CatalogLanguageType, OfferCardStatusType, CurrencyType, AgeUnit, CampaignStatusType, CommodityCodeType,
	OfferConditionQualityType, OfferConditionType, TimeUnit, MediaFileUploadState, SellingProgramType,
	SellingProgramStatusType, OfferType,
)

from typing import Final, Set, Optional, Collection, List, Dict, Any, overload
from warnings import warn

from pydantic.main import BaseModel
from pydantic.fields import Field
from pydantic.config import ConfigDict
from pydantic.functional_validators import field_validator
from pydantic.functional_serializers import field_serializer
from arrow import Arrow, get as get_arrow


CardStatusesParam = Optional[Collection[OfferCardStatusType]]
CategoryIdsParam = Optional[Collection[int]]
OfferIdsParam = Optional[Collection[str]]
TagsParam = Optional[Collection[str]]
VendorNamesParam = Optional[Collection[str]]


class Request(BaseModel):
	QUERY_PARAMS: Final[Set[str]] = {"language", "limit", "page_token"}
	S11N_ALIAS_OFFER_IDS: Final[str] = "offerIds"
	model_config = ConfigDict(arbitrary_types_allowed=True)

	# query params
	language: Optional[CatalogLanguageType] = None
	limit: Optional[int] = Field(default=None)
	page_token: Optional[str] = None

	# payload v1
	archived: Optional[bool] = None
	card_statuses: CardStatusesParam = Field(default=None, serialization_alias="cardStatuses")
	category_ids: CategoryIdsParam = Field(default=None, serialization_alias="categoryIds")
	tags: TagsParam = None
	vendor_names: VendorNamesParam = Field(default=None, serialization_alias="vendorNames")

	# payload v2
	offer_ids: OfferIdsParam = Field(default=None, serialization_alias=S11N_ALIAS_OFFER_IDS)

	@overload
	def __init__(self, *, offer_ids: Collection[str]) -> None: ...
	@overload
	def __init__(
		self,
		*,
		language: Optional[CatalogLanguageType] = None,
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
		archived: Optional[bool] = None,
		card_statuses: CardStatusesParam = None,
		category_ids: CategoryIdsParam = None,
		tags: TagsParam = None,
		vendor_names: VendorNamesParam = None,
	) -> None: ...
	def __init__(
		self,
		*,
		language: Optional[CatalogLanguageType] = None,
		limit: Optional[int] = None,
		page_token: Optional[str] = None,
		archived: Optional[bool] = None,
		card_statuses: CardStatusesParam = None,
		category_ids: CategoryIdsParam = None,
		tags: TagsParam = None,
		vendor_names: VendorNamesParam = None,
		offer_ids: OfferIdsParam = None,
	) -> None:
		super().__init__(
			language=language,
			limit=limit,
			page_token=page_token,
			archived=archived,
			card_statuses=card_statuses,
			category_ids=category_ids,
			tags=tags,
			vendor_names=vendor_names,
			offer_ids=offer_ids,
		)

	@field_validator("limit", mode="after")
	@classmethod
	def limit_must_be_greater_than_0(cls, value: Optional[int]) -> Optional[int]:
		if value is None:
			return None

		if value < 1:
			raise ValueError("Limit cannot be less than 1")

		return value

	@field_validator("card_statuses", mode="after")
	@classmethod
	def card_statuses_must_be_filled(cls, value: CardStatusesParam) -> CardStatusesParam:
		if value is None:
			return None

		if len(value) < 1:
			raise ValueError("Card statuses length cannot be less than 1")

		return value

	@field_validator("category_ids", mode="after")
	@classmethod
	def category_ids_must_be_filled(cls, value: CategoryIdsParam) -> CategoryIdsParam:
		if value is None:
			return None

		if len(value) < 1:
			raise ValueError("Category ids length cannot be less than 1")

		return value

	@field_validator("offer_ids", mode="after")
	@classmethod
	def offer_ids_must_be_filled(cls, value: OfferIdsParam) -> OfferIdsParam:
		if value is None:
			return None

		if len(value) < 1:
			raise ValueError("Offer ids length cannot be less than 1")
		elif len(value) > 200:
			raise ValueError("Offer ids length cannot be greater than 200")

		for offer_id in value:
			if len(offer_id) < 1:
				raise ValueError("Offer id length cannot be less than 1")
			elif len(offer_id) > 250:
				raise ValueError("Offer id length cannot be greater than 250")

		return value

	@field_validator("tags", mode="after")
	@classmethod
	def tags_must_be_filled(cls, value: TagsParam) -> TagsParam:
		if value is None:
			return None

		if len(value) < 1:
			raise ValueError("Tags length cannot be less than 1")

		return value

	@field_validator("vendor_names", mode="after")
	@classmethod
	def vendor_names_must_be_filled(cls, value: VendorNamesParam) -> VendorNamesParam:
		if value is None:
			return None

		if len(value) < 1:
			raise ValueError("Vendor names length cannot be less than 1")

		return value

	@field_serializer("language")
	def serialize_language(self, value: Optional[CatalogLanguageType]) -> Optional[str]:
		if value is None:
			return None

		return value.value

	@field_serializer("card_statuses")
	def serialize_card_statuses(self, value: CardStatusesParam) -> Optional[List[str]]:
		if value is None:
			return None

		return [i.value for i in value]

	def model_dump_request_params(self) -> Dict[str, Any]:
		result = self.model_dump(include=self.QUERY_PARAMS, by_alias=True, exclude_none=True)

		if self.offer_ids is not None and len(result) != 0:
			warn("When using offer_ids, the other query parameters will be ignored")
			result = {}

		return result

	def model_dump_request_payload(self) -> Dict[str, Any]:
		result = self.model_dump(exclude=self.QUERY_PARAMS, by_alias=True, exclude_none=True)

		if self.offer_ids is not None and len(result) != 1:
			warn("When using offer_ids, the other parameters will be ignored")
			result = {self.S11N_ALIAS_OFFER_IDS: result[self.S11N_ALIAS_OFFER_IDS]}

		return result


############
# RESPONSE #
############
class Mapping(BaseModel):
	market_category_id: Optional[int] = Field(default=None, validation_alias="marketCategoryId")
	market_category_name: Optional[str] = Field(default=None, validation_alias="marketCategoryName")
	market_sku: Optional[int] = Field(default=None, validation_alias="marketSku")
	market_sku_name: Optional[str] = Field(default=None, validation_alias="marketSkuName")


class Price(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	currency_id: CurrencyType = Field(validation_alias="currencyId")
	updated_at: Arrow = Field(validation_alias="updatedAt")
	value: float

	@field_validator("updated_at", mode="before")
	@classmethod
	def datetimes_must_be_arrow(cls, value: str) -> Arrow:
		return get_arrow(value)


class Age(BaseModel):
	unit: AgeUnit = Field(validation_alias="ageUnit")
	value: float


class BasicPrice(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True)

	updated_at: Arrow = Field(validation_alias="updatedAt")
	currency_id: Optional[CurrencyType] = Field(default=None, validation_alias="currencyId")
	discount_base: Optional[int] = Field(default=None, validation_alias="discountBase")
	value: Optional[float] = None

	@field_validator("updated_at", mode="before")
	@classmethod
	def datetimes_must_be_arrow(cls, value: str) -> Arrow:
		return get_arrow(value)


class CampaignStatus(BaseModel):
	campaign_id: int = Field(validation_alias="campaignId")
	status: CampaignStatusType


class CommodityCode(BaseModel):
	code: str
	type: CommodityCodeType


class OfferCondition(BaseModel):
	quality: Optional[OfferConditionQualityType] = None
	reason: Optional[str] = None
	type: Optional[OfferConditionType] = None


class TimePeriod(BaseModel):
	period: int = Field(validation_alias="timePeriod")
	unit: TimeUnit = Field(validation_alias="timeUnit")
	comment: Optional[str] = None


class OfferManual(BaseModel):
	url: str
	title: Optional[str] = None


class OfferMediaFile(BaseModel):
	title: Optional[str] = None
	upload_state: Optional[MediaFileUploadState] = None
	url: Optional[str] = None


class OfferMediaFiles(BaseModel):
	first_video_as_cover: Optional[bool] = Field(default=None, validation_alias="firstVideoAsCover", deprecated=True)
	manuals: List[OfferMediaFile] = Field(default_factory=list)
	pictures: List[OfferMediaFile] = Field(default_factory=list)
	videos: List[OfferMediaFile] = Field(default_factory=list)


class OfferSellingProgram(BaseModel):
	selling_program: SellingProgramType = Field(validation_alias="sellingProgram")
	status: SellingProgramStatusType


class WeightDimensions(BaseModel):
	height: float
	length: float
	weight: float
	width: float


class Offer(BaseModel):
	id: str = Field(validation_alias="offerId")
	additional_expenses: Optional[Price] = Field(default=None, validation_alias="additionalExpenses")		# TODO: Add type
	adult: Optional[bool] = None
	age: Optional[Age] = None
	archived: Optional[bool] = None
	barcodes: List[str] = Field(default_factory=list)
	basic_price: Optional[BasicPrice] = Field(default=None, validation_alias="basicPrice")
	box_count: Optional[int] = Field(default=None, validation_alias="boxCount")
	campaigns: List[CampaignStatus] = Field(default_factory=list)
	card_status: Optional[OfferCardStatusType] = Field(default=None, validation_alias="cardStatus")
	certificates: List[str] = Field(default_factory=list, validation_alias="certificates")
	commodity_codes: List[CommodityCode] = Field(default_factory=list, validation_alias="commodityCodes")
	condition: Optional[OfferCondition] = None
	description: Optional[str] = None
	downloadable: Optional[bool] = None
	guarantee_period: Optional[TimePeriod] = Field(default=None, validation_alias="guaranteePeriod")
	life_time: Optional[TimePeriod] = Field(default=None, validation_alias="lifeTime")
	manuals: List[OfferManual] = Field(default_factory=list)
	manufacturer_countries: List[str] = Field(default_factory=list, validation_alias="manufacturerCountries")
	market_category_id: Optional[int] = Field(default=None, validation_alias="marketCategoryId")		# Seems to be abandoned
	media_files: Optional[OfferMediaFiles] = Field(default=None, validation_alias="mediaFiles")
	name: Optional[str] = None
	pictures: List[str] = Field(default_factory=list)
	purchase_price: Optional[Price] = Field(default=None, validation_alias="purchasePrice")
	selling_programs: List[OfferSellingProgram] = Field(default_factory=list, validation_alias="sellingParams")
	shelf_life: Optional[TimePeriod] = Field(default=None, validation_alias="shelfLife")
	tags: List[str] = Field(default_factory=list)
	type: Optional[OfferType] = None
	vendor: Optional[str] = None
	vendor_code: Optional[str] = Field(default=None, validation_alias="vendorCode")
	videos: List[str] = Field(default_factory=list)
	weight_dimensions: Optional[WeightDimensions] = Field(default=None, validation_alias="weightDimensions")


class OfferMappings(BaseModel):
	mapping: Optional[Mapping] = None
	offer: Optional[Offer] = None


class Paging(BaseModel):
	next_page_token: Optional[str] = Field(default=None, validation_alias="nextPageToken")
	prev_page_token: Optional[str] = Field(default=None, validation_alias="prevPageToken")


class ResponseResult(BaseModel):
	offer_mappings: List[OfferMappings] = Field(validation_alias="offerMappings")
	paging: Optional[Paging] = None


class Response(BaseResponse):
	result: Optional[ResponseResult] = None
