window.htmx = require('htmx.org').default;
require('htmx-ext-sse');

const onload = () => {
    document.body.querySelectorAll('input[type=range]').forEach(range => {
        let number = range.parentElement.parentElement.querySelector('input[type=number]');

        range.addEventListener('input', () => {
            number.value = range.value;
        });
    });

    document.body.querySelectorAll('input[type=number]').forEach(number => {
        let range = number.parentElement.querySelector('input[type=range]');

        number.addEventListener('change', () => {
            range.value = number.value;
            range.dispatchEvent(new Event('change'));
        });
    });

    document.body.querySelectorAll('input[type=checkbox][name=fast]').forEach(fast => {
        let inputs = Array.from(fast.parentElement.querySelectorAll('input').values())
            .filter(e => e != fast && e.type != 'checkbox');

        if (inputs.length == 0)
            return;

        fast.addEventListener('change', () => {
            for (const inp of inputs)
                inp.setAttribute('hx-trigger', fast.checked ? 'input throttle:10ms' : 'change');

            htmx.process(fast.parentElement);
        });
    });
};

document.addEventListener('DOMContentLoaded', onload);

document.addEventListener('htmx:load', e => e.detail.elt.id === 'controls' && onload());
