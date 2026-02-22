# Execution Checklist: Rust + Tauri Refactor (Detailed Technical Plan)

This extensive checklist details the granular step-by-step phases necessary to rewrite the Perfect World Launcher into a high-performance, lightweight Rust/Tauri application while strictly maintaining the identical UI, UX, and functionality.

## Phase 1: Environment Readiness & Deep Initialization
- [ ] **System Dependencies Configuration**
  - [ ] Install or update Rust (`rustup update stable`).
  - [ ] Ensure the latest Microsoft Visual C++ Build Tools (MSVC) are correctly installed for Windows native compilation.
  - [ ] Install Node.js (v20+ LTS) and confirm `npm` or `pnpm` is available in PATH.
- [ ] **Tauri Project Scaffolding**
  - [ ] Navigate to the project root and execute the Tauri scaffolding tool: `npm create tauri-app@latest perfect-world-launcher -- --manager npm --template vanilla-ts`.
  - [ ] Choose Vanilla HTML/CSS/TypeScript to avoid shipping heavy frontend frameworks (React/Vue/Angular), achieving the absolute smallest binary footprint.
  - [ ] Clean up scaffolded Boilerplate (remove `greet` commands, example styling, and default TS logic).
- [ ] **Manifest & Metadata Porting (`tauri.conf.json`)**
  - [ ] Map Python project version (`v24.0`) to Tauri's `version` field.
  - [ ] Configure `build.beforeBuildCommand` to `npm run build` and `build.beforeDevCommand` to `npm run dev`.
  - [ ] Set exact Window parameters under `tauri.windows`:
    - [ ] `title`: "Perfect World Launcher"
    - [ ] `width`: 1000, `height`: 750 (match PySide6 dimensions).
    - [ ] `resizable`: true, `fullscreen`: false.
    - [ ] `theme`: "Dark" (enforcing native Win11 title bar styling to match `#0f172a`).
- [ ] **Icon Migration**
  - [ ] Copy `assets/pw_launcher_icon_3.ico` into the Tauri toolchain.
  - [ ] Run `npm run tauri icon path/to/icon.ico` to auto-generate all required sizes (`.ico`, `.png`, `.icns`) inside `src-tauri/icons/`.

## Phase 2: Native Data Architecture & Serialization (Rust)
- [ ] **Cargo Dependencies Setup**
  - [ ] Add `serde = { version = "1.0", features = ["derive"] }` for JSON structured serialization.
  - [ ] Add `serde_json = "1.0"` for file parsing.
  - [ ] Add `directories = "5.0"` for safe cross-platform AppData path resolution.
- [ ] **Data Model Recreations (`src-tauri/src/models.rs`)**
  - [ ] Define the `Account` struct (matching `models/account.py`):
    - [ ] `pub login: String`, `pub password: String`, `pub character: String`, `pub run: bool`.
    - [ ] Ensure all fields have `#[derive(Debug, Clone, Serialize, Deserialize)]`.
  - [ ] Define the `Server` struct (matching `models/server.py`):
    - [ ] `pub name: String`, `pub client_path: String`, `pub accounts: Vec<Account>`.
    - [ ] Define helper method: `pub fn validate_path(&self) -> bool`.
  - [ ] Define the root `Settings` struct:
    - [ ] `pub delay: u64`, `pub servers: Vec<Server>`.
- [ ] **State Management Engine (`src-tauri/src/state.rs`)**
  - [ ] Implement a `Mutex<Settings>` wrapper inside a Tauri `State` struct to allow shared concurrent access across IPC commands without race conditions.

