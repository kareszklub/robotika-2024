use anyhow::anyhow;
use tokio::{
    io::{AsyncReadExt, BufStream},
    net::{TcpListener, TcpStream},
    sync::mpsc::{UnboundedReceiver, UnboundedSender},
};

use crate::message::{Control, ControlValue, Message};

type Tx = UnboundedSender<Message>;
type Rx = UnboundedReceiver<ControlValue>;

pub async fn init(mut tx: Tx, mut rx: Rx) -> anyhow::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:9999").await?;

    loop {
        let (socket, _) = listener.accept().await?;

        if let Err(e) = process_socket(socket, &mut tx, &mut rx).await {
            error!("error while processing debug socket: {e}");
        }
    }
}

async fn process_socket(socket: TcpStream, tx: &mut Tx, rx: &mut Rx) -> anyhow::Result<()> {
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

                tx.send(Message::Print(msg))?;
            }

            // 2: define controls
            2 => {
                let len = socket.read_u16().await? as usize;
                let mut ctrls = Vec::with_capacity(len);

                for _ in 0..len {
                    ctrls.push(Control::read(&mut socket).await?);
                }

                tx.send(Message::DefineControls(ctrls))?;
            }

            // 3: get control value
            3 => {
                let c = socket.read_u8().await?;
                tx.send(Message::GetControlValue(c))?;

                let v = rx.recv().await.ok_or(anyhow!("No response??"))?;
                v.write(&mut socket).await?;
            }

            t => Err(anyhow!("Invalid message type {t}"))?,
        }
    }
}
