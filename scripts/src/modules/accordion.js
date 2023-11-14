class Accordion {
    static selector() {
        return "[data-accordion]";
    }

    constructor(node) {
        this.accordion = node;
        this.button = this.accordion.querySelector("[data-accordion-button]");
        this.content = this.accordion.querySelector("[data-accordion-content]");
        this.accordion.classList.add("is-closed");
        this.bindEvents();
    }

    bindEvents() {
        this.button.addEventListener("click", (e) => {
            e.preventDefault();
            let open = this.accordion.classList.contains("is-open");

            if (open) {
                this.button.setAttribute("aria-expanded", "false");
                this.content.setAttribute("aria-hidden", "true");
                this.accordion.classList.remove("is-open");
                this.accordion.classList.add("is-closed");
                open = false;
            } else {
                this.button.setAttribute("aria-expanded", "true");
                this.content.setAttribute("aria-hidden", "false");
                this.accordion.classList.add("is-open");
                this.accordion.classList.remove("is-closed");
                open = true;
            }
        });

        this.button.addEventListener("focus", () => {
            this.button.setAttribute("aria-selected", "true");
        });

        this.button.addEventListener("blur", () => {
            this.button.setAttribute("aria-selected", "false");
        });
    }
}

export default Accordion;
