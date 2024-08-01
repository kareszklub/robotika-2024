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
    io::{AsyncReadExt, AsyncWriteExt, BufStream},
    net::{TcpListener, TcpStream},
    sync::{mpsc, Notify},
};

pub async fn init(
    state: Arc<AppState>,
    mut ctrl_rx: mpsc::UnboundedReceiver<(String, Control)>,
    disconnect: Arc<Notify>,
) -> anyhow::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:9999").await?;

    loop {
        info!("waiting for new connection");

        let (socket, _) = listener.accept().await?;

        info!("new client connected: {}", socket.peer_addr()?);

        // will "block" this loop for the socket, meaning maximum one pico will be handled at any time
        if let Err(e) = process_socket(socket, &state, &mut ctrl_rx, &disconnect).await {
            error!("error while processing debug socket: {e}");
        }
    }
}

async fn process_socket(
    socket: TcpStream,
    state: &AppState,
    ctrl_rx: &mut mpsc::UnboundedReceiver<(String, Control)>,
    disconnect: &Notify,
) -> anyhow::Result<()> {
    let mut socket = BufStream::new(socket);

    let mut buf = Vec::new();

    loop {
        tokio::select! {
            mtype = socket.read_u8() => recv_socket(&mut socket, state, &mut buf, mtype?).await?,

            val = ctrl_rx.recv() => {
                let (name, control) = val.expect("ctrl_rx closed???");

                write_string(&mut socket, &name).await?;
                control.write(&mut socket).await?;
            },

            () = disconnect.notified() => {
                info!("disconnecting...");
                return Ok(())
            }
        }

        socket.flush().await?;
    }
}

// read and process a singular message
async fn recv_socket<R>(
    socket: &mut R,
    state: &AppState,
    buf: &mut Vec<u8>,
    mtype: u8,
) -> anyhow::Result<()>
where
    R: AsyncReadExt + AsyncWriteExt + Unpin,
{
    match mtype {
        // 1: debug message
        1 => {
            let msg = read_string(socket, buf).await?;
            debug!("msg: {msg}");

            state.msg_tx.send(SseMessage::Log(msg))?;
        }

        // 2: define controls
        2 => {
            let len = socket.read_u16().await? as u32;

            let mut ctrls: HashMap<String, (u32, Control)> = HashMap::new();
            for i in 0..len {
                let name = read_string(socket, buf).await?;
                ctrls.insert(name, (i, Control::read(socket).await?));
            }

            let mut hs = state.config.write().await;

            // filter out removed values
            hs.retain(|k, _| ctrls.contains_key(k));

            for (name, (i, control)) in ctrls {
                match hs.entry(name) {
                    // new value introduced on the pico
                    Entry::Vacant(entry) => {
                        entry.insert((i, control));
                    }

                    // override already exists
                    Entry::Occupied(entry) => {
                        write_string(socket, entry.key()).await?;
                        entry.get().1.write(socket).await?;
                    }
                };
            }
            drop(hs);
            socket.flush().await?;

            state.msg_tx.send(SseMessage::ControlsChanged)?;
        }

        t => Err(anyhow!("Invalid message type {t}"))?,
    }

    Ok(())
}
