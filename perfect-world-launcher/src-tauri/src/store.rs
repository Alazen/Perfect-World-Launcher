use std::fs;
use std::path::PathBuf;
use crate::models::Settings;
use directories::ProjectDirs;

fn get_settings_path() -> PathBuf {
    let mut exe_path = std::env::current_exe().unwrap_or_else(|_| PathBuf::from("perfect-world-launcher.exe"));
    exe_path.pop();
    let local_settings = exe_path.join("settings.json");

    // Try to write logic: check if exists, or try creating to see if directory is writable
    if local_settings.exists() {
        // Can we write to it?
        if let Ok(file) = fs::OpenOptions::new().write(true).open(&local_settings) {
            return local_settings;
        }
    } else {
        // Try creating
        if let Ok(_) = fs::File::create(&local_settings) {
            return local_settings;
        }
    }

    // Fallback to APPDATA logic
    if let Some(proj_dirs) = ProjectDirs::from("", "", "PerfectWorldLauncher") {
        let config_dir = proj_dirs.config_dir();
        if !config_dir.exists() {
            let _ = fs::create_dir_all(config_dir);
        }
        return config_dir.join("settings.json");
    }

    local_settings
}

pub fn load_settings() -> Result<Settings, String> {
    let path = get_settings_path();
    if !path.exists() {
        return Ok(Settings::default());
    }
    let data = fs::read_to_string(&path).map_err(|e| e.to_string())?;
    // if JSON is malformed, we might want to return default instead of error
    let settings = serde_json::from_str(&data).unwrap_or_else(|_| Settings::default());
    Ok(settings)
}

pub fn save_settings(settings: &Settings) -> Result<(), String> {
    let path = get_settings_path();
    let data = serde_json::to_string_pretty(settings).map_err(|e| e.to_string())?;
    fs::write(path, data).map_err(|e| e.to_string())?;
    Ok(())
}