## Phase 3: Storage & File System I/O Operations
- [ ] **Persistence Logic (`src-tauri/src/store.rs`, Refactoring `settings_store.py`)**
  - [ ] Replicate the path resolution fallback logic:
    - [ ] First, attempt to locate or create `settings.json` adjacent to `std::env::current_exe()`.
    - [ ] If the execution directory is Read-Only (e.g., Program Files), query OS for `%APPDATA%\PerfectWorldLauncher\settings.json` using the `directories` crate.
  - [ ] Implement `fn load_settings() -> Result<Settings, String>`:
    - [ ] Use `std::fs::read_to_string` to load bytes.
    - [ ] Use `serde_json::from_str` to populate structures.
    - [ ] If file does not exist, return a default `Settings` struct instantiation.
  - [ ] Implement `fn save_settings(settings: &Settings) -> Result<(), String>`:
    - [ ] Use `serde_json::to_string_pretty` for identical formatting.
    - [ ] Use `std::fs::File::create` and `write_all`.

## Phase 4: Core Execution & Launch Engine (Rust OS Integration)
- [ ] **Process Launch Controller (`src-tauri/src/launcher.rs`, Refactoring `launch.py`)**
  - [ ] Construct argument strings dynamically: `format!("user:{} pwd:{} role:{}", acct.login, acct.password, acct.character)`.
  - [ ] Utilize `std::process::Command::new(&server.client_path)`.
  - [ ] Push arguments: `["startbypatcher", &arg_string]`.
  - [ ] Define the Working Directory using `Command::current_dir(parent_path)` so the `elementclient` binds to its respective data folders natively.
  - [ ] Capture process spawning Result (`Ok(Child)` vs `Err(e)`).
- [ ] **Sequential Delays (Refactoring `delay_stepper.py`)**
  - [ ] During bulk launches, wrap iterations in `std::thread::sleep(std::time::Duration::from_secs(delay))`.
  - [ ] Create an interrupt (`AtomicBool`) allowing users to "Cancel Launch" mid-sequence.
- [ ] **Tauri IPC Command Registrations (`src-tauri/src/main.rs`)**
  - [ ] `#[tauri::command] fn get_config(state: State) -> Settings`
  - [ ] `#[tauri::command] fn save_config(new_config: Settings, state: State) -> Result<(), String>`
  - [ ] `#[tauri::command] async fn launch_all(state: State, app: AppHandle)`
  - [ ] `#[tauri::command] async fn launch_server(server_index: usize, state: State, app: AppHandle)`
  - [ ] `#[tauri::command] async fn launch_account(server_index: usize, account_index: usize, state: State, app: AppHandle)`
  - [ ] Assemble all handlers inside `tauri::Builder::default().invoke_handler(...)`.

## Phase 5: Pixel-Perfect Frontend Styling (Translating `theme.py` -> CSS)
- [ ] **Global Variables Structure (`src/styles.css`)**
  - [ ] Extract all Hex and RGBA values from PySide6 properties into CSS Variables (e.g., `--bg-primary: #020617;`, `--text-highlight: #38bdf8;`).
  - [ ] Setup exact border radiuses (e.g., `--radius-lg: 12px;`, `--radius-md: 8px;`).
- [ ] **Layout Foundations & Typography**
  - [ ] Enforce the exact typography stack: `font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;`.
  - [ ] Replicate the linear gradient application background on the `body` tag natively.
  - [ ] Use `display: flex` and `flex-direction: column` to ensure the header, content area, and footer stick natively to the window bounds.
- [ ] **Micro-Animations & Hover States**
  - [ ] Add `transition: all 0.2s ease` to all interactive buttons.
  - [ ] Convert PySide6 Qt Button hover stylesheets into CSS `:hover` states with scale transforms (`transform: translateY(-1px)`).
  - [ ] Implement smooth scrolling on the main container using `overflow-y: overlay` and custom WebKit scrollbars formatted to match the Python app's sleek translucent scrollbars.

## Phase 6: Web UI Component Translation (HTML/TypeScript)
- [ ] **DOM Structure Mapping**
  - [ ] Write `index.html` referencing `<div id="app"></div>` payload wrapper.
  - [ ] Create TS render methods to generate DOM elements dynamically:
    - [ ] `renderTopControls()`: Import/Export buttons, Delay inputs.
    - [ ] `renderServerList()`: Iterate over State Array natively to render DOM nodes.
    - [ ] `renderServerCard(server)`: Create collapsible `<details>` or styled Flexbox containers holding Client Path binding arrays.
    - [ ] `renderAccountsTable(accounts)`: Rebuild the data grid using CSS Grid or HTML Tables (`input[type="checkbox"]`, `input[type="text"]`, `input[type="password"]`).
    - [ ] `renderBottomBar()`: Start X Accounts logic calculating from the active checkboxes dynamically.
