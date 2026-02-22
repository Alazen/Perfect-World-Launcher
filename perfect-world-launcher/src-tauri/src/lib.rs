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

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let initial_settings = crate::store::load_settings().unwrap_or_default();

    tauri::Builder::default()
        .manage(AppState::new(initial_settings))
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init()) // Dialog plugin needs to be initialized if we use native pickers
        .invoke_handler(tauri::generate_handler![
            get_config, save_config, launch_all, launch_server, launch_account
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
