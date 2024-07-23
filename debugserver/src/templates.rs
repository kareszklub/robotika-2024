use crate::IP;
use crate::{AppState, Control};
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
        for (name, control) in body {
            match hs.get_mut(&name).map(|c| &mut c.1) {
                Some(Control::Bool { value }) => {
                    let b = control == "on" || control == "true";

                    debug!("{name}: {value} => {b}");
                    *value = b;
                }

                Some(Control::Float { value, min, max }) => {
                    let n = control.parse().unwrap();

                    if *min <= n && n <= *max {
                        debug!("{name}: {value} => {n}");
                        *value = n;
                    }
                }

                Some(Control::Int { value, min, max }) => {
                    let n = control.parse().unwrap();
                    if *min <= n && n <= *max {
                        debug!("{name}: {value} => {n}");
                        *value = n;
                    }
                }

                Some(Control::String { value }) => {
                    debug!("{name}: {value} => {control}");
                    *value = control;
                }

                None => error!("invalid name {name}"),
            }

            let (_, c) = hs.get(&name).unwrap();
            state.ctrl_tx.send((name, c.to_owned())).unwrap();
        }
    }
}
