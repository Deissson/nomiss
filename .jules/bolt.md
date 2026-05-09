## 2025-05-15 - [Efficient DOM Updates and Formatting]
**Learning:** Using `innerHTML +=` in a loop or on a large container (like chat history) is a major performance bottleneck because it forces the browser to re-parse and re-render the entire subtree every time.
**Action:** Always batch DOM updates by building a single HTML string or use `insertAdjacentHTML` for appending to existing lists. For repeated date formatting, use a persistent `Intl.DateTimeFormat` instance.

## 2026-05-09 - [Eliminating Redundant Network Requests]
**Learning:** Returning the full updated state directly from mutation endpoints (POST/DELETE) eliminates the need for a subsequent GET request to synchronize the frontend, providing a noticeable performance boost in high-latency environments.
**Action:** Implement "immediate sync" by returning the updated data list from all backend mutations and updating the frontend to utilize this data directly. Add input validation (e.g., `Array.isArray()`) on the frontend to handle potential error responses from these endpoints gracefully.
