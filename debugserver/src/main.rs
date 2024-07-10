mod debug;
mod http;
mod templates;

#[macro_use]
extern crate log;
use std::env;
use tokio::{sync::broadcast::Sender, task::JoinHandle};

type Tx = Sender<String>;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    if env::var("RUST_LOG").is_err() {
        env::set_var("RUST_LOG", "debugserver=debug");
    }
    pretty_env_logger::init();

    let (tx, _rx) = tokio::sync::broadcast::channel(1024);

    let debug_task = tokio::task::spawn({
        let tx = tx.clone();
        async { debug::init(tx).await }
    });
    let http_task = tokio::task::spawn(async { http::init(tx).await });

    let _res = tokio::try_join!(flatten(http_task), flatten(debug_task))?;
    Ok(())
}

async fn flatten<T>(handle: JoinHandle<anyhow::Result<T>>) -> anyhow::Result<T> {
    match handle.await {
        Ok(Ok(result)) => Ok(result),
        Ok(Err(err)) => Err(err),
        Err(err) => anyhow::Result::Err(err.into()),
    }
}
