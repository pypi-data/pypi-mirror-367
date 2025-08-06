from enum import Enum


class CatalogLanguageType(Enum):
	RU = "RU"		# русский
	UZ = "UZ"		# узбекский


class OfferCardStatusType(Enum):
	HAS_CARD_CAN_NOT_UPDATE = "HAS_CARD_CAN_NOT_UPDATE"		# Карточка Маркета.
	HAS_CARD_CAN_UPDATE = "HAS_CARD_CAN_UPDATE"		# Можно дополнить.
	HAS_CARD_CAN_UPDATE_ERRORS = "HAS_CARD_CAN_UPDATE_ERRORS"		# Изменения не приняты.
	HAS_CARD_CAN_UPDATE_PROCESSING = "HAS_CARD_CAN_UPDATE_PROCESSING"		# Изменения на проверке.
	NO_CARD_NEED_CONTENT = "NO_CARD_NEED_CONTENT"		# Создайте карточку.
	NO_CARD_MARKET_WILL_CREATE = "NO_CARD_MARKET_WILL_CREATE"		# Создаст Маркет.
	NO_CARD_ERRORS = "NO_CARD_ERRORS"		# Не создана из-за ошибки.
	NO_CARD_PROCESSING = "NO_CARD_PROCESSING"		# Проверяем данные.
	NO_CARD_ADD_TO_CAMPAIGN = "NO_CARD_ADD_TO_CAMPAIGN"		# Разместите товар в магазине.


class CurrencyType(Enum):
	RUR = "RUR"
	USD = "USD"
	EUR = "EUR"
	UAH = "UAH"
	AUD = "AUD"
	GBP = "GBP"
	BYR = "BYR"
	BYN = "BYN"
	DKK = "DKK"
	ISK = "ISK"
	KZT = "KZT"
	CAD = "CAD"
	CNY = "CNY"
	NOK = "NOK"
	XDR = "XDR"
	SGD = "SGD"
	TRY = "TRY"
	SEK = "SEK"
	CHF = "CHF"
	JPY = "JPY"
	AZN = "AZN"
	ALL = "ALL"
	DZD = "DZD"
	AOA = "AOA"
	ARS = "ARS"
	AMD = "AMD"
	AFN = "AFN"
	BHD = "BHD"
	BGN = "BGN"
	BOB = "BOB"
	BWP = "BWP"
	BND = "BND"
	BRL = "BRL"
	BIF = "BIF"
	HUF = "HUF"
	VEF = "VEF"
	KPW = "KPW"
	VND = "VND"
	GMD = "GMD"
	GHS = "GHS"
	GNF = "GNF"
	HKD = "HKD"
	GEL = "GEL"
	AED = "AED"
	EGP = "EGP"
	ZMK = "ZMK"
	ILS = "ILS"
	INR = "INR"
	IDR = "IDR"
	JOD = "JOD"
	IQD = "IQD"
	IRR = "IRR"
	YER = "YER"
	QAR = "QAR"
	KES = "KES"
	KGS = "KGS"
	COP = "COP"
	CDF = "CDF"
	CRC = "CRC"
	KWD = "KWD"
	CUP = "CUP"
	LAK = "LAK"
	LVL = "LVL"
	SLL = "SLL"
	LBP = "LBP"
	LYD = "LYD"
	SZL = "SZL"
	LTL = "LTL"
	MUR = "MUR"
	MRO = "MRO"
	MKD = "MKD"
	MWK = "MWK"
	MGA = "MGA"
	MYR = "MYR"
	MAD = "MAD"
	MXN = "MXN"
	MZN = "MZN"
	MDL = "MDL"
	MNT = "MNT"
	NPR = "NPR"
	NGN = "NGN"
	NIO = "NIO"
	NZD = "NZD"
	OMR = "OMR"
	PKR = "PKR"
	PYG = "PYG"
	PEN = "PEN"
	PLN = "PLN"
	KHR = "KHR"
	SAR = "SAR"
	RON = "RON"
	SCR = "SCR"
	SYP = "SYP"
	SKK = "SKK"
	SOS = "SOS"
	SDG = "SDG"
	SRD = "SRD"
	TJS = "TJS"
	THB = "THB"
	TWD = "TWD"
	BDT = "BDT"
	TZS = "TZS"
	TND = "TND"
	TMM = "TMM"
	UGX = "UGX"
	UZS = "UZS"
	UYU = "UYU"
	PHP = "PHP"
	DJF = "DJF"
	XAF = "XAF"
	XOF = "XOF"
	HRK = "HRK"
	CZK = "CZK"
	CLP = "CLP"
	LKR = "LKR"
	EEK = "EEK"
	ETB = "ETB"
	RSD = "RSD"
	ZAR = "ZAR"
	KRW = "KRW"
	NAD = "NAD"
	TL = "TL"
	UE = "UE"


