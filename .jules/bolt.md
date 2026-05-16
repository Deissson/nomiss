## 2025-05-15 - [Efficient DOM Updates and Formatting]
**Learning:** Using `innerHTML +=` in a loop or on a large container (like chat history) is a major performance bottleneck because it forces the browser to re-parse and re-render the entire subtree every time.
**Action:** Always batch DOM updates by building a single HTML string or use `insertAdjacentHTML` for appending to existing lists. For repeated date formatting, use a persistent `Intl.DateTimeFormat` instance.

## 2026-05-06 - [Reducing Network Round-trips]
**Learning:** Mutation endpoints that return only a success message force the frontend to make a second GET request to refresh the state.
**Action:** Return the updated state directly from POST/PUT/DELETE endpoints to allow the frontend to update the UI in a single round-trip.

## 2025-05-16 - Modular Stack Migration (FastAPI + React/TS)
**Learning:** Transitioning from a single-file monolith to a modular structure significantly improves maintainability. Using TypeScript (verbatimModuleSyntax: true) requires careful handling of type-only imports and configuration of tsconfig.json (Bundler resolution, vite-env.d.ts) to avoid build errors.
**Action:** Always ensure `vite-env.d.ts` is present when using TypeScript with Vite to resolve asset imports like CSS. Use modular routing in FastAPI (`APIRouter`) for clean backend separation.
