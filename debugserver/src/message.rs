use tokio::io::{AsyncReadExt, AsyncWriteExt};

pub enum Control {
    Bool { default: bool },
    Float { default: f32, min: f32, max: f32 },
    Int { default: i64, min: i64, max: i64 },
    String { default: String },
}
impl Control {
    pub async fn read<A>(w: &mut A) -> tokio::io::Result<Self>
    where
        A: AsyncReadExt + Unpin,
    {
        let t = w.read_u8().await?;
        Ok(match t {
            // bool:
            0 => {
                let default = w.read_u8().await? != 0;
                Self::Bool { default }
            }

            // float:
            1 => {
                let default = w.read_f32().await?;
                let min = w.read_f32().await?;
                let max = w.read_f32().await?;
                Self::Float { default, min, max }
            }

            // int:
            2 => {
                let default = w.read_i64().await?;
                let min = w.read_i64().await?;
                let max = w.read_i64().await?;
                Self::Int { default, min, max }
            }

            // string:
            3 => {
                let len = w.read_u16().await? as usize;

                let mut buf = vec![0; len];
                w.read_exact(&mut buf).await?;

                let default = String::from_utf8(buf).map_err(|_| {
                    tokio::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        format!("Invalid control type {t}"),
                    )
                })?;

                Self::String { default }
            }

            _ => Err(tokio::io::Error::new(
                std::io::ErrorKind::InvalidData,
                format!("Invalid control type {t}"),
            ))?,
        })
    }
}

pub enum ControlValue {
    Bool(bool),
    Float(f32),
    Int(i64),
    String(String),
}

impl ControlValue {
    pub async fn write<A>(&self, w: &mut A) -> tokio::io::Result<()>
    where
        A: AsyncWriteExt + Unpin,
    {
        match self {
            ControlValue::Bool(v) => w.write_all(&(*v as u8).to_be_bytes()).await?,
            ControlValue::Float(v) => w.write_all(&v.to_be_bytes()).await?,
            ControlValue::Int(v) => w.write_all(&v.to_be_bytes()).await?,
            ControlValue::String(v) => {
                w.write_all(&(v.len() as u16).to_be_bytes()).await?;
                w.write_all(v.as_bytes()).await?
            }
        }

        Ok(())
    }
}