- [ ] **Dialog & File Integrations**
  - [ ] Import `@tauri-apps/api/dialog`.
  - [ ] Wire the "Browse" button on Server Cards: `open({ directory: false, filters: [{ name: 'Executable', extensions: ['exe'] }] })`.
  - [ ] Wire Import/Export settings invoking `open()` and `save()` standard Tauri dialogs.

## Phase 7: Bi-Directional State Synchronization (Frontend <-> Backend)
- [ ] **Lifecycle Initialization**
  - [ ] Use TS `window.addEventListener("DOMContentLoaded", ...)` or Top-Level Await to execute `invoke("get_config")`.
  - [ ] Cache settings locally (`let currentConfig: Settings`).
  - [ ] Execute initial DOM Render.
- [ ] **Change Observers**
  - [ ] Bind `oninput` or `onchange` events directly to Input fields in TS loops. 
  - [ ] Every time an input changes (e.g., updating an Account Login or toggling "Run"), update `currentConfig`, recalculate the total accounts flagged, update the "Start X accounts" button string, and asynchronously call `invoke("save_config", { new_config: currentConfig })`.
  - [ ] Set up debouncing for text inputs to prevent spanning `save_config` RPCs on every single keystroke.

## Phase 8: Event-Driven Realtime Logging Subsystem
- [ ] **Rust Emitter Architecture**
  - [ ] In `src-tauri/src/launcher.rs`, during sequential launches, utilize `AppHandle::emit_all("launch-log", format!("..."))`.
  - [ ] Emit specific events for Success (green log), Info (gray log), and Error (red log).
- [ ] **Frontend Listener Consumption**
  - [ ] Import Tauri's `listen` API from `@tauri-apps/api/event`.
  - [ ] Attach listener explicitly mapping the emitted payload into a new HTML `<span>` or `<div>` inside the Log Panel DOM Node.
  - [ ] Implement auto-scroll tracking (`element.scrollTop = element.scrollHeight`) so fresh logs always remain visible.
- [ ] **Log Toggle UI**
  - [ ] Replicate the exact toggle button behavior using CSS `transform: translateY(100%)` for hiding, transitioning to `translateY(0)` for revealing, ensuring 60fps native GPU-accelerated animation.

## Phase 9: Quality Assurance & Optimization Parity Checks
- [ ] **Functional Validation**
  - [ ] Verify that importing an older Python app `settings.json` parses immediately in Rust with zero data loss.
  - [ ] Verify all accounts launch with correct client arguments and strictly honor Working Directories.
- [ ] **UI Parity Checklist**
  - [ ] Perform side-by-side visual comparison against the PySide6 executable at default dimensions, maximizing, and resizing.
  - [ ] Confirm inputs, row spacing, rounded corners, icons, and table alignments match completely.
- [ ] **Telemetry Checks**
  - [ ] Open Windows Task Manager -> View Tauri App Process.
  - [ ] Confirm IDLE memory falls between 15MB - 30MB (Compared to PySide 100MB+).

## Phase 10: Production Compilation & Distribution
- [ ] **Release Security Checks**
  - [ ] Open `tauri.conf.json`, navigate to `tauri.allowlist`. Strip out unused shell functions, keeping only necessary explicit APIs (`dialog.open/save`).
- [ ] **Final Build Generation**
  - [ ] Execute `npm run tauri build`.
  - [ ] Verify the MSI and standalone `.exe` structures are generated cleanly inside `src-tauri/target/release/`.
- [ ] **Release Testing**
  - [ ] Take the final standalone `app.exe` (should be ~4-6 MB), copy to a pristine folder, create a server dummy block, save logic, and verify it perfectly replicates all functionality independently from the Node/Rust environments.
