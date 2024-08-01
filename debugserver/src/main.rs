mod debug;
mod http;
mod message;
mod templates;

#[macro_use]
extern crate log;
use local_ip_address::local_ip;
use message::Control;
use std::{
    collections::HashMap,
    env,
    sync::{Arc, LazyLock},
};
use tokio::{
    io::AsyncWriteExt,
    sync::{broadcast, mpsc, Notify, RwLock},
    task::JoinHandle,
};

pub type Config = HashMap<String, (u32, Control)>;

#[derive(Debug, Clone)]
pub(crate) enum SseMessage {
    Log(String),
    ControlsChanged,
}

pub(crate) struct AppState {
    pub msg_tx: broadcast::Sender<SseMessage>,
    pub ctrl_tx: mpsc::UnboundedSender<(String, Control)>,
    pub config: RwLock<Config>,

    pub disconnect: Arc<Notify>,
}

static IP: LazyLock<String> =
    LazyLock::new(|| local_ip().expect("Couldn't get ip address").to_string());

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    if env::var("RUST_LOG").is_err() {
        env::set_var("RUST_LOG", "debugserver=debug");
    }

    pretty_env_logger::init();

    LazyLock::force(&IP);

    let (msg_tx, msg_rx) = broadcast::channel(1024);
    let (ctrl_tx, ctrl_rx) = mpsc::unbounded_channel();

    let disconnect = Arc::new(Notify::new());
    let state = Arc::new(AppState {
        msg_tx,
        ctrl_tx,
        config: Default::default(),
        disconnect: disconnect.clone(),
    });

    let file_task = tokio::task::spawn(log_file(msg_rx));
    let debug_task = tokio::task::spawn(debug::init(state.clone(), ctrl_rx, disconnect));
    let http_task = tokio::task::spawn(http::init(state));

    let _ = tokio::try_join!(flatten(file_task), flatten(http_task), flatten(debug_task))?;

    Ok(())
}

async fn flatten<T>(handle: JoinHandle<anyhow::Result<T>>) -> anyhow::Result<T> {
    match handle.await {
        Ok(Ok(result)) => Ok(result),
        Ok(Err(err)) => Err(err),
        Err(err) => anyhow::Result::Err(err.into()),
    }
}

async fn log_file(mut rx: broadcast::Receiver<SseMessage>) -> anyhow::Result<()> {
    let mut file = tokio::fs::File::options()
        .create(true)
        .append(true)
        .open("debugserver.log")
        .await?;

    while let Ok(msg) = rx.recv().await {
        if let SseMessage::Log(msg) = msg {
            file.write_all((msg + "\n").as_bytes()).await?;
        }
    }

    Ok(())
}
