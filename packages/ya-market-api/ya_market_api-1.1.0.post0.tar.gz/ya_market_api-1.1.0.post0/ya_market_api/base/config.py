from typing import Optional, Generic, TypeVar


T = TypeVar("T")


class Config(Generic[T]):
	__slots__ = "session", "business_id", "base_url"

	session: T
	business_id: Optional[int]
	base_url: str

	def __init__(self, session: T, business_id: Optional[int], base_url: str) -> None:
		self.session = session
		self.business_id = business_id
		self.base_url = base_url
