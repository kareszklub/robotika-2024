use crate::{AppState, Control, IP};
use askama::Template;
use askama_axum::IntoResponse;
use axum::{extract::State, response::Response, Form};
use itertools::Itertools;
use std::ops::Deref;
use std::{collections::HashMap, sync::Arc};

#[derive(Template)]
#[template(path = "index.html")]
pub(crate) struct Index<'a> {
    controls: Controls<'a>,
}
impl<'a> Index<'a> {
    pub async fn get(state: State<Arc<AppState>>) -> Response {
        let config = state.config.read().await;
        let config = config.iter().sorted_by_cached_key(|(_, (i, _))| *i);

        Index {
            controls: Controls { config, oob: false },
        }
        .into_response()
    }
}

#[derive(Template)]
#[template(path = "controls.html")]
pub(crate) struct Controls<'a> {
    pub config: std::vec::IntoIter<(&'a String, &'a (u32, Control))>,
    pub oob: bool,
}
impl<'a> Controls<'a> {
    pub async fn get(state: State<Arc<AppState>>) -> Response {
        let config = state.config.read().await;
        let config = config.iter().sorted_by_cached_key(|(_, (i, _))| *i);

        Controls { config, oob: false }.into_response()
    }

    pub async fn post(
        State(state): State<Arc<AppState>>,
        Form(body): Form<HashMap<String, String>>,
    ) -> impl IntoResponse {
        if body.len() > 1 {
            warn!("multiple controls updated: {body:?}");
        }

        let mut hs = state.config.write().await;
        for (ctrl_name, ctrl_val) in body {
            let Some(c) = hs.get_mut(&ctrl_name).map(|c| &mut c.1) else {
                error!("Invalid control update received for \"{ctrl_name}\"");
                continue;
            };

            match c {
                Control::Bool { value } => {
                    let b = match &ctrl_val[..] {
                        "on" | "true" => true,
                        "" | "false" => false,

                        _ => {
                            error!("Invalid bool update: {ctrl_val}");
                            continue;
                        }
                    };

                    debug!("{ctrl_name}: {value} => {b}");
                    *value = b;
                }

                Control::Float { value, min, max } => {
                    let Ok(n) = ctrl_val.parse() else {
                        error!("Invalid float update: {ctrl_val}");
                        continue;
                    };

                    if *min <= n && n <= *max {
                        debug!("{ctrl_name}: {value} => {n}");
                        *value = n;
                    } else {
                        warn!("Out of bound control");
                    }
                }

                Control::Int { value, min, max } => {
                    let Ok(n) = ctrl_val.parse() else {
                        error!("Invalid int update: {ctrl_val}");
                        continue;
                    };

                    if *min <= n && n <= *max {
                        debug!("{ctrl_name}: {value} => {n}");
                        *value = n;
                    } else {
                        warn!("Out of bound control");
                    }
                }

                Control::String(value) => {
                    debug!("{ctrl_name}: {value} => {ctrl_val}");
                    *value = ctrl_val;
                }

                Control::Color(r, g, b) => {
                    let rgb = (
                        parse_hex_byte(&ctrl_val[1..=2]),
                        parse_hex_byte(&ctrl_val[3..=4]),
                        parse_hex_byte(&ctrl_val[5..=6]),
                    );

                    if let (Ok(rr), Ok(gg), Ok(bb)) = rgb {
                        debug!("{ctrl_name}: ({r}, {g}, {b}) => ({rr}, {gg}, {bb})");

                        *r = rr;
                        *g = gg;
                        *b = bb;
                    } else {
                        error!("Invalid color update: {ctrl_val}");
                    }
                }
            }

            state
                .ctrl_tx
                .send((ctrl_name, c.clone()))
                .expect("Control update channel closed");
        }
    }
}

fn parse_hex_digit(c: char) -> Result<u8, &'static str> {
    Ok(match c {
        '0'..='9' => c as u8 - b'0',
        'a'..='f' => c as u8 + 10 - b'a',
        'A'..='F' => c as u8 + 10 - b'A',

        _ => Err("Invalid hex digit")?,
    })
}

fn parse_hex_byte(s: &str) -> Result<u8, &'static str> {
    let mut chars = s.chars();

    let (c1, c2) = (
        chars.next().ok_or("Missing hex digit")?,
        chars.next().ok_or("Missing hex digit")?,
    );

    let (c1, c2) = (parse_hex_digit(c1)?, parse_hex_digit(c2)?);

    Ok(0x10 * c1 + c2)
}
