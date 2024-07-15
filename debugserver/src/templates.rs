use std::sync::Arc;

use crate::{AppState, Config};
use askama::Template;
use askama_axum::IntoResponse;
use axum::{
    extract::State,
    http::{header, StatusCode},
    response::Response,
};

#[derive(Template)]
#[template(path = "index.html")]
pub struct Index<'a> {
    config: &'a Config,
}
pub async fn index(state: State<Arc<AppState>>) -> Response {
    let config = state.config.read().await;
    let template = Index { config: &config };

    match template.render() {
        Ok(body) => {
            let headers = [(
                header::CONTENT_TYPE,
                axum::http::HeaderValue::from_static(Index::MIME_TYPE),
            )];

            (headers, body).into_response()
        }
        Err(_) => StatusCode::INTERNAL_SERVER_ERROR.into_response(),
    }
}
