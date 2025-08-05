import httpx
from coder_search_mcp.schemas.tool import (
    ValidateCodeSnippetRequest,
    ValidateCodeSnippetResponse,
    ResolveLibraryVersionRequest,
    ResolveLibraryVersionResponse
)

# Convenience functions for direct usage
async def validate_versions_in_code_snippet(
    base_url: str,
    request: ValidateCodeSnippetRequest,
    timeout: float = 30.0
) -> ValidateCodeSnippetResponse:
    """
    Convenience function to validate a code snippet.
    
    Args:
        base_url: Base URL for the tool service
        request: Validation request
        timeout: Request timeout in seconds
        
    Returns:
        ValidateCodeSnippetResponse with validation instructions
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        url = f"{base_url.rstrip('/')}/validate_code_snippet"
        response = await client.post(
            url,
            json=request.model_dump(),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return ValidateCodeSnippetResponse(**response.json())


async def resolve_library_version(
    base_url: str,
    request: ResolveLibraryVersionRequest,
    timeout: float = 30.0
) -> ResolveLibraryVersionResponse:
    """
    Convenience function to resolve library versions.
    
    Args:
        base_url: Base URL for the tool service
        request: Resolution request
        timeout: Request timeout in seconds
        
    Returns:
        ResolveLibraryVersionResponse with resolved libraries and instructions
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        url = f"{base_url.rstrip('/')}/resolve_library_version"
        response = await client.post(
            url,
            json=request.model_dump(),
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return ResolveLibraryVersionResponse(**response.json())
