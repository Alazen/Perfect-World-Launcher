<div align="center" style="background: linear-gradient(135deg, #1a2236, #0f172a); color: #f8fafc; padding: 48px 32px; border-radius: 20px; box-shadow: 0 18px 45px rgba(15, 19, 37, 0.35); margin-bottom: 32px;">
  <img src="assets/pw_launcher_banner.png" alt="Perfect World Launcher banner" width="420" style="border-radius: 18px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.45);" />
  <h1 style="font-size: 2.6rem; margin: 24px 0 12px;">Perfect World Launcher</h1>
  <p style="max-width: 760px; margin: 0 auto; line-height: 1.65; font-size: 1.05rem;">
    Manage multiple Perfect World accounts across any number of servers with one-click launch sequences, smart delays, and polished workflows tailored for multi-client players.
  </p>
  <div style="margin-top: 28px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap;">
    <a href="#get-started" style="">Get Started</a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="#build-from-source-optional" style="">Build From Source</a>
  </div>
</div>


  <div style="">
    <h3 style="margin: 0 0 10px; color: #f8fafc; font-size: 1.1rem;">Multi-server Ready</h3>
    <p style="margin: 0; color: rgba(226, 232, 240, 0.85); line-height: 1.6;">Organize every private or official server in one interface with per-server launch controls.</p>
  </div>
  <div style="">
    <h3 style="margin: 0 0 10px; color: #f8fafc; font-size: 1.1rem;">Smart Sequencing</h3>
    <p style="margin: 0; color: rgba(226, 232, 240, 0.85); line-height: 1.6;">Launch selected accounts sequentially with configurable delays to keep every client stable.</p>
  </div>
  <div style="">
    <h3 style="margin: 0 0 10px; color: #f8fafc; font-size: 1.1rem;">Portable and Shareable</h3>
    <p style="margin: 0; color: rgba(226, 232, 240, 0.85); line-height: 1.6;">Import and export JSON profiles so guildmates or alts can reuse your exact setup in seconds.</p>
  </div>

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
- No Python or additional dependencies are required when using the packaged EXE.

## Get Started

