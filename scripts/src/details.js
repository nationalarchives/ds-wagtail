import {manage_details_element} from './modules/manage_details_element'

// Prevent the details element from closing at 1200px or above
const summary_element = document.querySelector('#js-hierarchy-global summary');

summary_element.addEventListener('click', e => {

    if(window.innerWidth < 1200) {
        return;
    }
    e.preventDefault();
});

// Register event handlers
document.addEventListener("DOMContentLoaded", () => {
    manage_details_element();
});

window.addEventListener("resize", () => {
    manage_details_element();
});

