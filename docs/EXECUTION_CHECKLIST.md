# Execution Checklist

This checklist breaks down the execution of the UI Redesign Plan to precisely match the target design. Check off items as they are successfully implemented and verified.

## Phase 1: Preparation
- [ ] Read through `docs/PLAN.md` to internalize the target aesthetics.
- [ ] Start the development server (`npm run dev` in `perfect-world-launcher/`) and keep it running for live UI reloading.
- [ ] Inspect the `index.html`, `src/main.ts`, and `src/styles.css` structure.

## Phase 2: Core CSS Palette and Shapes (`styles.css`)
- [ ] **Colors**: Update `:root` variables to the new dark charcoal theme:
  - `--bg-app`: `#18181A` (approx)
  - `--bg-card`: `#212429` (approx)
  - `--bg-input`: `#2A2D35` (approx)
  - `--bg-input-hover`: `#333742` (approx)
  - `--btn-primary`: `#3BDFE4` (Bright Cyan/Blue)
  - `--text-primary`: `#FFFFFF`
  - `--text-muted`: `#A0A5B1`
- [ ] **Global Overrides**: Update `body` to remove gradients and set the solid charcoal background.
- [ ] **Shapes & Controls**:
  - Update `button` rules: `border-radius: 9999px`, specific paddings (e.g. `8px 24px`), remove legacy gradients.
  - Update `input` rules: `border-radius: 9999px`, specific height and font rules.
- [ ] **Cards**: Update `.server-card`: `border-radius: 24px`, background color, solid/subtle border.
- [ ] **Checkboxes**: Overhaul `.run-checkbox`. Implement a large rounded cyan styling with a centered tick (`✔`) when checked.

## Phase 3: Structural Layout Refactoring (`main.ts`)
- [ ] **State**: Add `let expandedServers: Set<number> = new Set();` to `main.ts` to track visibility state per server-card. By default, add the first server to the set (or start all collapsed).
- [ ] **Header (Top Row)**: 
  - Refactor `appEl.innerHTML` header portion.
  - Add pill buttons: `Import Settings`, `Export Settings`.
  - Format the `Delay (s): X` segment. Change from `<input type="number">` to text `5` enclosed by `-` and `+` circular buttons.
- [ ] **Server Listing Logic**:
  - In `render()`, modify the loop mapping `currentState.servers` to HTML.
  - Apply an IF condition: `if (expandedServers.has(serverIdx)) { // Expanded card string } else { // Collapsed card string }`.
  - **Collapsed Template**: Row containing: `Show` (Button) -> `Server Name` (Input) -> `Play Server Name` (Cyan Button) -> `Remove Server Name` (Button).
  - **Expanded Template**: Row containing `Hide` -> `Server Name` -> `Play Server Name` -> `Remove`. Below it, the `Client Path:` label, input, and `Browse`. Below that, the accounts grid. Below that, the `Add Account` button.
- [ ] **Accounts Grid Layout**:
  - Adjust column templates in `styles.css` `.accounts-grid` to match: Run (Check), Play (cyan button), Login, Password, Character, Remove (button).
  - Ensure labels perfectly align with the target image. Remove backgrounds from header cells.
- [ ] **Footer (Bottom Row)**:
  - Refactor the footer element. Ensure buttons are placed sequentially: `Start X accounts` (Massive, Cyan, Left-aligned), `Add Server`, `Save and Close`, `Show Log`. Center the minor buttons or space them as shown in the screenshot.
  - Position the log textual output (`[HH:MM:SS] ...`) at the very bottom-left of the window, outside or underneath the footer buttons.

## Phase 4: Event Bindings (`main.ts`)
- [ ] **Delay +/- Actions**: Add click event listeners to increment/decrease delay, then `requestSave()` and `render()`.
- [ ] **Show/Hide Triggers**: Add click event listeners to `.btn-show-srv` / `.btn-hide-srv`. On click: `expandedServers.add(idx)` or `expandedServers.delete(idx)`, then `render()`.
- [ ] **Save and Close**: Add click event listener to `.btn-save-close`. Await `invoke("save_config")` followed by `window.close()` or `appWindow.close()`.
- [ ] Re-bind existing inputs (server-name, client-path, acc-login, acc-pass, acc-char) to the new DOM structure.
- [ ] Re-bind play and remove buttons.
- [x] **Import/Export Settings**: Connect `#btn-import` and `#btn-export` to Tauri's dialog APIs and new Rust backend commands `import_settings_from_file` and `export_settings_to_file` to allow loading/saving configuration to custom files.

## Phase 5: Deep Polish & Review
- [ ] Review Paddings / Margins side-by-side with the reference screenshot.
- [ ] Check hovering states (slight brighten on button hover, bright cyan border focus on inputs).
- [ ] Ensure the log text renders properly at the bottom left without an intrusive overlapping panel (unlike the old design).
- [ ] Verify functionality (add account, add server, play, browse path) still works identically.
