use tokio::{
    io::AsyncReadExt,
    net::{TcpListener, TcpStream},
    sync::mpsc::UnboundedSender,
};

type Tx = UnboundedSender<String>;

pub async fn init(tx: Tx) -> anyhow::Result<()> {
    let listener = TcpListener::bind("0.0.0.0:9999").await?;
    loop {
        let (socket, _) = listener.accept().await?;

        if let Err(e) = process_socket(socket, tx.clone()).await {
            error!("error while processing debug socket: {e}");
        }
    }
}

async fn process_socket(mut socket: TcpStream, tx: Tx) -> anyhow::Result<()> {
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

            // exit
            0 => {
                info!("client disconnected");
                return Ok(());
            }

            _ => (),
        }
    }
}