class AgeUnit(Enum):
	YEAR = "YEAR"
	MONTH = "MONTH"


class CampaignStatusType(Enum):
	PUBLISHED = "PUBLISHED"		# Готов к продаже
	CHECKING = "CHECKING"		# На проверке
	DISABLED_BY_PARTNER = "DISABLED_BY_PARTNER"		# Скрыт вами
	DISABLED_AUTOMATICALLY = "DISABLED_AUTOMATICALLY"		# Отклонен
	REJECTED_BY_MARKET = "REJECTED_BY_MARKET"		# Исправьте ошибки
	CREATING_CARD = "CREATING_CARD"		# Создается карточка
	NO_CARD = "NO_CARD"		# Нужна карточка
	NO_STOCKS = "NO_STOCKS"		# Нет на складе
	ARCHIVED = "ARCHIVED"		# В архиве


class CommodityCodeType(Enum):
	CUSTOMS_COMMODITY_CODE = "CUSTOMS_COMMODITY_CODE"
	IKPU_CODE = "IKPU_CODE"


class OfferConditionQualityType(Enum):
	PERFECT = "PERFECT"		# идеальный
	EXCELLENT = "EXCELLENT"		# отличный
	GOOD = "GOOD"		# хороший
	NOT_SPECIFIED = "NOT_SPECIFIED"		# не выбран


class OfferConditionType(Enum):
	PREOWNED = "PREOWNED"		# бывший в употреблении товар, раньше принадлежал другому человеку
	SHOWCASESAMPLE = "SHOWCASESAMPLE"		# витринный образец
	REFURBISHED = "REFURBISHED"		# повторная продажа товара
	REDUCTION = "REDUCTION"		# товар с дефектами
	RENOVATED = "RENOVATED"		# восстановленный товар
	NOT_SPECIFIED = "NOT_SPECIFIED"		# не выбран


class TimeUnit(Enum):
	HOUR = "HOUR"		# час
	DAY = "DAY"		# сутки
	WEEK = "WEEK"		# неделя
	MONTH = "MONTH"		# месяц
	YEAR = "YEAR"		# год


class MediaFileUploadState(Enum):
	UPLOADING = "UPLOADING"		# загружается
	UPLOADED = "UPLOADED"		# успешно загружен
	FAILED = "FAILED"		# при загрузке произошла ошибка. Повторите попытку позже


class SellingProgramType(Enum):
	FBY = "FBY"		# FBY
	FBS = "FBS"		# FBS
	DBS = "DBS"		# DBS
	EXPRESS = "EXPRESS"		# Экспресс


class SellingProgramStatusType(Enum):
	FINE = "FINE"		# доступно
	REJECT = "REJECT"		# недоступно


class OfferType(Enum):
	DEFAULT = "DEFAULT"		# товары, для которых вы передавали особый тип ранее и хотите убрать его
	MEDICINE = "MEDICINE"		# лекарства
	BOOK = "BOOK"		# бумажные и электронные книги
	AUDIOBOOK = "AUDIOBOOK"		# аудиокниги
	ARTIST_TITLE = "ARTIST_TITLE"		# музыкальная и видеопродукция
	ON_DEMAND = "ON_DEMAND"		# товары на заказ
	ALCOHOL = "ALCOHOL"		# алкоголь
