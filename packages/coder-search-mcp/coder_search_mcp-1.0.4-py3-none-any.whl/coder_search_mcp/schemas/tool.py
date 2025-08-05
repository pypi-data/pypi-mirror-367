from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class Library(BaseModel):
    name: str = Field(description="Library name")
    version: Optional[str] = Field(None, description="Library version")

class ValidateCodeSnippetRequest(BaseModel):
    """Request schema for validate_code_snippet tool."""
    code_snippet: str = Field(description="The generated code snippet")
    libraries: List[Library] = Field(description="List of libraries used in the code snippet")


class ValidateCodeSnippetResponse(BaseModel):
    """Response schema for validate_code_snippet tool."""
    instructions: str = Field(description="Instructions to follow after the tool use")


class ResolveLibraryVersionRequest(BaseModel):
    """Request schema for resolve_library_version tool."""
    libraries: List[Library] = Field(description="List of libraries to resolve"),
    language: str = Field(description="Language of the library")
    

class ResolveLibraryVersionResponse(BaseModel):
    """Response schema for resolve_library_version tool."""
    libraries: List[Library] = Field(description="List of resolved libraries")
    instructions: str = Field(description="Instructions to follow after the tool use")