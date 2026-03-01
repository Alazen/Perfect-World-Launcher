# Perfect World Launcher Documentation

## Building the Application for Release

To build the executable for release and ensure all frontend assets are properly bundled, you **must use the Tauri CLI command** from the root folder of the project (`perfect-world-launcher`).

### Correct Build Command

```bash
npm run tauri build
```

This command will:
1. Automatically build the frontend assets (using `vite build`).
2. Move the built assets into the `dist` directory.
3. Build the Rust backend natively, embedding the `dist` assets into the executable.

After running this command, the compiled release executable will be located at:
`src-tauri/target/release/perfect-world-launcher.exe`

### ⚠️ Incorrect Build Command (Do Not Use)

**Do not** use `cargo build --release` inside the `src-tauri` directory to generate the final executable.

While this will successfully compile the `.exe`, it will bypass Tauri's frontend build process. As a result, the launcher will attempt to connect to the active dev server at `localhost` instead of loading embedded assets. This will result in an `ERR_CONNECTION_REFUSED` error when opening the app because the dev server is not running in production.
