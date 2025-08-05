from mcp.server.fastmcp import FastMCP
from coder_search_mcp.schemas.tool import (
    ValidateCodeSnippetRequest,
    ValidateCodeSnippetResponse,
    ResolveLibraryVersionRequest,
    ResolveLibraryVersionResponse,
)
from coder_search_mcp.utils.tool import resolve_library_version, validate_versions_in_code_snippet


mcp = FastMCP("CoderSearch")

VERSION = "1.0.0"
BACKEND_BASE_URL = "https://coder-search-backend.onrender.com"

@mcp.tool()
async def get_actual_library_versions(request: ResolveLibraryVersionRequest) -> ResolveLibraryVersionResponse:
    """Use this tool before generating code that relies on additional packages, libraries, or SDKs to determine which versions to use. Inspect the current project files (e.g., requirements.txt, pyproject.toml, etc.) to extract versions for any packages already in use. Submit a list of packages you plan to use along with their versions. If a package is already included in the project dependencies, provide the existing version; if it's a new package, leave the version empty or set it to null. The tool will verify and complete the version information for each package. You will also receive specific instructions that you are expected to follow when generating code.
    
    Expected input data:
    - libraries: List of Library objects with name and version fields
    - language: Programming language (e.g., 'python', 'javascript', 'java')
    """
    return await resolve_library_version(BACKEND_BASE_URL, request)

@mcp.tool()
async def validate_code_snippet(request: ValidateCodeSnippetRequest) -> ValidateCodeSnippetResponse:
    """Use this tool after generating code that relies on additional packages, libraries, or SDKs to validate whether symbols, methods and properties used are correct. Submit a list of packages you have used along with their versions. The tool will verify and complete the version information for each package. You will also receive specific instructions that you are expected to follow after using this tool.
    
    Expected input data:
    - code_snippet: String containing the generated code to validate
    - libraries: List of Library objects with name and version fields used in the code
    """
    return await validate_versions_in_code_snippet(BACKEND_BASE_URL, request)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()