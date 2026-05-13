## 2025-05-14 - [Empty States and Keyboard Accessibility]
**Learning:** Adding an empty state to a dashboard significantly improves the onboarding experience for new users by providing immediate feedback and instructions. Keyboard support (e.g., "Enter" to submit) in forms is a low-effort, high-impact accessibility and UX win.
**Action:** Always check for empty states in dashboards and ensure all form inputs support intuitive keyboard interactions.

## 2025-05-15 - [Accessible Progress Bars and Loading States]
**Learning:** Using `aria-valuetext` on progress bars provides essential context for screen reader users by translating percentages into human-readable status (e.g., "60% of limit used"). Implementing loading states on submit buttons while refocusing the input field significantly improves the flow for repetitive data entry tasks.
**Action:** Always include `aria-valuetext` on progress bars and provide immediate button feedback with focus management in forms.
