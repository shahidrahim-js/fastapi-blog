from pydantic import BaseModel, ConfigDict, Field

# Base schema containing the fields shared by Post create and response schemas.
# Fields are a required field that is without a default value. 
class PostBase(BaseModel):
  title: str = Field(min_length=1, max_length=100)
  content: str = Field(min_length=1)
  author: str = Field(min_length=1, max_length=50)

# Post create schema, that inherits the fields and validation rule from PostBase.
class PostCreate(PostBase):
  pass

# Post response schema. Inherits the fields and validation rule from PostBase.
# from_attributes=True enable Pydantic to accsess object attributes using dot notation (for example: post.title).
class PostResponse(PostBase):
  model_config = ConfigDict(from_attributes=True)

  id: int
  created_at: str #[TO-DO: replace str type with date/time type when integrating the schema with datbase.]