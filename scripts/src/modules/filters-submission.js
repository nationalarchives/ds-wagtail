import debounce from "./debounce";

class FiltersSubmission {
    constructor(node) {
        this.node = node;
        this.submitButton = node.querySelector("[data-js-submit]");
        this.submitButton.remove();
        this.dateField = this.node.querySelector("[data-js-date]");

        this.eventTypeFields = this.node.querySelectorAll(
            "[data-js-event-type]",
        );
        const eventTypeChecked = this.node.querySelector(
            "[data-js-event-type]:checked",
        );
        this.onlineField = this.node.querySelector("[data-js-online]");
        this.familyField = this.node.querySelector("[data-js-family]");
        // When the page loads normally, the initial values are based on
        // the current field values
        this.dateValue = this.dateField.value;
        this.eventTypeValue = eventTypeChecked ? eventTypeChecked.value : null;
        this.onlineValue = this.onlineField.checked;
        this.familyValue = this.familyField.checked;
        this.addEventListeners();
    }

    addEventListeners() {
        this.dateField.addEventListener(
            "change",
            debounce((e) => {
                this.dateValue = e.target.value;
                this.reloadEvents();
            }, 200),
        );

        this.eventTypeFields.forEach((field) => {
            field.addEventListener(
                "change",
                debounce((e) => {
                    this.eventTypeValue = e.target.value;
                    this.reloadEvents();
                }, 200),
            );
        });

        this.onlineField.addEventListener(
            "change",
            debounce((e) => {
                this.onlineValue = e.target.checked;
                this.reloadEvents();
            }, 200),
        );

        this.familyField.addEventListener(
            "change",
            debounce((e) => {
                this.familyValue = e.target.checked;
                this.reloadEvents();
            }, 200),
        );

        window.addEventListener(
            "popstate",
            debounce((e) => {
                this.updateFields(document.location);
                this.reloadEvents(false);
            }, 200),
        );
    }

    buildURL() {
        let url = new URL(window.location.href.split("?")[0]);

        if (this.dateValue) {
            url.searchParams.append("date", this.dateValue);
        }
        if (this.eventTypeValue) {
            url.searchParams.append("event_type", this.eventTypeValue);
        }
        if (this.onlineValue) {
            url.searchParams.append("is_online_event", "on");
        }
        if (this.familyValue) {
            url.searchParams.append("family_friendly", "on");
        }
        return url.toString();
    }

    // when the back or forward buttons is used for a JavaScript change,
    // we need to update the field values based on the URL
    updateFields(url) {
        let urlParams = new URLSearchParams(url.search);
        this.dateValue = urlParams.get("date");
        this.dateField.value = this.dateValue;
        this.eventValue = urlParams.get("event_type");
        this.eventTypeFields.forEach((field) => {
            field.checked = field.value === this.eventValue;
        });
        this.onlineValue = urlParams.get("is_online_event");
        this.onlineField.checked = this.onlineValue === "on";
        this.familyValue = urlParams.get("family_friendly");
        this.familyField.checked = this.familyValue === "on";
    }

    async reloadEvents(updateURL = true) {
        let newURL = this.buildURL();
        fetch(newURL, {
            method: "GET",
            headers: {
                "JS-Request": true,
            },
        })
            .then((response) => response.text())
            .then((value) => {
                document.querySelector("[data-js-whatson-listing]").innerHTML =
                    value;
                if (updateURL) {
                    history.pushState({}, "", newURL);
                }
            });
    }
}

export default FiltersSubmission;
