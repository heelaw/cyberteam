//! CyberTeam Desktop - Main entry point
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use parking_lot::RwLock;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::process::Stdio;
use std::sync::Arc;
use tauri::{AppHandle, Emitter};
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command;
use tracing::{error, info, warn};
use uuid::Uuid;

/// Session information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub id: String,
    pub name: String,
    pub created_at: String,
    pub last_message: Option<String>,
}

/// Agent information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Agent {
    pub id: String,
    pub name: String,
    pub role: String,
    pub description: String,
    pub status: String,
    pub last_active: String,
}

/// Application state
pub struct AppState {
    pub sessions: RwLock<HashMap<String, Session>>,
    pub settings: RwLock<HashMap<String, String>>,
    pub active_processes: RwLock<HashMap<String, u32>>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            sessions: RwLock::new(HashMap::new()),
            settings: RwLock::new(HashMap::new()),
            active_processes: RwLock::new(HashMap::new()),
        }
    }
}

/// Initialize logging
fn init_logging() {
    use tracing_subscriber::{fmt, prelude::*, EnvFilter};

    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));

    tracing_subscriber::registry()
        .with(fmt::layer())
        .with(filter)
        .init();

    info!("CyberTeam Desktop logging initialized");
}

/// Get a setting value
#[tauri::command]
async fn get_setting(
    key: String,
    state: tauri::State<'_, Arc<AppState>>,
) -> Result<String, String> {
    let settings = state.settings.read();
    settings
        .get(&key)
        .cloned()
        .ok_or_else(|| format!("Setting '{}' not found", key))
}

/// Set a setting value
#[tauri::command]
async fn set_setting(
    key: String,
    value: String,
    state: tauri::State<'_, Arc<AppState>>,
) -> Result<(), String> {
    let mut settings = state.settings.write();
    settings.insert(key, value);
    Ok(())
}

/// Get Claude CLI path from settings
fn get_claude_path(state: &Arc<AppState>) -> String {
    let settings = state.settings.read();
    settings
        .get("claude_path")
        .cloned()
        .unwrap_or_else(|| "/opt/homebrew/bin/claude".to_string())
}

/// Get API key from settings
fn get_api_key(state: &Arc<AppState>) -> Option<String> {
    let settings = state.settings.read();
    settings.get("api_key").cloned()
}

/// Create a new Claude Code session
#[tauri::command]
async fn create_session(
    name: String,
    state: tauri::State<'_, Arc<AppState>>,
) -> Result<String, String> {
    let session_id = Uuid::new_v4().to_string();
    let session = Session {
        id: session_id.clone(),
        name,
        created_at: chrono_lite_now(),
        last_message: None,
    };

    let mut sessions = state.sessions.write();
    sessions.insert(session_id.clone(), session);

    info!("Created new session: {}", session_id);
    Ok(session_id)
}

/// List all sessions
#[tauri::command]
async fn list_sessions(
    state: tauri::State<'_, Arc<AppState>>,
) -> Result<Vec<Session>, String> {
    let sessions = state.sessions.read();
    let list: Vec<Session> = sessions.values().cloned().collect();
    Ok(list)
}

/// Get a session by ID
#[tauri::command]
async fn get_session(
    session_id: String,
    state: tauri::State<'_, Arc<AppState>>,
) -> Result<Session, String> {
    let sessions = state.sessions.read();
    sessions
        .get(&session_id)
        .cloned()
        .ok_or_else(|| format!("Session '{}' not found", session_id))
}

