// This JS handles the expand/collapse of the details/summary list element across different screen sizes.

// Set the details element as open at 1200px or above
export const manage_details_element = () => {

    const details_element = document.getElementById('js-hierarchy-global'),
        summary_element = document.querySelector('#js-hierarchy-global summary');

    if (!!details_element) {

        if (window.innerWidth < 1200) {
            details_element.removeAttribute('open');
            summary_element.setAttribute('tabindex', '0');
        } else {
            details_element.setAttribute('open', '');
            summary_element.setAttribute('tabindex', '-1');
        }
    }
};