from pydantic import BaseModel as SCBaseModel

class TokenResponseSchema(SCBaseModel):
    access_token: str
    token_type: str