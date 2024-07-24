use crate::{templates, AppState, SseMessage};
use askama_axum::IntoResponse;
use axum::{
    extract::State,
    http::{header, StatusCode, Uri},
    response::{
        sse::{Event, KeepAlive, Sse},
        Response,
    },
    routing::get,
    Router,
};
use futures_util::stream::Stream;
use itertools::Itertools;
use rust_embed::Embed;
use std::{convert::Infallible, sync::Arc};

pub async fn init(state: Arc<AppState>) -> anyhow::Result<()> {
    let router = Router::new()
        .route("/", get(templates::Index::get))
        .route(
            "/controls",
            get(templates::Controls::get).post(templates::Controls::post),
        )
        .route("/logs/stream", get(sse_handler))
        .route("/static/*file", get(static_handler))
        .with_state(state);

    let addr = "0.0.0.0:8080";

    let listener = tokio::net::TcpListener::bind(&addr).await?;
    info!("Listening on {addr}");

    axum::serve(listener, router).await?;

    Ok(())
}

async fn sse_handler(
    State(state): State<Arc<AppState>>,
) -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let mut rx = state.msg_tx.subscribe();
    let mut id = 0u32;

    let stream = async_stream::stream! {
        while let Ok(msg) = rx.recv().await {
            let txt = match msg {
                SseMessage::Log(msg) => {
                    if id == 0 {
                        format!("<p hx-swap-oob=\"outerHTML:#logs-placeholder\">{msg}</p>")
                    } else {
                        format!("<p>{msg}</p>")
                    }
                }

                SseMessage::ControlsChanged => {
                    let config = state.config.read().await;
                    let config = config.iter().sorted_by_cached_key(|(_, (i, _))| *i);

                    crate::templates::Controls { config, oob: true }.to_string()
                },
            };

            yield Ok(Event::default().event("log").id(id.to_string()).data(txt));

            id += 1;
        }
    };

    Sse::new(stream).keep_alive(KeepAlive::default())
}

#[derive(Embed)]
#[folder = "static"]
struct Asset;

pub struct StaticFile<T>(pub T);

impl<T> IntoResponse for StaticFile<T>
where
    T: Into<String>,
{
    fn into_response(self) -> Response {
        let path = self.0.into();

        match Asset::get(path.as_str()) {
            Some(content) => {
                let mime = mime_guess::from_path(path).first_or_octet_stream();
                ([(header::CONTENT_TYPE, mime.as_ref())], content.data).into_response()
            }

            None => (StatusCode::NOT_FOUND, "404 Not Found").into_response(),
        }
    }
}

async fn static_handler(uri: Uri) -> impl IntoResponse {
    let mut path = uri.path().trim_start_matches('/').to_string();

    if path.starts_with("static/") {
        path = path.replace("static/", "");
    }

    StaticFile(path)
}
