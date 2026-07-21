# URL Patterns for Fetching MCP Source Code

## GitHub Repositories

### Converting GitHub URLs to Raw Content URLs

**Repository URL**: `https://github.com/{owner}/{repo}`
**Branch/Tree URL**: `https://github.com/{owner}/{repo}/tree/{branch}`
**File URL**: `https://github.com/{owner}/{repo}/blob/{branch}/{path}`

**Raw Content URL Pattern**:
```
https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}
```

### Example Conversions

| User Provides | Fetch URL |
|--------------|-----------|
| `https://github.com/user/mcp-server` | `https://raw.githubusercontent.com/user/mcp-server/main/README.md` |
| `https://github.com/user/mcp-server/tree/main` | `https://raw.githubusercontent.com/user/mcp-server/main/README.md` |
| `https://github.com/user/mcp-server/blob/main/src/index.ts` | `https://raw.githubusercontent.com/user/mcp-server/main/src/index.ts` |

### Common Branch Names to Try
1. `main`
2. `master`
3. `develop`

## Files to Fetch (In Order)

### Step 1: Documentation & Metadata
1. `README.md` or `readme.md` - Main documentation
2. `LICENSE` or `LICENSE.md` or `LICENSE.txt` - License file
3. `package.json` (Node.js) or `pyproject.toml` (Python) - Dependencies
4. `SECURITY.md` - Security policy (if exists)

### Step 2: Entry Points (based on package.json/pyproject.toml)
**For TypeScript/Node.js MCP**:
- Check `main` field in package.json
- Common: `src/index.ts`, `index.ts`, `src/server.ts`

**For Python MCP**:
- Check `[project.scripts]` in pyproject.toml
- Common: `src/__init__.py`, `server.py`, `main.py`

### Step 3: Tool Definitions
Look for files containing tool registrations:
- `@server.tool()` decorators (Python FastMCP)
- `server.registerTool()` calls (TypeScript)
- Files named: `tools.ts`, `tools.py`, `handlers.ts`, `handlers.py`

### Step 4: Configuration
- `.env.example` - Environment variables needed
- `config.ts`, `config.py`, `settings.py` - Configuration patterns
- `docker-compose.yml` - Container setup

## npm Packages

### Finding Source Repository
1. npm page: `https://www.npmjs.com/package/{package-name}`
2. Look for "Repository" link which points to GitHub
3. Use GitHub patterns above

### Direct npm Registry API
```
https://registry.npmjs.org/{package-name}
```
Returns JSON with `repository` field containing source URL.

## PyPI Packages

### Finding Source Repository
1. PyPI page: `https://pypi.org/project/{package-name}`
2. Look for "Homepage" or "Source" link
3. Use GitHub patterns above

## URL Extraction Strategy

Given a user-provided URL:

1. **If GitHub repo URL**: Extract owner/repo, try fetching README from main branch
2. **If GitHub file URL**: Extract the raw URL directly
3. **If npm URL**: Fetch registry API to get repository URL
4. **If PyPI URL**: Fetch project page, extract repository link
5. **If raw content URL**: Use directly

## Example Fetch Sequence

For `https://github.com/example/my-mcp-server`:

```
1. https://raw.githubusercontent.com/example/my-mcp-server/main/README.md
2. https://raw.githubusercontent.com/example/my-mcp-server/main/LICENSE
3. https://raw.githubusercontent.com/example/my-mcp-server/main/package.json
4. (parse package.json to find entry point)
5. https://raw.githubusercontent.com/example/my-mcp-server/main/src/index.ts
```

## Error Handling

| Error | Likely Cause | Try Instead |
|-------|--------------|-------------|
| 404 on README.md | Wrong branch or no README | Try `readme.md` or `master` branch |
| 404 on main branch | Repo uses master | Try `master` branch |
| 404 on index.ts | Different entry point | Check package.json main field |
| Rate limited | Too many requests | Wait and retry, or inform user |

## Private Repositories

If GitHub returns 404 but the repo exists:
- Repository may be private
- Inform user: "This repository appears to be private. I can't access its source code for review."
