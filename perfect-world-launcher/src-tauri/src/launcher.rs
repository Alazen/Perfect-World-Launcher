use std::process::Command;
use std::path::Path;
use tauri::{AppHandle, Emitter};
use std::thread;
use std::time::Duration;
use crate::models::{Account, Server};

pub fn launch_target_accounts(app: AppHandle, mut targets: Vec<(Server, Account)>, delay: u64) {
    std::thread::spawn(move || {
        let total = targets.len();
        for (i, (server, account)) in targets.drain(..).enumerate() {
            let _ = app.emit("launch-log", format!("Starting ({}/{}) - Server: {} - Account: {}", i + 1, total, server.name, account.character));
            
            // Argument assembly matches Python original
            let arg_string = format!(
                "user:{} pwd:{} role:{}",
                account.login, account.password, account.character
            );

            let client_path = Path::new(&server.client_path);
            let parent_dir = client_path.parent().unwrap_or(Path::new(""));

            match Command::new(&server.client_path)
                .arg("startbypatcher")
                .arg(&arg_string)
                .current_dir(parent_dir)
                .spawn()
            {
                Ok(_) => {
                    let _ = app.emit("launch-log", format!("Successfully launched {}", account.character));
                },
                Err(e) => {
                    let _ = app.emit("launch-log", format!("Failed to launch {}: {}", account.character, e));
                }
            }

            // Sleep if not the last account
            if i < total - 1 {
                let _ = app.emit("launch-log", format!("Waiting {} seconds...", delay));
                thread::sleep(Duration::from_secs(delay));
            }
        }
        let _ = app.emit("launch-log", "Launch sequence complete.".to_string());
    });
}

pub fn launch_server_launcher(app: AppHandle, client_path_str: &str) {
    let client_path = Path::new(client_path_str);
    
    // We need to find the element dir. Usually client_path is something like:
    // C:\Games\PW New History 1.8.7\element\x64\ElementClient_64.exe
    // or C:\Games\PW New History 1.8.7\element\ElementClient.exe
    
    let mut current = client_path.parent();
    let mut root_dir = None;
    
    while let Some(path) = current {
        if let Some(file_name) = path.file_name() {
            if file_name.to_string_lossy().to_lowercase() == "element" {
                root_dir = path.parent();
                break;
            }
        }
        current = path.parent();
    }
    
    let root_path = match root_dir {
        Some(p) => p,
        None => {
            let _ = app.emit("launch-log", format!("Could not find 'element' folder in path: {}", client_path_str));
            return;
        }
    };
    
    let launcher_dir = root_path.join("launcher");
    let launcher_exe = launcher_dir.join("Launcher.exe");
    
    if !launcher_exe.exists() {
        let _ = app.emit("launch-log", format!("Launcher not found at: {}", launcher_exe.display()));
        return;
    }
    
    let _ = app.emit("launch-log", format!("Starting Server Launcher from: {}", launcher_exe.display()));
    
    // Launch the Launcher.exe
    match Command::new(&launcher_exe)
        .current_dir(&launcher_dir)
        .spawn()
    {
        Ok(_) => {
            let _ = app.emit("launch-log", "Successfully launched Server Launcher");
        },
        Err(e) => {
            let _ = app.emit("launch-log", format!("Failed to launch Server Launcher: {}", e));
        }
    }
}
