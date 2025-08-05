use std::env;
use std::path::Path;
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::OnceLock;

use pyo3::types::PyAnyMethods;
use pyo3::Python;
use tracing::error;
use tracing_subscriber::filter::FilterFn;
use tracing_subscriber::layer::SubscriberExt;
use tracing_subscriber::util::SubscriberInitExt;
use tracing_subscriber::{EnvFilter, Layer};
use utils::normalized_path_from_user_string;

use crate::telemetry::{init_telemetry_logging, restart_telemetry_task_after_spawn};

/// Default log level for the library to use. Override using `RUST_LOG` env variable.
#[cfg(not(debug_assertions))]
const DEFAULT_LOG_LEVEL: &str = "warn";

#[cfg(debug_assertions)]
const DEFAULT_LOG_LEVEL: &str = "warn";

fn use_json() -> Option<bool> {
    env::var("HF_XET_LOG_FORMAT").ok().map(|s| s.eq_ignore_ascii_case("json"))
}

fn init_logging_to_file(path: &Path) -> Result<(), std::io::Error> {
    // Set up logging to a file.
    use std::ffi::OsStr;

    use tracing_appender::{non_blocking, rolling};

    let (path, file_name) = match path.file_name() {
        Some(name) => (path.to_path_buf(), name),
        None => (path.join("xet.log"), OsStr::new("xet.log")),
    };

    let log_directory = match path.parent() {
        Some(parent) => {
            std::fs::create_dir_all(parent)?;
            parent
        },
        None => Path::new("."),
    };

    // Make sure the log location is writeable so we error early here and dump to stderr on failure.
    std::fs::write(&path, [])?;

    // Build a non‑blocking file appender. • `rolling::never` = one static file, no rotation. • Keep the
    // `WorkerGuard` alive so the background thread doesn’t shut down and drop messages.
    let file_appender = rolling::never(log_directory, file_name);

    let (writer, guard) = non_blocking(file_appender);

    // Store the guard globally so it isn’t dropped.
    static FILE_GUARD: OnceLock<tracing_appender::non_blocking::WorkerGuard> = OnceLock::new();
    let _ = FILE_GUARD.set(guard); // ignore error if already initialised

    // Build the fmt layer.
    let fmt_layer_base = tracing_subscriber::fmt::layer()
        .with_line_number(true)
        .with_file(true)
        .with_target(false)
        .with_writer(writer);

    // Standard filter layer: RUST_LOG env var or DEFAULT_LOG_LEVEL fallback.
    let filter_layer = EnvFilter::try_from_default_env()
        .or_else(|_| EnvFilter::try_new(DEFAULT_LOG_LEVEL))
        .unwrap_or_default();

    // Initialise the subscriber.
    if use_json().unwrap_or(true) {
        tracing_subscriber::registry()
            .with(fmt_layer_base.json())
            .with(filter_layer)
            .init();
    } else {
        tracing_subscriber::registry()
            .with(fmt_layer_base.pretty())
            .with(filter_layer)
            .init();
    }

    Ok(())
}

fn get_version_info_string(py: Python<'_>) -> String {
    // populate remote telemetry calls with versions for python and hf_hub if possible
    let mut version_info = String::new();

    // Get Python version
    if let Ok(sys) = py.import("sys") {
        if let Ok(version) = sys.getattr("version").and_then(|v| v.extract::<String>()) {
            if let Some(python_version_number) = version.split_whitespace().next() {
                version_info.push_str(&format!("python/{python_version_number}; "));
            }
        }
    }

    // Get huggingface_hub+hf_xet versions
    let package_names = ["huggingface_hub", "hfxet"];
    if let Ok(importlib_metadata) = py.import("importlib.metadata") {
        for package_name in package_names.iter() {
            if let Ok(version) = importlib_metadata
                .call_method1("version", (package_name,))
                .and_then(|v| v.extract::<String>())
            {
                version_info.push_str(&format!("{package_name}/{version}; "));
            }
        }
    }
    version_info
}

fn init_global_logging(py: Python) {
    let version_info = get_version_info_string(py);

    if let Ok(log_path_s) = env::var("HF_XET_LOG_FILE") {
        let log_path = normalized_path_from_user_string(log_path_s);
        match init_logging_to_file(&log_path) {
            Ok(_) => return,
            Err(e) => {
                eprintln!("Error opening log file {log_path:?} for writing: {e:?}.  Reverting to logging to console.");
            },
        }
    }

    let fmt_layer_base = tracing_subscriber::fmt::layer()
        .with_line_number(true)
        .with_file(true)
        .with_target(false);

    let filter_layer = EnvFilter::try_from_default_env()
        .or_else(|_| EnvFilter::try_new(DEFAULT_LOG_LEVEL))
        .unwrap_or_default();

    // Do we use telemetry?
    if env::var("HF_HUB_ENABLE_TELEMETRY").is_ok() {
        match init_telemetry_logging(version_info) {
            Ok(tl) => {
                let telemetry_filter_layer = tl.with_filter(FilterFn::new(|meta| meta.target() == "client_telemetry"));

                tracing_subscriber::registry()
                    .with(filter_layer)
                    .with(fmt_layer_base.json())
                    .with(telemetry_filter_layer)
                    .init();

                return;
            },

            Err(e) => {
                eprintln!("Error initializing telemetry process : {e:?}. Reverting to logging to console.");
            },
        }
    }

    // Now, just use basic console logging.
    let tr_sub = tracing_subscriber::registry().with(filter_layer);

    if use_json().unwrap_or(false) {
        tr_sub.with(fmt_layer_base.json()).init();
    } else {
        tr_sub.with(fmt_layer_base.pretty()).init();
    }
}

static INITIALIZED_LOGGING_ID: AtomicU32 = AtomicU32::new(0);

pub fn check_logging_state(py: Python<'_>) {
    let logger_pid = INITIALIZED_LOGGING_ID.load(Ordering::SeqCst);

    let pid = std::process::id();

    if logger_pid == 0 {
        init_global_logging(py);
        INITIALIZED_LOGGING_ID.store(pid, Ordering::SeqCst);
    } else if logger_pid != pid {
        if let Err(e) = restart_telemetry_task_after_spawn() {
            error!("Error restarting telemetry task in subprocess; telemtry may not work: {e:?}");
        }
    }
}
