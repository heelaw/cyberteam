// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::io::Write;
use std::process::{Command, Stdio};
use std::sync::Mutex;
use tauri::State;

// ============ Types ============

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClaudeMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionInfo {
    pub id: String,
    pub agent_id: String,
    pub status: String,
    pub created_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpawnResult {
    pub session_key: String,
    pub success: bool,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SendResult {
    pub success: bool,
    pub reply: Option<String>,
    pub error: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListResult {
    pub sessions: Vec<SessionInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Settings {
    pub provider: String,
    pub api_key: String,
    pub base_url: String,
    pub model: String,
}

// ============ State ============

pub struct AppState {
    pub sessions: Mutex<HashMap<String, SessionChild>>,
    pub settings: Mutex<Option<Settings>>,
    pub claude_code_path: Mutex<String>,
}

pub struct SessionChild {
    pub child: Option<std::process::Child>,
    pub agent_id: String,
    pub status: String,
    pub created_at: i64,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            sessions: Mutex::new(HashMap::new()),
            settings: Mutex::new(None),
            claude_code_path: Mutex::new("/opt/homebrew/bin/claude".to_string()),
        }
    }
}

// ============ Commands ============

#[tauri::command]
fn get_claude_path(state: State<AppState>) -> String {
    state.claude_code_path.lock().unwrap().clone()
}

#[tauri::command]
fn set_claude_path(path: String, state: State<AppState>) -> bool {
    // Verify the path exists
    if std::path::Path::new(&path).exists() {
        *state.claude_code_path.lock().unwrap() = path;
        true
    } else {
        false
    }
}

#[tauri::command]
fn save_settings(settings: Settings, state: State<AppState>) -> bool {
    *state.settings.lock().unwrap() = Some(settings);
    true
}

#[tauri::command]
fn get_settings(state: State<AppState>) -> Option<Settings> {
    state.settings.lock().unwrap().clone()
}

#[tauri::command]
fn spawn_session(
    task: String,
    agent_id: String,
    run_timeout_seconds: Option<u64>,
    model: Option<String>,
    state: State<AppState>,
) -> SpawnResult {
    let session_key = format!("tauri:{}:{}", agent_id, uuid_simple());

    // Build Claude CLI arguments
    let claude_path = state.claude_code_path.lock().unwrap().clone();
    let timeout = run_timeout_seconds.unwrap_or(300);

    // Use --print flag for non-interactive mode
    let mut args = vec![
        "--print".to_string(),
        "--output-format".to_string(), "stream-json".to_string(),
    ];

    if let Some(m) = model {
        args.push("--model".to_string());
        args.push(m);
    }

    // Add the task
    args.push(task);

    // Spawn Claude Code CLI
    let child = Command::new(&claude_path)
        .args(&args)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn();

    match child {
        Ok(child) => {
            let session = SessionChild {
                child: Some(child),
                agent_id: agent_id.clone(),
                status: "running".to_string(),
                created_at: unix_timestamp(),
            };
            state.sessions.lock().unwrap().insert(session_key.clone(), session);

            SpawnResult {
                session_key,
                success: true,
                error: None,
            }
        }
        Err(e) => SpawnResult {
            session_key: session_key.clone(),
            success: false,
            error: Some(e.to_string()),
        },
    }
}

#[tauri::command]
fn send_to_session(session_key: String, message: String, state: State<AppState>) -> SendResult {
    let mut sessions = state.sessions.lock().unwrap();

    if let Some(session) = sessions.get_mut(&session_key) {
        if let Some(ref mut child) = session.child {
            if let Some(ref mut stdin) = child.stdin {
                match stdin.write_all(format!("{}\n", message).as_bytes()) {
                    Ok(_) => {
                        return SendResult {
                            success: true,
                            reply: None,
                            error: None,
                        };
                    }
                    Err(e) => {
                        return SendResult {
                            success: false,
                            reply: None,
                            error: Some(e.to_string()),
                        };
                    }
                }
            }
        }
    }

    SendResult {
        success: false,
        reply: None,
        error: Some("Session not found or stdin not available".to_string()),
    }
}

#[tauri::command]
fn list_sessions(state: State<AppState>) -> ListResult {
    let sessions = state.sessions.lock().unwrap();

    let infos: Vec<SessionInfo> = sessions
        .values()
        .map(|s| SessionInfo {
            id: format!("{:x}", s.created_at),
            agent_id: s.agent_id.clone(),
            status: s.status.clone(),
            created_at: s.created_at,
        })
        .collect();

    ListResult { sessions: infos }
}

#[tauri::command]
fn stop_session(session_key: String, state: State<AppState>) -> bool {
    let mut sessions = state.sessions.lock().unwrap();

    if let Some(mut session) = sessions.remove(&session_key) {
        if let Some(ref mut child) = session.child {
            let _ = child.kill();
            let _ = child.wait();
        }
        session.status = "stopped".to_string();
        true
    } else {
        false
    }
}

#[tauri::command]
fn read_session_output(session_key: String, state: State<AppState>) -> Option<String> {
    let sessions = state.sessions.lock().unwrap();

    if let Some(session) = sessions.get(&session_key) {
        if let Some(ref child) = session.child {
            use std::io::Read;
            if let Some(ref mut stdout) = child.stdout {
                let mut buf = String::new();
                match stdout.read_to_string(&mut buf) {
                    Ok(_) => return Some(buf),
                    Err(_) => return None,
                }
            }
        }
    }
    None
}

// ============ Helpers ============

fn uuid_simple() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap();
    format!("{:x}{:x}", duration.as_secs(), duration.subsec_nanos())
}

fn unix_timestamp() -> i64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs() as i64
}

// ============ Main ============

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(AppState::default())
        .invoke_handler(tauri::generate_handler![
            get_claude_path,
            set_claude_path,
            save_settings,
            get_settings,
            spawn_session,
            send_to_session,
            list_sessions,
            stop_session,
            read_session_output,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
