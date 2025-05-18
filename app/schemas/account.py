from pydantic import BaseModel

class AccountBase(BaseModel):
	"""
	Base account schema with common attributes.
	"""

	name: str

class AccountCreate(AccountBase):
	"""
	Schema for creating an account under an organization.

	Parameters
	-----
	name : str
		Account name
	description : str, optional
		Account description
	"""

	name: str
	description: str | None = None

class AccountRead(AccountBase):
	"""
	Schema for reading account data.

	Parameters
	-----
	id : str
		Account unique identifier
	name : str
		Account name
	description : str, optional
		Account description
	organization_id : str
		ID of the organization the account belongs to
	"""
	
	id: str
	name: str
	description: str | None = None
	organization_id: str

class AccountUpdate(AccountBase):
	"""
	Schema for updating account. Only account description could be updated.
	
	Parameters
	-----
	description : str, optional
		Account description
	"""

	description: str | None = None
