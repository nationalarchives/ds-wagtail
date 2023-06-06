import push_to_data_layer from "./analytics/push_to_data_layer";
class RecordMatters {
    constructor(node) {
        this.node = node;
        this.readMoreButton = this.node.querySelector("#readMoreButton");
        this.readLessButton = this.node.querySelector("#readLessButton");
        this.readMoreContent = this.node.querySelector("#readMoreContent");
        this.readLessContent = this.node.querySelector("#readLessContent");
        this.setUp();
    }

    setUp() {

        // set-up from the non-js version
        this.hide(this.readMoreContent);
        this.show(this.readLessContent);
        this.show(this.readLessButton);

        this.readMoreButton.addEventListener("click", (e) => {
            e.preventDefault();
            this.show(this.readMoreContent);
            this.hide(this.readLessContent);

            push_to_data_layer({
                "event": "Expand accordion",
                "data-component-name": e.target.getAttribute("data-component-name"),
                "data-link-type": e.target.getAttribute("data-link-type"),
                "data-link": e.target.getAttribute("data-link")
            })
        })

        this.readLessButton.addEventListener("click", (e) => {
            e.preventDefault();
            this.show(this.readLessContent);
            this.hide(this.readMoreContent);

            push_to_data_layer({
                "event": "Collapse accordion",
                "data-component-name": e.target.getAttribute("data-component-name"),
                "data-link-type": e.target.getAttribute("data-link-type"),
                "data-link": e.target.getAttribute("data-link")
            })
        })
    }

    show(node) {
        node.classList.remove('hidden');
    }

    hide(node) {
        node.classList.add('hidden');
    }
}

export default RecordMatters;