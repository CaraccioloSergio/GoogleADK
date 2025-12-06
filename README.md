# GoogleADK — Labbi Catalog Test Agent

Small utility repo that provides a tiny ADK-based agent for querying
the Labbi catalogue (UAT/dev) via HTTP. The project contains two helper
functions for calling Labbi APIs and an `Agent` instance ready to be
used by other code.

**Repository layout**
- `requirements.txt`: Python dependencies.
- `multi_tool_agent/__init__.py`: package export for the agent.
- `multi_tool_agent/agent.py`: implementation of the HTTP helpers and
  the `root_agent` `Agent` instance.

**Requirements**
- Python 3.11+ (uses `zoneinfo` & type union `X | Y`).
- Install dependencies:

```powershell
pip install -r requirements.txt
```

Dependencies from `requirements.txt`:
- `google-adk`
- `google-genai`
- `requests`
- `python-dotenv`

Usage
-----

Basic import and usage from Python:

```python
from multi_tool_agent.agent import labbi_search_catalog, test_api_labbi, root_agent

# Call the catalog search helper
res = labbi_search_catalog(query='aspirina', page=0, size=10)
print(res)

# Call the test API for drugstores by CUIT
res2 = test_api_labbi('20304050607')
print(res2)

# `root_agent` is an `Agent` instance preconfigured to use
# the `labbi_search_catalog` tool.
print(root_agent.name, root_agent.model)
```

Notes
-----
- `labbi_search_catalog` contains an `auth_token` parameter with a
  default placeholder token inside the function. For production use,
  you should remove hard-coded tokens and load them from environment
  variables or a secrets manager (for example, using `python-dotenv`).
- The HTTP helpers use the standard library `http.client` and return
  structured `dict` objects with `status` keys for ADK-style tooling.
- Endpoints in the code reference `uat.api.labbi.com.ar` and
  `dev.api.labbi.com.ar` — confirm the correct hostnames before use.

Contributing
------------
- Open a PR if you want to add tests, CI, or expand the agent tools.

License
-------
No license specified. Add a `LICENSE` file if you want to make this
project open-source.
