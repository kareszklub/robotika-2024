/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.html"],
    theme: {
        extend: {},
    },
    daisyui: {
        themes: ["night"],
    },
    plugins: [
        require("@tailwindcss/typography"),
        require("daisyui"),
    ],
}
