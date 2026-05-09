# Palette UX/Accessibility Learnings

## 2025-05-09 - [Dynamic State for Action Buttons]
**Learning:** Buttons for state-dependent actions (like 'Undo') should be dynamically disabled when the action is unavailable. This prevents user confusion and provides clear visual feedback. Combining `disabled` attribute with visual muting (e.g., `opacity-30`) and a descriptive `title` improves both usability and accessibility.
**Action:** Always implement dynamic `disabled` states and visual feedback for buttons whose actions depend on the current application state.
