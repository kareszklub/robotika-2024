use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[derive(Debug, Clone)]
pub enum Control {
    Bool { value: bool },
    Float { value: f32, min: f32, max: f32 },
    Int { value: i64, min: i64, max: i64 },
    String { value: String },
}
impl Control {
    pub async fn read<W>(w: &mut W) -> tokio::io::Result<Self>
    where
        W: AsyncReadExt + Unpin,
    {
        let t = w.read_u8().await?;
        Ok(match t {
            // bool:
            0 => {
                let value = w.read_u8().await? != 0;

                Self::Bool { value }
            }

            // float:
            1 => {
                let value = w.read_f32().await?;
                let min = w.read_f32().await?;
                let max = w.read_f32().await?;

                Self::Float { value, min, max }
            }

            // int:
            2 => {
                let value = w.read_i64().await?;
                let min = w.read_i64().await?;
                let max = w.read_i64().await?;

                Self::Int { value, min, max }
            }

            // string:
            3 => {
                let len = w.read_u16().await? as usize;

                let mut buf = vec![0; len];
                w.read_exact(&mut buf).await?;

                let value = String::from_utf8(buf).map_err(|_| {
                    tokio::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        format!("Invalid control type {t}"),
                    )
                })?;

                Self::String { value }
            }

            _ => Err(tokio::io::Error::new(
                std::io::ErrorKind::InvalidData,
                format!("Invalid control type {t}"),
            ))?,
        })
    }

    pub async fn write<W>(&self, w: &mut W) -> tokio::io::Result<()>
    where
        W: AsyncWriteExt + Unpin,
    {
        match self {
            Control::Bool { value } => w.write_u8(*value as u8).await,
            Control::Float { value, .. } => w.write_f32(*value).await,
            Control::Int { value, .. } => w.write_i64(*value).await,
            Control::String { value } => write_string(w, value).await,
        }
    }
}

pub async fn read_string<R>(w: &mut R, buf: &mut Vec<u8>) -> tokio::io::Result<String>
where
    R: AsyncReadExt + Unpin,
{
    let len = w.read_u16().await? as usize;

    buf.resize(len, 0);
    w.read_exact(buf).await?;

    let name = String::from_utf8(buf.clone())
        .map_err(|_| tokio::io::Error::new(std::io::ErrorKind::InvalidData, "Not valid utf-8"))?;

    Ok(name)
}

pub async fn write_string<W>(w: &mut W, s: &str) -> tokio::io::Result<()>
where
    W: AsyncWriteExt + Unpin,
{
    w.write_u16(s.len() as u16).await?;
    w.write_all(s.as_bytes()).await?;

    Ok(())
}
