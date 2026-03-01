#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

pub mod models;
pub mod store;
pub mod state;
pub mod launcher;

// Prevents additional console window on Windows in release, DO NOT REMOVE!!
fn main() {
    perfect_world_launcher_lib::run()
}
