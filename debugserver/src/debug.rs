use crate::message::Control;
use anyhow::anyhow;
use tokio::{
    io::{AsyncReadExt, BufStream},
    net::{TcpListener, TcpStream},
};

type Tx = tokio::sync::broadcast::Sender<String>;

pub async fn init(mut tx: Tx) -> anyhow::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:9999").await?;

    loop {
        let (socket, _) = listener.accept().await?;

        // will "block" this loop for the socket, meaning maximum one pico will be handled at any time
        if let Err(e) = process_socket(socket, &mut tx).await {
            error!("error while processing debug socket: {e}");
        }
    }
}

async fn process_socket(socket: TcpStream, tx: &mut Tx) -> anyhow::Result<()> {
    let mut socket = BufStream::new(socket);
    let mut buf = Vec::new();

    loop {
        let mtype = socket.read_u8().await?;

        match mtype {
            // 1: debug message
            1 => {
                let len = socket.read_u16().await? as usize;

                buf.resize(len, 0);
                socket.read_exact(&mut buf).await?;

                let msg = String::from_utf8(buf.clone())?;
                debug!("msg: {msg}");

                tx.send(msg)?;
            }

            // 2: define controls
            2 => {
                let len = socket.read_u16().await? as usize;
                let mut ctrls = Vec::with_capacity(len);

                for _ in 0..len {
                    ctrls.push(Control::read(&mut socket).await?);
                }

                // TODO: handle unprompted controls
            }

            t => Err(anyhow!("Invalid message type {t}"))?,
        }
    }
}
