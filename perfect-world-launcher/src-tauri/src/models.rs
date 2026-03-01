use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Account {
    pub run: bool,
    pub login: String,
    pub password: String,
    pub character: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Server {
    pub name: String,
    pub client_path: String,
    pub accounts: Vec<Account>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settings {
    pub delay: u64,
    pub servers: Vec<Server>,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            delay: 3,
            servers: Vec::new(),
        }
    }
}
