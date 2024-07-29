window.htmx = require('htmx.org').default;
require('htmx-ext-sse');

const onload = () => {
    document.body.querySelectorAll('.control-container').forEach(ctrl => {
        // all inputs and fast checkboxes, except regular checkboxes
        const inputs = Array.from(ctrl.querySelectorAll('input'))
            .filter(e => !(e.type === 'checkbox' && e.name !== 'fast'));

        const fast = inputs.find(e => e.type === 'checkbox' && e.name === 'fast');
        const number = inputs.find(e => e.type === 'number');
        const range = inputs.find(e => e.type === 'range');

        if (number && range) {
            range.addEventListener('input', () => { number.value = range.value; });

            // so we can access it later
            number.onchange = () => {
                range.value = number.value;
                range.dispatchEvent(new Event(fast.checked ? 'input' : 'change'));
            };
        }

        // at least fast and one other
        if (fast && inputs.length > 1) {
            fast.addEventListener('change', () => {
                for (const inp of inputs) {
                    if (inp.type === 'number') {
                        // swap onchange and oninput
                        [inp.onchange, inp.oninput] = [inp.oninput, inp.onchange];
                    } else if (inp.name !== 'fast') {
                        inp.setAttribute('hx-trigger', fast.checked ? 'input throttle:10ms' : 'change');
                        htmx.process(inp);
                    }
                }
            });
        }
    });
};

const MAX_ELEMENTS = 500;
document.addEventListener('DOMContentLoaded', () => {
    const logs = document.getElementById('logs');

    logs.addEventListener('htmx:afterSwap', () => {
        if (logs.childElementCount >= MAX_ELEMENTS)
            logs.removeChild(logs.children[0]);
    });

    onload();
});

document.addEventListener('htmx:load', e => e.detail.elt.id === 'controls' && onload());
