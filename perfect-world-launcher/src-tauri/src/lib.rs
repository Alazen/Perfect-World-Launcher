pub mod models;
pub mod store;
pub mod state;
pub mod launcher;

use tauri::{AppHandle, State, Manager, Emitter};
use crate::models::{Settings, Server, Account};
use crate::state::AppState;

#[tauri::command]
fn get_config(state: State<AppState>) -> Settings {
    let settings = state.settings.lock().unwrap();
    settings.clone()
}

#[tauri::command]
fn save_config(new_config: Settings, state: State<AppState>) -> Result<(), String> {
    let mut settings = state.settings.lock().unwrap();
    *settings = new_config.clone();
    crate::store::save_settings(&settings)
}

#[tauri::command]
fn export_settings_to_file(path: String, state: State<AppState>) -> Result<(), String> {
    let settings = state.settings.lock().unwrap();
    let data = serde_json::to_string_pretty(&*settings).map_err(|e| e.to_string())?;
    std::fs::write(path, data).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn import_settings_from_file(path: String, state: State<AppState>) -> Result<Settings, String> {
    let data = std::fs::read_to_string(path).map_err(|e| e.to_string())?;
    let new_settings: Settings = serde_json::from_str(&data).map_err(|e| e.to_string())?;
    
    let mut settings = state.settings.lock().unwrap();
    *settings = new_settings.clone();
    
    crate::store::save_settings(&settings)?;
    
    Ok(new_settings)
}

#[tauri::command]
async fn launch_all(app: AppHandle, state: State<'_, AppState>) -> Result<(), ()> {
    let delay = { state.settings.lock().unwrap().delay };
    let servers = { state.settings.lock().unwrap().servers.clone() };

    let mut targets: Vec<(Server, Account)> = Vec::new();
    for server in &servers {
        for account in &server.accounts {
            if account.run {
                targets.push((server.clone(), account.clone()));
            }
        }
    }

    if targets.is_empty() {
        let _ = app.emit("launch-log", "No enabled accounts selected. Aborting.");
        return Ok(());
    }

    crate::launcher::launch_target_accounts(app, targets, delay);
    Ok(())
}

#[tauri::command]
async fn launch_server(app: AppHandle, state: State<'_, AppState>, server_index: usize) -> Result<(), ()> {
    let (delay, server) = {
        let settings = state.settings.lock().unwrap();
        if server_index >= settings.servers.len() {
            return Ok(());
        }
        (settings.delay, settings.servers[server_index].clone())
    };

    let mut targets: Vec<(Server, Account)> = Vec::new();
    for account in server.accounts.clone() {
        if account.run {
            targets.push((server.clone(), account));
        }
    }

    if targets.is_empty() {
        let _ = app.emit("launch-log", format!("No enabled accounts on {} selected.", server.name));
        return Ok(());
    }

    crate::launcher::launch_target_accounts(app, targets, delay);
    Ok(())
}

#[tauri::command]
async fn launch_account(app: AppHandle, state: State<'_, AppState>, server_index: usize, account_index: usize) -> Result<(), ()> {
    let targets = {
        let settings = state.settings.lock().unwrap();
        if server_index >= settings.servers.len() {
            return Ok(());
        }
        let server = &settings.servers[server_index];
        if account_index >= server.accounts.len() {
            return Ok(());
        }
        vec![(server.clone(), server.accounts[account_index].clone())]
    };

    crate::launcher::launch_target_accounts(app, targets, 0); // Single account has no delay context
    Ok(())
}

#[tauri::command]
async fn launch_server_launcher(app: AppHandle, state: State<'_, AppState>, server_index: usize) -> Result<(), ()> {
    let client_path = {
        let settings = state.settings.lock().unwrap();
        if server_index >= settings.servers.len() {
            return Ok(());
        }
        settings.servers[server_index].client_path.clone()
    };

    if !client_path.is_empty() {
        crate::launcher::launch_server_launcher(app, &client_path);
    } else {
        let _ = app.emit("launch-log", "Client path is empty. Cannot launch server launcher.");
    }
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let initial_settings = crate::store::load_settings().unwrap_or_default();

    tauri::Builder::default()
        .manage(AppState::new(initial_settings))
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init()) // Dialog plugin needs to be initialized if we use native pickers
        .invoke_handler(tauri::generate_handler![
            get_config, save_config, launch_all, launch_server, launch_account, launch_server_launcher,
            export_settings_to_file, import_settings_from_file
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
