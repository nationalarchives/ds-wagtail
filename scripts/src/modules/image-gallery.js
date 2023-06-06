import TabManager from "./tab_manager";

class ImageGallery {
    constructor(galleryNode) {
        this.node = galleryNode;
        this.nonJsNodes = this.node.querySelectorAll(".transcription__text");
        this.closeButton = this.node.querySelector("#closeButton");
        this.openButton = this.node.querySelector("#showButton");
        this.transcriptionContentNode =
            this.node.querySelectorAll("[id^='item-']");
        this.transcriptionPreview = this.node.querySelector(
            ".transcription__preview"
        );
        this.tabList = this.node.querySelectorAll("[role=tablist]");
        this.setUp();
    }

    setUp() {
        // Hide non-js nodes
        for (let i = 0; i < this.nonJsNodes.length; i++) {
            this.hide(this.nonJsNodes[i]);
        }
        // Show JS nodes
        for (let i = 0; i < this.transcriptionContentNode.length; i++) {
            this.hide(this.transcriptionContentNode[i]);
        }
        this.show(this.openButton);
        this.show(this.transcriptionPreview);

        // Event listeners
        this.closeButton.addEventListener("click", (e) => {
            e.preventDefault();
            for (let i = 0; i < this.transcriptionContentNode.length; i++) {
                this.hide(this.transcriptionContentNode[i]);
            }
            this.show(this.transcriptionPreview);
            this.show(this.openButton);
            this.openButton.setAttribute("aria-expanded", "false");
            this.hide(this.closeButton);
            this.openButton.scrollIntoView({
                behavior: "auto",
                block: "center",
                inline: "center",
            });
        });
        this.openButton.addEventListener("click", (e) => {
            e.preventDefault();
            for (let i = 0; i < this.transcriptionContentNode.length; i++) {
                this.show(this.transcriptionContentNode[i]);
            }
            this.hide(this.transcriptionPreview);
            this.hide(this.openButton);
            this.openButton.setAttribute("aria-expanded", "true");
            this.show(this.closeButton);
            this.transcriptionContentNode[0].scrollIntoView();
        });

        // tabs
        for (var i = 0; i < this.tabList.length; i++) {
            new TabManager(this.tabList[i]);
            this.show(this.tabList[i]);
        }
    }

    show(node) {
        node.classList.remove("hidden");
    }

    hide(node) {
        node.classList.add("hidden");
    }
}

export default ImageGallery;
