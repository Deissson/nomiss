## 2025-05-14 - [Empty States and Keyboard Accessibility]
**Learning:** Adding an empty state to a dashboard significantly improves the onboarding experience for new users by providing immediate feedback and instructions. Keyboard support (e.g., "Enter" to submit) in forms is a low-effort, high-impact accessibility and UX win.
**Action:** Always check for empty states in dashboards and ensure all form inputs support intuitive keyboard interactions.
## 2024-05-20 - [Safe Event Handler Interpolation]
**Learning:** When interpolating JavaScript variables into inline HTML event attributes (like onclick), use JSON.stringify() and escape double quotes as &quot; to prevent XSS vulnerabilities and ensure the attribute remains valid for all characters.
**Action:** Always wrap dynamic string values in JSON.stringify(val).replace(/"/g, '&quot;') when injecting into inline event handlers.
