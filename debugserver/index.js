window.htmx = require('htmx.org').default;
require("htmx-ext-sse");

const onload = () => {
    document.body.querySelectorAll("input[type=range]").forEach(range => {
        let number = range.parentElement.parentElement.querySelector("input[type=number]");

        range.addEventListener("input", ()=>{
            number.value = range.value;
        });
    });

    document.body.querySelectorAll("input[type=number]").forEach(number => {
        let range = number.parentElement.querySelector("input[type=range]");

        number.addEventListener("change", () => {
            range.value = number.value;
            range.dispatchEvent(new Event('change'));
        });
    });
};

document.addEventListener("DOMContentLoaded", onload);

document.addEventListener("htmx:load", e => e.detail.elt.id === "controls" && onload());
