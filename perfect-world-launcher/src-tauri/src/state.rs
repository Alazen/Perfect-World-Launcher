use std::sync::Mutex;
use crate::models::Settings;

pub struct AppState {
    pub settings: Mutex<Settings>,
}

impl AppState {
    pub fn new(initial: Settings) -> Self {
        Self {
            settings: Mutex::new(initial),
        }
    }
}
