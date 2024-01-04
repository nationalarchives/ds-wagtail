class UniversalViewer {
    static selector() {
        return "[data-uv]";
    }

    constructor(node) {
        this.node = node;
        this.data = this.node.getAttribute('data-id');

        this.bindEvents();
    }

    bindEvents() {
        const urlAdapter = new UV.IIIFURLAdapter();

        const data = urlAdapter.getInitialData({
            manifest: this.data,
        });
        
        this.node = UV.init("uv", data);
        urlAdapter.bindTo(this.node);
    }
}

export default UniversalViewer;
