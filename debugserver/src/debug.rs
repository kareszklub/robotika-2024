use crate::{
    message::{read_string, write_string, Control},
    AppState, SseMessage,
};
use anyhow::anyhow;
use std::{
    collections::{hash_map::Entry, HashMap},
    sync::Arc,
};
use tokio::{
    io::{AsyncReadExt, BufStream},
    net::{TcpListener, TcpStream},
    sync::mpsc::UnboundedReceiver,
};

pub async fn init(
    state: Arc<AppState>,
    ctrl_rx: UnboundedReceiver<(String, Control)>,
) -> anyhow::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:9999").await?;

    loop {
        let (socket, _) = listener.accept().await?;

        // will "block" this loop for the socket, meaning maximum one pico will be handled at any time
        if let Err(e) = process_socket(socket, &state, &ctrl_rx).await {
            error!("error while processing debug socket: {e}");
        }
    }
}

async fn process_socket(
    socket: TcpStream,
    state: &AppState,
    ctrl_rx: &UnboundedReceiver<(String, Control)>,
) -> anyhow::Result<()> {
    let mut socket = BufStream::new(socket);
    let mut buf = Vec::new();

    loop {
        let mtype = socket.read_u8().await?;

        match mtype {
            // 1: debug message
            1 => {
                let msg = read_string(&mut socket, &mut buf).await?;
                debug!("msg: {msg}");

                state.msg_tx.send(SseMessage::Log(msg))?;
            }

            // 2: define controls
            2 => {
                let len = socket.read_u16().await? as usize;

                let mut ctrls: HashMap<String, Control> = HashMap::new();
                for _ in 0..len {
                    let name = read_string(&mut socket, &mut buf).await?;
                    ctrls.insert(name, Control::read(&mut socket).await?);
                }

                let mut hs = state.config.write().await;

                // filter out removed values
                hs.retain(|k, _| ctrls.contains_key(k));

                for (name, control) in ctrls {
                    match hs.entry(name) {
                        // new value introduced on the pico
                        Entry::Vacant(entry) => {
                            entry.insert(control);
                        }

                        // override already exists
                        Entry::Occupied(entry) => {
                            write_string(&mut socket, entry.key()).await?;
                            entry.get().write(&mut socket).await?;
                        }
                    };
                }
            }

            t => Err(anyhow!("Invalid message type {t}"))?,
        }
    }
}
