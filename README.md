<div align="center">
  <img src="assets/pw_launcher_banner.png" alt="Perfect World Launcher banner" width="420" />
  <h1>Perfect World Launcher</h1>

  [![Tauri](https://img.shields.io/badge/Tauri-2.0-24C8DB?logo=tauri&logoColor=fff)](#)
  [![Rust](https://img.shields.io/badge/Rust-1.76+-000000?logo=rust&logoColor=fff)](#)
  [![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=fff)](#)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](#)

  <p>
    Manage multiple Perfect World accounts across any number of servers with one-click launch sequences, smart delays, and polished workflows tailored for multi-client players.
  </p>

  [Get Started](#get-started) • [Build From Source](#build-from-source)
</div>


### Multi-server Ready
Organize every private or official server in one interface with per-server launch controls.

### Smart Sequencing
Launch selected accounts sequentially with configurable delays to keep every client stable.

### Portable and Shareable
Import and export JSON profiles so guildmates or alts can reuse your exact setup in seconds.

## Core Capabilities

- Manage unlimited servers, each mapped to its own <code>elementclient.exe</code> path.
- Add accounts per server with saved login, password, and character details.
- Toggle which accounts participate in bulk launches with a Run checkbox.
- Launch a single account, a specific server, or every selected account with a single click.
- Configure a delay in seconds to keep multiple client launches stable.
- Import or export your entire configuration as JSON for backup and sharing.
## Requirements

- Windows 10 or Windows 11.
- A working Perfect World client for every server to be launched.
  - You need the path to that server's <code>elementclient.exe</code>.
  - The client must accept <code>startbypatcher</code> command-line arguments (standard for many Perfect World builds).
- No additional dependencies are required when using the packaged EXE.

## Get Started

1. Download the latest .exe from [Releases](https://github.com/Alazen/Perfect-World-Launcher/releases/).
2. Choose a folder: save the EXE somewhere you can write (for example Documents or Desktop). On first run the app creates `settings.json` next to the EXE.
3. If the folder is not writable (or you move the app), it automatically creates and natively stores settings at `%APPDATA%\PerfectWorldLauncher\settings.json`.
4. Launch the app: double click `Perfect World Launcher v24.0.exe`.

> Tip: keep the EXE and `settings.json` together to carry your setup between machines.

## UI Tour

| Area | What you get |
| :--- | :--- |
| **Top controls** | - **Import Settings**: load a `settings.json` file.<br>- **Export Settings**: save configuration to a chosen JSON path.<br>- **Delay (s)**: delay between launching each selected account. |
| **Servers list** | - **Add Server**: inserts a new server card.<br>- **Hide/Show**: collapse or expand the server details. |
| **Server card details** | - **Client Path**: browse to the server's `elementclient.exe`.<br>- **Play &lt;Server&gt;**: launch only the selected accounts for that server.<br>- **Server Launcher**: explicitly run the `Launcher.exe` located in your selected server directory.<br>- **Remove &lt;Server&gt;**: delete the server and all of its accounts.<br>- **Accounts table**: contains **Run?** checkbox, **Play** single char button, **Login**, **Password**, **Character**, and **Remove**.<br>- **Add Account**: append another account row to the server. |
| **Bottom controls** | - **Start X accounts**: launch every selected account.<br>- **Save and Close**: persist the current configuration and exit.<br>- **Show/Hide Log**: toggle the log panel. |

## Launching Accounts

### Global launch
1. Set the desired delay at the top.
2. Enable Run for the accounts you want to include.
3. Click **Start X accounts** to launch them sequentially.

### Per-server launch
Use **Play &lt;Server&gt;** on a server card to start only its selected accounts.

### Single-account launch
Hit **Play** in an account row for an immediate launch of that character.

> **Under the hood:** every launch executes `elementclient.exe startbypatcher user:<login> pwd:<password> role:<character>` with the working directory set to the client folder. Accounts are launched sequentially and the delay is applied between each one.

## Filling In Client Path

- Click <strong>Browse</strong> on a server card and select the correct <code>elementclient.exe</code>.
- Make sure the client supports <code>startbypatcher</code> for a seamless login.
- Paths are validated before launch; any missing or invalid path is highlighted in the log.

## Saving, Importing, and Exporting Settings

- Preferred storage: next to the EXE as `settings.json`.
- Automatic fallback: `%APPDATA%\PerfectWorldLauncher\settings.json` when the EXE folder is not writable.
- Settings save automatically before launching and when closing, and you can export them at any time.

Import and export share the same JSON structure:

```json
{
  "delay": 3,
  "servers": [
    {
      "name": "MyServer",
      "client_path": "C:\\Games\\PW\\MyServer\\elementclient.exe",
      "accounts": [
        { "run": true,  "login": "user1", "password": "pass1", "character": "CharA" },
        { "run": false, "login": "user2", "password": "pass2", "character": "CharB" }
      ]
    }
  ]
}
```

Notes worth remembering:

- The number shown in <strong>Start X accounts</strong> updates automatically as you toggle Run.
- Server and account names are trimmed but otherwise respected exactly as entered.

## Logs and Status

- Use <strong>Show Log</strong> to reveal a real-time panel with launch progress and issues.
- The status bar keeps a concise summary of the latest action.
- Logs only live for the current session and are not written to disk.

## Troubleshooting

- <strong>Client path is invalid or missing</strong>
  - Reopen the server card and point <strong>Client Path</strong> to the correct <code>elementclient.exe</code>.
- <strong>Nothing happens when launching</strong>
  - Confirm that login, password, and character fields are filled in.
  - Verify the client supports <code>startbypatcher</code> and that antivirus or anti-cheat software is not blocking the EXE.
  - Increase the delay to give each client more time to initialize.
- <strong>Save failed or permissions error</strong>
  - The app automatically switches to <code>%APPDATA%\PerfectWorldLauncher\settings.json</code>.
  - Move the EXE to a writable folder if you prefer to keep settings beside it.
- <strong>Antivirus warnings</strong>
  - Unsigned executables can trigger false positives. Add an exception if necessary.

## Security Notes

- Passwords are stored in plain text inside <code>settings.json</code>.
- Keep the file in a secure location and restrict access to the machine or OS account.
- Consider separate OS user accounts if you share a PC.

## Frequently Asked Questions

- <strong>Do I need to keep the window open during launch?</strong> Yes. Closing the app stops the sequence.
- <strong>Does the character name need to match exactly?</strong> Yes. Use the precise in-game name expected by the client.
- <strong>Can I run multiple servers at once?</strong> Yes. Add several servers, select the right accounts, and start them all sequentially.

## Known Limitations

- Works only with clients that accept the <code>startbypatcher</code> arguments; some servers may block this.
- Login and character values must match server expectations, including case and spacing.
- Launches are sequential by design; simultaneous launches are not supported.

## Updating

- Reuse your existing <code>settings.json</code> when updating the EXE.
- Keep <code>settings.json</code> next to the new EXE or in <code>%APPDATA%\PerfectWorldLauncher</code> for a seamless migration.

## Build From Source

The launcher is built using Tauri and Rust.
To build and run from source:

1. Ensure you have Node.js and Rust installed.
2. Navigate to the `perfect-world-launcher` directory:
   ```cmd
   cd perfect-world-launcher
   ```
3. Install dependencies (if you haven't already):
   ```cmd
   npm install
   ```
4. Build the application:
   ```cmd
   npm run tauri build
   ```
5. Run the compiled executable:
   ```cmd
   Start-Process .\src-tauri\target\release\perfect-world-launcher.exe
   ```

### Release Checklist

- Launch the freshly built EXE to confirm it opens and renders correctly.
- Ensure no stray files appear next to the executable (settings move to <code>%APPDATA%\PerfectWorldLauncher</code> if needed).
- Smoke test launching accounts and saving settings.

---

Made with Rust and Tauri. Portions of the code were produced with help from LLMs.
