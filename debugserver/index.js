window.htmx = require('htmx.org').default;
require("htmx-ext-sse");

const numWidth = number => (number.style.width = 6 + Math.max(3, number.value.toString().length) + "ch")

const onload = () => {
    document.body.querySelectorAll("input[type=range]").forEach(range => {
        let number = range.parentElement.querySelector("input[type=number]");

        range.addEventListener("input", ()=>{
            number.value = range.value;

            numWidth(number);
        });
    });

    document.body.querySelectorAll("input[type=number]").forEach(number => {
        let range = number.parentElement.querySelector("input[type=range]");

        number.addEventListener("input", () => numWidth(number));

        number.addEventListener("change", () => {
            range.value = number.value;
            range.dispatchEvent(new Event('change'));
        });

        numWidth(number);
    });
};

document.addEventListener("DOMContentLoaded", onload);

document.addEventListener("htmx:load", e => e.detail.elt.id === "controls" && onload());
