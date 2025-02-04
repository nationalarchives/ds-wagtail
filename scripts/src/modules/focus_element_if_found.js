/**
 * This module manages focus in the event that
 * a given element is found to be on the page
 *
 * @param {string} needle_class - a class on the element we are looking for
 */

const focus_element_if_found = (needle_class = "") => {
    const needle_elements = document.getElementsByClassName(needle_class);

    if (needle_elements.length) {
        needle_elements[0].setAttribute("tabindex", "-1");
        needle_elements[0].focus();
        return true;
    } else {
        return false;
    }
};

export default focus_element_if_found;
