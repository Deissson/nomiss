# Bolt's Journal - NoMiss Performance Optimizations

## 2025-05-04 - Initial Assessment and Strategy
**Learning:** The application uses a FastAPI backend with synchronous file I/O and synchronous Anthropic API calls. The frontend performs multiple `innerHTML` updates in a loop, which is inefficient for DOM rendering.
**Action:** Transition backend to async/await, use a global `AsyncAnthropic` client for connection pooling, and batch DOM updates in the frontend to reduce reflows.

## 2025-05-04 - Backend Async Pitfalls
**Learning:** Converting FastAPI endpoints to `async def` when they perform blocking synchronous I/O (like `json.load/dump`) can starve the event loop. Also, globalizing the AI client must preserve the ability to use request-specific API keys if the architecture supports it.
**Action:** Revert backend async changes for synchronous I/O paths. Focus on the frontend DOM optimization as a safe, measurable win.
