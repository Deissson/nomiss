## 2025-05-14 - [Empty States and Keyboard Accessibility]
**Learning:** Adding an empty state to a dashboard significantly improves the onboarding experience for new users by providing immediate feedback and instructions. Keyboard support (e.g., "Enter" to submit) in forms is a low-effort, high-impact accessibility and UX win.
**Action:** Always check for empty states in dashboards and ensure all form inputs support intuitive keyboard interactions.

## 2025-05-15 - [State-Dependent UI Feedback]
**Learning:** For actions that are only valid in certain states (like "Undo"), disabling the button with clear visual feedback (`opacity-30`) and semantic attributes (`disabled`, `cursor-not-allowed`) prevents user frustration and invalid state transitions.
**Action:** Identify state-dependent actions and implement proper disabled states using Tailwind modifiers.
