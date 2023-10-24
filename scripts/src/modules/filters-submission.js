class FiltersSubmission {
    constructor(node) {
        this.node = node;
        this.dateField = this.node.querySelector("[data-js-date]");
        this.dateValue = this.dateField.value;
        this.eventTypeFields = this.node.querySelectorAll(
            "[data-js-event-type]",
        );
        const eventTypeChecked = this.node.querySelector(
            "[data-js-event-type]:checked",
        );
        this.eventTypeValue = eventTypeChecked ? eventTypeChecked.value : null;
        this.onlineField = this.node.querySelector("[data-js-online]");
        this.onlineValue = this.onlineField.checked;
        this.familyField = this.node.querySelector("[data-js-family]");
        this.familyValue = this.familyField.checked;
        this.addEventListeners();
    }

    addEventListeners() {
        this.dateField.addEventListener("change", (e) => {
            this.dateValue = e.target.value;
            this.reloadEvents();
        });

        this.eventTypeFields.forEach((field) => {
            field.addEventListener("change", (e) => {
                this.eventTypeValue = e.target.value;
                this.reloadEvents();
            });
        });

        this.onlineField.addEventListener("change", (e) => {
            this.onlineValue = e.target.checked;
            this.reloadEvents();
        });

        this.familyField.addEventListener("change", (e) => {
            this.familyValue = e.target.checked;
            this.reloadEvents();
        });
    }

    buildURL() {
        let url = window.location.href.split("?")[0];
        let first = true;
        if (this.dateValue) {
            url += first ? `?` : `&`;
            url += `date=${this.dateValue}`;
            first = false;
        }
        if (this.eventTypeValue) {
            url += first ? `?` : `&`;
            url += `event_type=${this.eventTypeValue}`;
            first = false;
        }
        if (this.onlineValue) {
            url += first ? `?` : `&`;
            url += `is_online_event=on`;
            first = false;
        }
        if (this.familyValue) {
            url += first ? `?` : `&`;
            url += `family_friendly=on`;
            first = false;
        }
        return url;
    }

    async reloadEvents() {
        fetch(this.buildURL(), {
            method: "GET",
            headers: {
                "JS-Request": true,
            },
        })
            .then((response) => response.text())
            .then((value) => {
                document.querySelector("[data-js-whatson-listing]").innerHTML =
                    value;
            });
    }
}

export default FiltersSubmission;
