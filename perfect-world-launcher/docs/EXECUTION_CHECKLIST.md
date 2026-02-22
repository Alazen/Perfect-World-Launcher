# Motion Update Execution Checklist

Use this checklist to systematically implement the Material 3 motion guidelines across the Perfect World Launcher UI.

## Phase 1: Foundation (CSS Variables)
- [ ] Open `src/styles.css`.
- [ ] Add M3 Easing tokens to `:root`:
  - [ ] `--md-sys-motion-easing-standard: cubic-bezier(0.2, 0.0, 0, 1.0);`
  - [ ] `--md-sys-motion-easing-standard-accelerate: cubic-bezier(0.3, 0.0, 1, 1.0);`
  - [ ] `--md-sys-motion-easing-standard-decelerate: cubic-bezier(0.0, 0.0, 0, 1.0);`
  - [ ] `--md-sys-motion-easing-emphasized: cubic-bezier(0.2, 0.0, 0, 1.0);`
  - [ ] `--md-sys-motion-easing-emphasized-accelerate: cubic-bezier(0.3, 0.0, 0.8, 0.15);`
  - [ ] `--md-sys-motion-easing-emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1.0);`
- [ ] Add M3 Duration tokens to `:root`:
  - [ ] Short durations: `--md-sys-motion-duration-short1` to `short4` (50ms - 200ms).
  - [ ] Medium durations: `--md-sys-motion-duration-medium1` to `medium4` (250ms - 400ms).
  - [ ] Long durations: `--md-sys-motion-duration-long1` to `long2` (450ms - 500ms).

## Phase 2: Global Interactive Elements
- [ ] **Buttons (`button`, `.btn-primary`, `.btn-success`, `.btn-danger`)**:
  - [ ] Replace `transition: all 0.2s ease;` with explicit transitions for `background-color`, `border-color`, `transform`, and `box-shadow` using `--md-sys-motion-duration-short3` and `--md-sys-motion-easing-standard`.
  - [ ] Update `button:active` to use `transform: scale(0.96);` and duration `short2`. Remove standard `translateY(1px)`.
- [ ] **Text Inputs (`input[type="text"]`, `password`, `number`)**:
  - [ ] Transition `border-color`, `box-shadow`, and `background-color` on `:focus` using `medium1` and standard decelerate.
- [ ] **Checkboxes (`.run-checkbox`)**:
  - [ ] Apply hover transition (color shifts).
  - [ ] Apply `:active` effect (`transform: scale(0.9)`).
  - [ ] Animate the checkmark `::after` pseudo-element with a scale-in effect when `:checked`.

## Phase 3: Layout & Component Motion
- [ ] **Server Cards (`.server-card`)**:
  - [ ] Add hover elevation (`transform: translateY(-2px)`) and increase drop shadow.
  - [ ] Provide smooth standard easing (`medium1`) for the hover transition.
- [ ] **Expand/Collapse Containers (`.expand-container`, `.server-header`)**:
  - [ ] Update the `grid-template-rows` transition to use `--md-sys-motion-easing-emphasized` and duration `medium4`.
  - [ ] Ensure nested `.server-header` `margin-bottom` property also matches this exact motion timing for perfect synchronization.
- [ ] **Log Panel (`.log-panel`)**:
  - [ ] Modify the `.log-panel` entrance transition (when gaining the `.visible` class) to use `--md-sys-motion-easing-emphasized-decelerate` with duration `long2`.
  - [ ] Add a specific exit transition (missing `.visible` class) using `--md-sys-motion-easing-emphasized-accelerate` with duration `medium1`. This ensures it leaves faster than it enters.

## Phase 4: Review and Polish
- [ ] Run `npm run dev` to start the application UI locally.
- [ ] Manually test clicking the +/- delay adjuster.
- [ ] Manually test clicking "Add Server" and expanding/collapsing servers.
- [ ] Manually test clicking the checkmarks and typing in the inputs.
- [ ] Verify that no motion feels artificially slow or "floaty".
- [ ] Confirm that *every* clickable component triggers some visual transform upon mousedown (`:active`).
