# Goal Description
Add a "Launcher" button next to the "Play <Server>" button on each server card. This button will dynamically determine the location of the server's `Launcher.exe` based on the configured `elementclient.exe` path and execute it.

## User Review Required
No major architectural changes are required. The main design decision is how to compute the root directory of the game.
We will compute the root directory by parsing the path of the `elementclient.exe`, locating the `element` directory within its path components (case-insensitive), and treating the directory immediately preceding it as the game root. From the game root, the launcher path is constructed as `<root>/launcher/Launcher.exe`.

## Proposed Changes

### UI Modifications
#### [MODIFY] `perfect_world_launcher_v24.0/launcher/ui/server_card.py`
- In `__init__`, instantiate a new `QPushButton` named `launcher_button` with the text "Launcher".
- Apply `Theme.button_secondary` style to it.
- Add the `launcher_button` to the `header_layout`, placing it between the `play_button` and `remove_button`.
- Connect the button's `clicked` signal to a new method `self.open_launcher()`.
- Update `update_display_strings` to set the button's text to "Launcher `display_name`" just like how the "Play" and "Remove" buttons work.
- Add `open_launcher` method:
  - Calls `self.window.open_server_launcher(self.index)` to handle the logic.

### Application Logic Modifications
#### [MODIFY] `perfect_world_launcher_v24.0/launcher/ui/window.py`
- Add a new method `open_server_launcher(self, server_index: int)`:
  - Gets the corresponding server model based on the index.
  - Passes the `client_path` to a helper function.
  - Logs the outcome to the log panel.

#### [NEW/MODIFY] `perfect_world_launcher_v24.0/launcher/services/launch.py` (Optional / Helper)
- Add a helper function `launch_server_updater(client_path: str)` that implements the path resolution and `subprocess.Popen` execution.

## Verification Plan

### Automated Tests
- No existing automated tests were found.

### Manual Verification
1. Launch the application `python perfect_world_launcher_v24.0.py`.
2. Add a new server or use an existing one.
3. Configure the `Client Path` to point to a valid (or mocked) `elementclient.exe`.
   - Test Case 1: `C:\Games\PW New History 1.8.7\element\x64\ElementClient_64.exe`
   - Test Case 2: `C:\Games\PW New History 1.8.7\element\ElementClient.exe`
4. Click the "Launcher <Server>" button.
5. Verify in the Log panel that the application correctly resolved the path to `C:\Games\PW New History 1.8.7\launcher\Launcher.exe`.
6. Verify that the correct executable is started (if it exists on disk).
