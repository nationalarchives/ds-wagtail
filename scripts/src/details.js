import manage_details_element from './modules/manage_details_element'

const summary_element = document.querySelector('#js-hierarchy-global summary');

summary_element.addEventListener('click', e => {

    if (window.innerWidth < 1200) {
        return;
    }
    e.preventDefault();
});

document.addEventListener("DOMContentLoaded", () => {
    manage_details_element();
});

window.addEventListener("resize", () => {
    manage_details_element();
});

