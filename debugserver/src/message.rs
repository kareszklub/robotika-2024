use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[derive(Debug, Clone)]
pub enum Control {
    Bool { value: bool },
    Float { value: f32, min: f32, max: f32 },
    Int { value: i64, min: i64, max: i64 },
    String(String),
    Color(u8, u8, u8),
}
impl Control {
    pub async fn read<R>(r: &mut R) -> tokio::io::Result<Self>
    where
        R: AsyncReadExt + Unpin,
    {
        Ok(match r.read_u8().await? {
            // bool:
            0 => Self::Bool {
                value: r.read_u8().await? != 0,
            },

            // float:
            1 => {
                let value = r.read_f32().await?;
                let min = r.read_f32().await?;
                let max = r.read_f32().await?;

                Self::Float { value, min, max }
            }

            // int:
            2 => {
                let value = r.read_i64().await?;
                let min = r.read_i64().await?;
                let max = r.read_i64().await?;

                Self::Int { value, min, max }
            }

            // string:
            3 => {
                let len = r.read_u16().await? as usize;

                let mut buf = vec![0; len];
                r.read_exact(&mut buf).await?;

                let value = String::from_utf8(buf).map_err(|_| {
                    tokio::io::Error::new(std::io::ErrorKind::InvalidData, "Invalid utf string")
                })?;

                Self::String(value)
            }

            // color:
            4 => Self::Color(r.read_u8().await?, r.read_u8().await?, r.read_u8().await?),

            t => Err(tokio::io::Error::new(
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
            Control::String(value) => write_string(w, value).await,
            Control::Color(r, g, b) => {
                w.write_u8(*r).await?;
                w.write_u8(*g).await?;
                w.write_u8(*b).await
            }
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
