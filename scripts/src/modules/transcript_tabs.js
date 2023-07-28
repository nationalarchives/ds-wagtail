import TabManager from "./tab_manager";

class TranscriptTabs {
    constructor(transcriptNode) {
        this.node = transcriptNode;
        this.nonJsNodes = this.node.querySelectorAll(".transcription__text");
        this.transcriptionContentNode =
            this.node.querySelectorAll("[id^='item-']");
        this.tabList = this.node.querySelectorAll('[role="tablist"]');
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

        //Hide transcription with JS enabled
        this.hide(this.node);

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

export default TranscriptTabs;