1. Download the latest .exe from [Releases](https://github.com/Alazen/Perfect-World-Launcher/releases/).
2. Choose a folder: save the EXE somewhere you can write (for example Documents or Desktop). On first run the app creates <code>settings.json</code> next to the EXE. If the folder is not writable, the app automatically stores settings at <code>%APPDATA%\PerfectWorldLauncher\settings.json</code>.
3. Launch the app: double click <code>Perfect World Launcher v23.0.exe</code>.

> Tip: keep the EXE and <code>settings.json</code> together to carry your setup between machines.

## UI Tour

<table style="width: 100%; border-collapse: separate; border-spacing: 0; margin-top: 16px; background: linear-gradient(160deg, rgba(12, 18, 32, 0.96), rgba(18, 28, 52, 0.92)); border: 1px solid rgba(148, 163, 184, 0.18); border-radius: 20px; overflow: hidden; box-shadow: 0 18px 45px rgba(7, 12, 24, 0.55);">
  <thead>
    <tr style="background: rgba(8, 13, 24, 0.95); color: #f8fafc;">
      <th align="left" style="padding: 14px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.16);">Area</th>
      <th align="left" style="padding: 14px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.16);">What you get</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background: rgba(15, 23, 42, 0.85); color: #e2e8f0;">
      <td style="padding: 18px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.12);"><strong>Top controls</strong></td>
      <td style="padding: 18px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.12);">
        <ul style="margin: 0; padding-left: 18px; color: rgba(226, 232, 240, 0.88);">
          <li><strong>Import Settings</strong>: load a <code>.json</code> settings file into the app.</li>
          <li><strong>Export Settings</strong>: save the current configuration to a chosen JSON path.</li>
          <li><strong>Delay (s)</strong>: sets the delay, in seconds, between launching each selected account.</li>
        </ul>
      </td>
    </tr>
    <tr style="background: rgba(18, 28, 52, 0.82); color: #e2e8f0;">
      <td style="padding: 18px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.12);"><strong>Servers list</strong></td>
      <td style="padding: 18px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.12);">
        <ul style="margin: 0; padding-left: 18px; color: rgba(226, 232, 240, 0.88);">
          <li><strong>Add Server</strong>: inserts a new server card.</li>
          <li>Each server card holds its name, client path, and an expandable accounts table.</li>
          <li><strong>Hide/Show</strong>: collapse or expand the server details when you want a cleaner workspace.</li>
        </ul>
      </td>
    </tr>
    <tr style="background: rgba(15, 23, 42, 0.85); color: #e2e8f0;">
      <td style="padding: 18px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.12);"><strong>Server card details</strong></td>
      <td style="padding: 18px 18px; border-bottom: 1px solid rgba(148, 163, 184, 0.12);">
        <ul style="margin: 0; padding-left: 18px; color: rgba(226, 232, 240, 0.88);">
          <li><strong>Client Path</strong>: browse to the server's <code>elementclient.exe</code>.</li>
          <li><strong>Play &lt;Server&gt;</strong>: launch only the selected accounts for that server.</li>
          <li><strong>Remove &lt;Server&gt;</strong>: delete the server and all of its accounts.</li>
          <li><strong>Accounts table</strong>:
            <ul style="margin: 0; padding-left: 18px; color: rgba(226, 232, 240, 0.8);">
              <li><strong>Run?</strong>: checkbox that decides whether the account participates in bulk start.</li>
              <li><strong>Play</strong>: launch that single account immediately.</li>
              <li><strong>Login</strong>, <strong>Password</strong>, <strong>Character</strong>: stored credentials for the server.</li>
              <li><strong>Remove</strong>: delete the account row.</li>
            </ul>
          </li>
          <li><strong>Add Account</strong>: append another account row to the server.</li>
        </ul>
      </td>
    </tr>
    <tr style="background: rgba(18, 28, 52, 0.82); color: #e2e8f0;">
      <td style="padding: 18px 18px;"><strong>Bottom controls</strong></td>
      <td style="padding: 18px 18px;">
        <ul style="margin: 0; padding-left: 18px; color: rgba(226, 232, 240, 0.88);">
          <li><strong>Start X accounts</strong>: launch every account with Run selected across all servers.</li>
          <li><strong>Save and Close</strong>: persist the current configuration and exit.</li>
          <li><strong>Show/Hide Log</strong>: toggle the log panel to observe launch progress and messages.</li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

## Launching Accounts

<div style="display: flex; gap: 18px; flex-wrap: nowrap; margin: 24px 0; background: linear-gradient(110deg, #0e1629, #152746); padding: 26px 28px; border-radius: 22px; box-shadow: 0 18px 45px rgba(7, 12, 24, 0.55); overflow-x: auto;">
  <div style="flex: 1 1 0; min-width: 240px; padding: 22px; background: linear-gradient(150deg, rgba(56, 189, 248, 0.26), rgba(12, 20, 36, 0.9)); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 16px; color: #e2e8f0;">
    <h3 style="margin-top: 0; color: #f8fafc;">Global launch</h3>
    <ol style="margin: 0; padding-left: 20px; line-height: 1.6; color: rgba(226, 232, 240, 0.88);">
      <li>Set the desired delay at the top.</li>
      <li>Enable Run for the accounts you want to include.</li>
      <li>Click <strong>Start X accounts</strong> to launch them sequentially.</li>
    </ol>
  </div>
  <div style="flex: 1 1 0; min-width: 240px; padding: 22px; background: linear-gradient(150deg, rgba(99, 102, 241, 0.24), rgba(14, 22, 38, 0.92)); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 16px; color: #e2e8f0;">
    <h3 style="margin-top: 0; color: #f8fafc;">Per-server launch</h3>
    <p style="margin: 0; line-height: 1.6; color: rgba(226, 232, 240, 0.88);">Use <strong>Play &lt;Server&gt;</strong> on a server card to start only its selected accounts.</p>
  </div>
  <div style="flex: 1 1 0; min-width: 240px; padding: 22px; background: linear-gradient(150deg, rgba(168, 85, 247, 0.28), rgba(16, 24, 42, 0.92)); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 16px; color: #e2e8f0;">
    <h3 style="margin-top: 0; color: #f8fafc;">Single-account launch</h3>
    <p style="margin: 0; line-height: 1.6; color: rgba(226, 232, 240, 0.88);">Hit <strong>Play</strong> in an account row for an immediate launch of that character.</p>
  </div>
</div>

<div style="margin: 24px 0; padding: 20px; border-radius: 14px; background: linear-gradient(135deg, #0b1323, #131f33); color: #f8fafc; border: 1px solid rgba(148, 163, 184, 0.2); box-shadow: 0 18px 45px rgba(7, 12, 24, 0.55);">
  <strong>Under the hood:</strong> every launch executes <code>elementclient.exe startbypatcher user:&lt;login&gt; pwd:&lt;password&gt; role:&lt;character&gt;</code> with the working directory set to the client folder. Accounts are launched sequentially and the delay is applied between each one.
</div>

## Filling In Client Path

- Click <strong>Browse</strong> on a server card and select the correct <code>elementclient.exe</code>.
- Make sure the client supports <code>startbypatcher</code> for a seamless login.
- Paths are validated before launch; any missing or invalid path is highlighted in the log.

## Saving, Importing, and Exporting Settings

- Preferred storage: next to the EXE as <code>settings.json</code>.
- Automatic fallback: <code>%APPDATA%\PerfectWorldLauncher\settings.json</code> when the EXE folder is not writable.
- Settings save automatically before launching and when closing, and you can export them at any time.

Import and export share the same JSON structure:

<pre style="background: rgba(10, 16, 28, 0.95); color: #e2e8f0; border: 1px solid rgba(148, 163, 184, 0.18); border-radius: 16px; padding: 18px 20px; margin: 16px 0; box-shadow: 0 18px 45px rgba(7, 12, 24, 0.55);"><code class="language-json">{
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
}</code></pre>

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
  - PyInstaller-built executables can trigger false positives. Add an exception if necessary.

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

## Build From Source (optional)

- Requires Python 3.11 or newer and <code>pip install PySide6 pyinstaller</code>.
- Entry point: <code>perfect_world_launcher_v23.0/perfect_world_launcher_v23.0.py</code>.
- PyInstaller spec: <code>PerfectWorldLauncher.spec</code> (bundles icons and defaults).
- Qt resources: run <code>pyside6-rcc perfect_world_launcher_v23.0/launcher/resources/app_icon.qrc -o perfect_world_launcher_v23.0/launcher/resources/app_icon_rc.py</code> after updating <code>assets/pw_launcher_icon_3.ico</code>.
- One-file build pipeline: <code>pwsh ./tools/build-onefile.ps1</code> regenerates resources, runs PyInstaller with <code>--onefile</code>, and places <code>Perfect World Launcher v&lt;version&gt;.exe</code> in <code>dist/</code>.

### Release Checklist

- Launch the freshly built EXE on a machine without Python to confirm it opens and renders correctly.
- Ensure no stray files appear next to the executable (settings move to <code>%APPDATA%\PerfectWorldLauncher</code> if needed).
- Smoke test launching accounts and saving settings.

---

Made with PySide6. Portions of the code were produced with help from LLMs.
