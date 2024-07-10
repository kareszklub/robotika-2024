mod debug;
mod http;
mod message;
pub mod templates;

#[macro_use]
extern crate log;
use std::env;
use tokio::{
    io::AsyncWriteExt,
    sync::broadcast::{Receiver, Sender},
    task::JoinHandle,
};

type Tx = Sender<String>;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    if env::var("RUST_LOG").is_err() {
        env::set_var("RUST_LOG", "debugserver=debug");
    }

    pretty_env_logger::init();

    let (msg_tx, msg_rx) = tokio::sync::broadcast::channel(1024);

    let file_task = tokio::task::spawn(log_file(msg_rx));
    let debug_task = tokio::task::spawn({
        let tx = msg_tx.clone();
        debug::init(tx)
    });
    let http_task = tokio::task::spawn(http::init(msg_tx));

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

async fn log_file(mut rx: Receiver<String>) -> anyhow::Result<()> {
    let mut file = tokio::fs::File::options()
        .create(true)
        .append(true)
        .open("debugserver.log")
        .await?;

    while let Ok(msg) = rx.recv().await {
        file.write_all((msg + "\n").as_bytes()).await?;
    }

    Ok(())
}
