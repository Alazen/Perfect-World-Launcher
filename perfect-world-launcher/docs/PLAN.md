# Perfect World Launcher - Motion Update Plan (Material Design 3)

## 1. Overview
The current Perfect World Launcher implements basic CSS transitions (e.g., `transition: all 0.2s ease` and simple `translateY(1px)` on active states). While functional, this lacks the expressiveness, weight, and polish expected of modern applications. 

This document outlines a comprehensive plan to upgrade the application's animations to align with **Material Design 3 (M3) Motion Principles**. By applying M3's easing curves, durations, and interactive choreographies, the launcher will feel highly responsive, fluid, and premium.

## 2. Material 3 Motion Principles Applied

Material Design 3 defines motion through carefully tuned easing curves and durations:

### 2.1 Easing Tokens
We will introduce global CSS variables for M3 easing curves to ensure consistency:
*   `--md-sys-motion-easing-linear: cubic-bezier(0, 0, 1, 1);`
*   `--md-sys-motion-easing-standard: cubic-bezier(0.2, 0.0, 0, 1.0);` (Default for general UI changes)
*   `--md-sys-motion-easing-standard-accelerate: cubic-bezier(0.3, 0.0, 1, 1.0);` (Elements exiting the screen)
*   `--md-sys-motion-easing-standard-decelerate: cubic-bezier(0.0, 0.0, 0, 1.0);` (Elements entering the screen)
*   `--md-sys-motion-easing-emphasized: cubic-bezier(0.2, 0.0, 0, 1.0);` (For prominent elements expanding/collapsing)
*   `--md-sys-motion-easing-emphasized-accelerate: cubic-bezier(0.3, 0.0, 0.8, 0.15);`
*   `--md-sys-motion-easing-emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1.0);`

### 2.2 Duration Tokens
*   `--md-sys-motion-duration-short1: 50ms;` (Micro-interactions, active states)
*   `--md-sys-motion-duration-short2: 100ms;`
*   `--md-sys-motion-duration-short3: 150ms;` (Hover states)
*   `--md-sys-motion-duration-short4: 200ms;`
*   `--md-sys-motion-duration-medium1: 250ms;`
*   `--md-sys-motion-duration-medium2: 300ms;` (Color fades, small expansions)
*   `--md-sys-motion-duration-medium3: 350ms;`
*   `--md-sys-motion-duration-medium4: 400ms;` (Large expansions like Server Cards)
*   `--md-sys-motion-duration-long1: 450ms;`
*   `--md-sys-motion-duration-long2: 500ms;` (Log panel entering)

## 3. Element-Specific Motion Strategies

Every interactive and clickable element must react instantaneously to user input with a state change (Hover, Focus, Pressed/Active).

### 3.1 Buttons (`button`, `.btn-primary`, `.btn-success`, etc.)
*   **Hover State**: Smoothly transition background color and border over `150ms (Short3)` using `--md-sys-motion-easing-standard`.
*   **Pressed/Active State**: Instead of just shifting down (`translateY(1px)`), the button should scale down to visually indicate compression. 
    *   `transform: scale(0.96);`
    *   Duration: `100ms (Short2)`
    *   Easing: `--md-sys-motion-easing-standard`
*   **Ripple Effect (Optional but Recommended)**: Consider adding a radial background highlight that follows the cursor, or relying on high-quality scaling + color shifting if an exact ripple is too costly.

### 3.2 Server Cards (`.server-card`)
*   **Hover State**: Elevate the card slightly.
    *   `transform: translateY(-2px);`
    *   Update `box-shadow` to a more prominent glowing drop-shadow.
    *   Duration: `250ms (Medium1)` using Standard Easing.
*   **Expand/Collapse (`.expand-container`, `.expand-content`)**:
    *   Current: `0.35s cubic-bezier(0.4, 0, 0.2, 1)`
    *   **M3 Upgrade**: Use Emphasized Easing (`--md-sys-motion-easing-emphasized`). Duration: `400ms (Medium4)`. The container expansion must feel weighty and smooth, smoothly guiding the user's eye.

### 3.3 Inputs & Text Fields (`input[type="text"]`, `input[type="password"]`, `input[type="number"]`)
*   **Hover**: Fade in border color `150ms (Short3)` Standard.
*   **Focus**: Expand a faint focus ring (box-shadow) outward.
    *   Duration: `250ms (Medium1)`
    *   Easing: `--md-sys-motion-easing-standard-decelerate` (Snappy entry).

### 3.4 Checkboxes (`.run-checkbox`)
*   **Hover State**: Gentle background color shift.
*   **Pressed State**: Quick scale down (`transform: scale(0.9);`) `100ms (Short2)`.
*   **Checked Transition**: When checked, the checkmark (`✔`) should animate in via a scale and opacity fade.
    *   `transform: scale(0) -> scale(1); opacity: 0 -> 1;`
    *   Duration: `200ms (Short4)` Emphasized Decelerate.

### 3.5 Log Panel (`.log-panel`)
*   **Entrance (Slide Up)**: 
    *   Current: `transform: translateY(150%); transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1)`
    *   **M3 Upgrade**: Use Emphasized Decelerate (`--md-sys-motion-easing-emphasized-decelerate`) with a `500ms (Long2)` duration to make it slide in with a strong initial burst of speed that gracefully slows to a halt.
*   **Exit (Slide Down)**:
    *   Use Emphasized Accelerate (`--md-sys-motion-easing-emphasized-accelerate`) with shorter duration `250ms (Medium1)` to quickly dismiss it.

## 4. Implementation Steps
1.  **Define CSS Motion Variables**: Add all foundational M3 easing and duration variables to the `:root` pseudo-class in `styles.css`.
2.  **Refactor Global Transitions**: Remove blanket `transition: all` declarations (which are bad for performance) and replace them with specific property transitions (e.g., `transition: background-color var(--duration) var(--easing), transform ...`).
3.  **Apply Clickable Micro-interactions**: Target `button:active`, `.run-checkbox:active`, and other clickable elements with the new scaling logic.
4.  **Refine Accordions & Panels**: Update `.expand-container` and `.log-panel` to use Emphasized easing curves for better spatial logic.
5.  **Review & Polish**: Test the application sequentially, clicking every interactive element to ensure no jarring jumps or overly sluggish transitions exist. 