/// Send a message to Claude Code CLI
#[tauri::command]
async fn send_message(
    message: String,
    session_id: Option<String>,
    app: AppHandle,
    state: tauri::State<'_, Arc<AppState>>,
) -> Result<String, String> {
    let claude_path = get_claude_path(&state);
    let api_key = get_api_key(&state);

    info!("Sending message to Claude: {} (session: {:?})", message, session_id);

    // Build environment
    let mut env_vars: HashMap<String, String> = HashMap::new();
    if let Some(key) = api_key {
        env_vars.insert("ANTHROPIC_API_KEY".to_string(), key);
    }

    // Use --dangerously-skip-permissions for CLI usage without interactive prompt
    let mut cmd = Command::new(&claude_path);
    cmd.args(["--dangerously-skip-permissions", "--print", &message]);
    cmd.envs(&env_vars);
    cmd.stdout(Stdio::piped());
    cmd.stderr(Stdio::piped());

    #[cfg(not(target_os = "windows"))]
    {
        cmd.stdin(Stdio::null());
    }

    let mut child = cmd.spawn().map_err(|e| {
        error!("Failed to spawn claude process: {}", e);
        format!(
            "Failed to spawn Claude: {}. Is Claude Code CLI installed at {}?",
            e, claude_path
        )
    })?;

    let stdout = child.stdout.take().ok_or("Failed to capture stdout")?;
    let stderr = child.stderr.take().ok_or("Failed to capture stderr")?;

    let app_handle = app.clone();
    let session_id_clone = session_id.clone();

    // Read stdout in background and emit events
    let stdout_handle = tokio::spawn(async move {
        let reader = BufReader::new(stdout);
        let mut lines = reader.lines();
        let mut full_output = String::new();

        while let Ok(Some(line)) = lines.next_line().await {
            full_output.push_str(&line);
            full_output.push('\n');
            let _ = app_handle.emit("claude-output", &line);
        }

        full_output
    });

    // Read stderr in background
    let stderr_handle = tokio::spawn(async move {
        let reader = BufReader::new(stderr);
        let mut lines = reader.lines();
        let mut full_error = String::new();

        while let Ok(Some(line)) = lines.next_line().await {
            full_error.push_str(&line);
            full_error.push('\n');
        }

        full_error
    });

    // Wait for process to complete
    let status = child
        .wait()
        .await
        .map_err(|e| format!("Process error: {}", e))?;

    let stdout_output = stdout_handle
        .await
        .map_err(|e| format!("Stdout error: {}", e))?;
    let stderr_output = stderr_handle
        .await
        .map_err(|e| format!("Stderr error: {}", e))?;

    if !stderr_output.is_empty() {
        warn!("Claude stderr: {}", stderr_output);
    }

    if status.success() {
        let response = stdout_output.trim().to_string();

        // Update session if provided
        if let Some(sid) = session_id_clone {
            let mut sessions = state.sessions.write();
            if let Some(session) = sessions.get_mut(&sid) {
                session.last_message = Some(message);
            }
        }

        info!("Claude response received: {} chars", response.len());
        Ok(response)
    } else {
        let exit_code = status.code().unwrap_or(-1);
        error!("Claude process failed with exit code: {}", exit_code);
        Err(format!(
            "Claude exited with code {}: {}",
            exit_code,
            stderr_output.trim()
        ))
    }
}

/// List all agents
#[tauri::command]
async fn list_agents() -> Result<Vec<Agent>, String> {
    Ok(vec![
        Agent {
            id: "1".to_string(),
            name: "CEO".to_string(),
            role: "总指挥".to_string(),
            description: "负责决策和任务调度".to_string(),
            status: "idle".to_string(),
            last_active: "刚刚".to_string(),
        },
        Agent {
            id: "2".to_string(),
            name: "COO".to_string(),
            role: "运营总监".to_string(),
            description: "负责运营策略和执行".to_string(),
            status: "idle".to_string(),
            last_active: "刚刚".to_string(),
        },
        Agent {
            id: "3".to_string(),
            name: "CFO".to_string(),
            role: "财务总监".to_string(),
            description: "负责财务规划和预算".to_string(),
            status: "idle".to_string(),
            last_active: "刚刚".to_string(),
        },
        Agent {
            id: "4".to_string(),
            name: "CTO".to_string(),
            role: "技术总监".to_string(),
            description: "负责技术架构和开发".to_string(),
            status: "idle".to_string(),
            last_active: "刚刚".to_string(),
        },
        Agent {
            id: "5".to_string(),
            name: "信息部".to_string(),
            role: "信息收集".to_string(),
            description: "负责信息采集和分析".to_string(),
            status: "idle".to_string(),
            last_active: "刚刚".to_string(),
        },
        Agent {
            id: "6".to_string(),
            name: "质疑者".to_string(),
            role: "质量把控".to_string(),
            description: "负责质疑和验证".to_string(),
            status: "idle".to_string(),
            last_active: "刚刚".to_string(),
        },
    ])
}

/// Toggle a skill
#[tauri::command]
async fn toggle_skill(skill_id: String, enabled: bool) -> Result<(), String> {
    info!("Toggle skill {}: {}", skill_id, enabled);
    Ok(())
}

/// Stop a running session/process
#[tauri::command]
async fn stop_session(session_id: String) -> Result<(), String> {
    info!("Stop session: {}", session_id);
    Ok(())
}

/// Lightweight date/time function to avoid chrono dependency
fn chrono_lite_now() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default();
    format!("{}", now.as_secs())
}

fn main() {
    // Initialize logging first
    init_logging();

    tracing::info!("Starting CyberTeam Desktop v1.0.0");

    // Create Tauri application
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(Arc::new(AppState::default()))
        .invoke_handler(tauri::generate_handler![
            get_setting,
            set_setting,
            create_session,
            list_sessions,
            get_session,
            send_message,
            list_agents,
            toggle_skill,
            stop_session,
        ])
        .setup(|app| {
            tracing::info!("Application setup complete");

            // Set up global exception handler
            let handle = app.handle().clone();
            std::panic::set_hook(Box::new(move |info| {
                tracing::error!("PANIC: {}", info);
                let _ = handle.emit("app-error", format!("Critical error: {}", info));
            }));

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
