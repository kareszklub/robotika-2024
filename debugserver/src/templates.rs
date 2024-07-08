use askama::Template;
use askama_axum::IntoResponse;

#[derive(Template)]
#[template(path = "index.html")]
pub struct Index {}
impl Index {
    pub async fn get() -> impl IntoResponse {
        Self {}
    }
}
