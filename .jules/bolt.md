## 2025-05-15 - [Efficient DOM Updates and Formatting]
**Learning:** Using `innerHTML +=` in a loop or on a large container (like chat history) is a major performance bottleneck because it forces the browser to re-parse and re-render the entire subtree every time.
**Action:** Always batch DOM updates by building a single HTML string or use `insertAdjacentHTML` for appending to existing lists. For repeated date formatting, use a persistent `Intl.DateTimeFormat` instance.

## 2025-05-16 - [Reducing Network Round-Trips via Mutation Response]
**Learning:** Returning the full updated state directly from POST/DELETE mutation endpoints instead of a simple success message allows the frontend to update the UI immediately. This eliminates the need for a follow-up GET request, saving one network round-trip per user action.
**Action:** Design backend mutation APIs to return the new application state when the payload size is manageable, reducing overall application latency.
