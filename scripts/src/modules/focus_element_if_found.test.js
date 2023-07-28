/**
 * @jest-environment jsdom
 */

import focus_element_if_found from "./focus_element_if_found";

test("handles various inputs", () => {
    document.body.innerHTML = `
    <div class="tna-form__error-summary" role="alert" id="analytics-error-message">
       <h2>There is a problem.</h2>
       <p>Check the highlighted fields below.</p>
    </div>
    `;

    expect(focus_element_if_found("tna-form__error-summary")).toBe(true);
    expect(focus_element_if_found("non-existent-class")).toBe(false);
    expect(focus_element_if_found("")).toBe(false);
    expect(focus_element_if_found()).toBe(false);
});

test("updates the DOM as expected", () => {
    document.body.innerHTML = `
    <div class="tna-form__error-summary" role="alert" id="error-message">
       <h2>There is a problem.</h2>
       <p>Check the highlighted fields below.</p>
    </div>
    `;

    expect(focus_element_if_found("tna-form__error-summary")).toBe(true);
    expect(
        document
            .getElementsByClassName("tna-form__error-summary")[0]
            .getAttribute("tabindex"),
    ).toBe("-1");
    expect(document.activeElement.getAttribute("id")).toBe("error-message");
});
