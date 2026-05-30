use std::path::PathBuf;
use std::process::Command;

/// Run `markitdown <path>` and return its stdout as a UTF-8 string.
///
/// The CLI must be installed on the user's PATH (e.g.
/// `pip install markitdown-postproc`). On Windows we also try `markitdown.exe`
/// and `py -m markitdown` as fallbacks.
#[tauri::command]
fn convert_file(path: String, strip_boilerplate: bool) -> Result<String, String> {
    let p = PathBuf::from(&path);
    if !p.exists() {
        return Err(format!("File not found: {}", path));
    }

    // We invoke the CLI rather than embedding Python so the desktop binary
    // stays small. The strip_boilerplate flag is passed via env var because
    // the upstream CLI doesn't yet expose it as a switch; the Python entry
    // point reads MARKITDOWN_STRIP_BOILERPLATE in this fork.
    let candidates: &[&[&str]] = if cfg!(windows) {
        &[
            &["markitdown"],
            &["markitdown.exe"],
            &["py", "-m", "markitdown"],
            &["python", "-m", "markitdown"],
        ]
    } else {
        &[&["markitdown"], &["python3", "-m", "markitdown"], &["python", "-m", "markitdown"]]
    };

    let mut last_err: Option<String> = None;
    for cmd in candidates {
        let mut command = Command::new(cmd[0]);
        for arg in &cmd[1..] {
            command.arg(arg);
        }
        command.arg(&path);
        if strip_boilerplate {
            command.env("MARKITDOWN_STRIP_BOILERPLATE", "1");
        }

        match command.output() {
            Ok(out) if out.status.success() => {
                return Ok(String::from_utf8_lossy(&out.stdout).into_owned());
            }
            Ok(out) => {
                last_err = Some(format!(
                    "{} exited with status {}: {}",
                    cmd.join(" "),
                    out.status,
                    String::from_utf8_lossy(&out.stderr).trim()
                ));
            }
            Err(e) => {
                last_err = Some(format!("Failed to launch {}: {}", cmd.join(" "), e));
            }
        }
    }

    Err(last_err.unwrap_or_else(|| {
        "Could not find a working `markitdown` CLI. Install with: pip install markitdown-postproc".to_string()
    }))
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![convert_file])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
