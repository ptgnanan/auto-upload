use std::path::PathBuf;

#[cfg(windows)]
pub fn check_webview2() -> Result<(), String> {
    use winreg::enums::*;
    use winreg::RegKey;
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    let key = hkcu.open_subkey("SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
        .or_else(|_| hkcu.open_subkey("SOFTWARE\\Microsoft\\EdgeUpdate\\Clients\\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"));
    match key {
        Ok(k) => {
            let version: String = k.get_value("pv").unwrap_or_default();
            if version.is_empty() {
                Err("WebView2 not installed".to_string())
            } else {
                Ok(())
            }
        }
        Err(_) => Err("WebView2 not installed".to_string())
    }
}

#[cfg(not(windows))]
pub fn check_webview2() -> Result<(), String> {
    Ok(())
}

pub fn get_data_dir() -> PathBuf {
    #[cfg(windows)]
    {
        std::env::var("LOCALAPPDATA")
            .map(PathBuf::from)
            .unwrap_or_else(|_| PathBuf::from("."))
            .join("AI Social Auto Upload")
    }
    #[cfg(not(windows))]
    {
        std::env::var("HOME").map(|h| PathBuf::from(h)).unwrap_or_else(|_| PathBuf::from("."))
            .join(".local/share/ai-social-auto-upload")
    }
}

pub fn create_data_dirs(data_dir: &PathBuf) -> std::io::Result<()> {
    std::fs::create_dir_all(data_dir.join("db"))?;
    std::fs::create_dir_all(data_dir.join("cookies"))?;
    Ok(())
}