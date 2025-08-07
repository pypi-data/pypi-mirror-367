# FastMCP Development Guidelines

## Git

This project uses `pre-commit` to run checks on all commits. If your commit doesn't pass the checks, it will not be created. Do not attempt to amend commits to pass checks.

## Documentation

- Documentation uses the Mintlify framework
- Files must be present in docs.json to be included in the documentation

## Testing and Investigation

### In-Memory Transport - Always Preferred

When testing or investigating FastMCP servers, **always prefer the in-memory transport** unless you specifically need HTTP transport features. Pass a FastMCP server directly to a Client to eliminate separate processes and network complexity.

```python
# Create your FastMCP server
mcp = FastMCP("TestServer")

@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

# Pass server directly to client - uses in-memory transport
async with Client(mcp) as client:
    result = await client.call_tool("greet", {"name": "World"})
```

### When to Use HTTP Transport

Only use HTTP transport when testing network-specific features. Prefer StreamableHttp over SSE as it's the modern approach.

```python
# Only when network testing is required
async with Client(transport=StreamableHttpTransport(server_url)) as client:
    result = await client.ping()
```

## Development Workflow

- You must always run pre-commit if you open a PR, because it is run as part of a required check.
- When opening PRs, apply labels appropriately for bugs/breaking changes/enhancements/features. Generally, improvements are enhancements (not features) unless told otherwise.
- NEVER modify files in docs/python-sdk/**, as they are auto-generated.
- Use # type: ignore[attr-defined] in unit tests when accessing an MCP result of indeterminate type instead of asserting its type
