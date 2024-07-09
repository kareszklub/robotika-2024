mod debug;
mod http;
mod message;
mod templates;

#[macro_use]
extern crate log;
use std::env;
use tokio::task::JoinHandle;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    if env::var("RUST_LOG").is_err() {
        env::set_var("RUST_LOG", "debugserver=debug");
    }

    pretty_env_logger::init();

    let (msg_tx, msg_rx) = tokio::sync::mpsc::unbounded_channel();
    let (res_tx, res_rx) = tokio::sync::mpsc::unbounded_channel();

    let debug_task = tokio::task::spawn(async { debug::init(msg_tx, res_rx).await });
    let http_task = tokio::task::spawn(async { http::init().await });

    let _ = tokio::try_join!(flatten(http_task), flatten(debug_task))?;

    Ok(())
}

async fn flatten<T>(handle: JoinHandle<anyhow::Result<T>>) -> anyhow::Result<T> {
    match handle.await {
        Ok(Ok(result)) => Ok(result),
        Ok(Err(err)) => Err(err),
        Err(err) => anyhow::Result::Err(err.into()),
    }
}
