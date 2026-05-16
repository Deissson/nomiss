## 2025-05-15 - [Efficient DOM Updates and Formatting]
**Learning:** Using `innerHTML +=` in a loop or on a large container (like chat history) is a major performance bottleneck because it forces the browser to re-parse and re-render the entire subtree every time.
**Action:** Always batch DOM updates by building a single HTML string or use `insertAdjacentHTML` for appending to existing lists. For repeated date formatting, use a persistent `Intl.DateTimeFormat` instance.

## 2026-05-06 - [Reducing Network Round-trips]
**Learning:** Mutation endpoints that return only a success message force the frontend to make a second GET request to refresh the state.
**Action:** Return the updated state directly from POST/PUT/DELETE endpoints to allow the frontend to update the UI in a single round-trip.

## 2026-05-16 - [Anthropic Client Reuse and Connection Pooling]
**Learning:** Instantiating the `anthropic.Anthropic` client on every request adds measurable latency (~32ms per call in this environment) and, more importantly, prevents HTTP connection reuse (TCP/TLS handshakes).
**Action:** Always initialize the API client globally at the module level in FastAPI to benefit from connection pooling and eliminate redundant initialization overhead.
