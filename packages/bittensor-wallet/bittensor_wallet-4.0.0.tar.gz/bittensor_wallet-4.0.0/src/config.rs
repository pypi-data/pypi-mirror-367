use std::fmt::Display;

use crate::constants::{BT_WALLET_HOTKEY, BT_WALLET_NAME, BT_WALLET_PATH};

#[derive(Clone)]
pub struct WalletConfig {
    pub name: String,
    pub path: String,
    pub hotkey: String,
}

impl WalletConfig {
    pub fn new(name: Option<String>, hotkey: Option<String>, path: Option<String>) -> Self {
        WalletConfig {
            name: name.unwrap_or_else(|| BT_WALLET_NAME.to_string()),
            hotkey: hotkey.unwrap_or_else(|| BT_WALLET_HOTKEY.to_string()),
            path: path.unwrap_or_else(|| BT_WALLET_PATH.to_string()),
        }
    }
}

#[derive(Clone)]
pub struct Config {
    pub wallet: WalletConfig,
}

impl Display for Config {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "Config(name: '{}', path: '{}', hotkey: '{}'",
            self.wallet.name, self.wallet.path, self.wallet.hotkey
        )
    }
}

impl Config {
    pub fn new(name: Option<String>, hotkey: Option<String>, path: Option<String>) -> Config {
        Config {
            wallet: WalletConfig::new(name, hotkey, path),
        }
    }

    pub fn name(&self) -> String {
        self.wallet.name.clone()
    }

    pub fn path(&self) -> String {
        self.wallet.path.clone()
    }

    pub fn hotkey(&self) -> String {
        self.wallet.hotkey.clone()
    }
}
