## 2025-05-14 - Dynamic Action Availability Feedback
**Learning:** In a dashboard with state-dependent actions like 'Undo', users can be confused if a button is clickable but has no effect. Providing clear visual (opacity, cursor) and functional (disabled attribute) feedback prevents unnecessary interaction and improves clarity.
**Action:** Always check if an action has a prerequisite state (e.g., `skipped > 0`) and reflect that availability in the UI.
