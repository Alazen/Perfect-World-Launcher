# Execution Checklist

## Phase 1: Logic Implementation
- [x] **1.1. Path Resolution Logic**
  - Implement a mechanism (e.g., in `launcher/services/launch.py` or as a standalone utility) that parses an `elementclient.exe` path.
  - Find the `element` folder in the path components (case-insensitive) to locate the root directory.
  - Return the computed `<root>/launcher/Launcher.exe` path.
- [x] **1.2. Launcher Execution**
  - Implement the execution of the resolved launcher executable using `subprocess.Popen`.
  - Ensure the working directory `cwd` for `Popen` is set to the `<root>/launcher` folder.
  - Add appropriate logging (e.g., via a pyqt signal or print to GUI logs) to display success or failure of finding/launching the executable.
- [x] **1.3. Window Controller Update**
  - Add `open_server_launcher(self, server_index: int)` to `launcher/ui/window.py`.
  - Wire it to fetch the `client_path` from the corresponding `ServerConfig` and call the method implemented in 1.1 / 1.2.

## Phase 2: UI Implementation
- [x] **2.1. ServerCard Button Creation**
  - In `launcher/ui/server_card.py`, instantiate a `QPushButton` named `launcher_button` with text "Launcher".
  - Apply the secondary button style using `Theme.button_secondary`.
  - Add this button to the `header_layout` adjacent to the "Play <Server>" button.
  - Connect its `clicked` signal to a new `open_launcher` method in the `ServerCard` class.
- [x] **2.2. ServerCard Methods**
  - Implement `open_launcher` to delegate the action to `self.window.open_server_launcher(self.index)`.
  - Update `update_display_strings` so the text updates to "Launcher <Server>" dynamically, similar to the existing buttons.

## Phase 3: Verification
- [ ] **3.1. Build and Run**
  - Run `python perfect_world_launcher_v24.0.py`.
  - Ensure the application opens without any UI layout issues.
- [ ] **3.2. Manual Testing**
  - Add a server pointing to a dummy or actual `C:\Games\PW New History 1.8.7\element\x64\ElementClient_64.exe`.
  - Click the "Launcher <Server>" button.
  - Verify through logs that the expected path `C:\Games\PW New History 1.8.7\launcher\Launcher.exe` is computed and executed.
  - Repeat the test with a path like `C:\Games\PW New History 1.8.7\element\ElementClient.exe`.
