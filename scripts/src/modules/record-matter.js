
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
        this.readMoreButton.addEventListener("click", (e) => {
            e.preventDefault();
            this.show(this.readMoreContent);
            this.hide(this.readLessContent);
        })

        this.readLessButton.addEventListener("click", (e) => {
            e.preventDefault();
            this.show(this.readLessContent);
            this.hide(this.readMoreContent);
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