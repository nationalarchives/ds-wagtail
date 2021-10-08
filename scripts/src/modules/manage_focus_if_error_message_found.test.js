/**
 * @jest-environment jsdom
 */

import manage_focus_if_error_message_found from "./manage_focus_if_error_message_found";

test('handles various inputs', () => {

    document.body.innerHTML = `
    <div class="tna-form__error-summary" role="alert" id="analytics-error-message">
       <h2>There is a problem.</h2>
       <p>Check the highlighted fields below.</p>
    </div>
    `;

    expect(manage_focus_if_error_message_found('tna-form__error-summary')).toBe(true);
    expect(manage_focus_if_error_message_found('non-existent-class')).toBe(false);
    expect(manage_focus_if_error_message_found('')).toBe(false);
    expect(manage_focus_if_error_message_found()).toBe(false);
});

test('updates the DOM as expected', () => {

    document.body.innerHTML = `
    <div class="tna-form__error-summary" role="alert" id="error-message">
       <h2>There is a problem.</h2>
       <p>Check the highlighted fields below.</p>
    </div>
    `;

    expect(manage_focus_if_error_message_found('tna-form__error-summary')).toBe(true);
    expect(document.getElementsByClassName('tna-form__error-summary')[0].getAttribute('tabindex')).toBe('-1');
    expect(document.activeElement.getAttribute('id')).toBe('error-message');
});