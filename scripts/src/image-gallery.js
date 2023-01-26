import TabManager from './modules/tab_manager';

class ImageGallery {
    constructor(galleryNode) {
        this.node = galleryNode;
        this.closeButton = this.node.querySelector('#closeButton');
        this.openButton = this.node.querySelector('#showButton');
        this.transcriptionContentNode = this.node.querySelectorAll("[id^='item-']");
        this.transcriptionPreview = this.node.querySelector('.transcription__preview');
        this.tablist = document.querySelectorAll('[role=tablist].automatic');
        this.setUp();
    }

    setUp() {
        // Event listeners
        this.closeButton.addEventListener('click', (e) =>{ 
            e.preventDefault();
            for (let i= 0; i < this.transcriptionContentNode.length; i++) {
                this.hide(this.transcriptionContentNode[i]);
            }
            this.show(this.transcriptionPreview)
            this.show(this.openButton);
            this.hide(this.closeButton);
        })
        this.openButton.addEventListener('click', (e) =>{
            e.preventDefault();
            for (let i= 0; i < this.transcriptionContentNode.length; i++) {
                this.show(this.transcriptionContentNode[i]);
            }            
            this.hide(this.transcriptionPreview);
            this.hide(this.openButton);
            this.show(this.closeButton);
        })

        // tabs
        for (var i = 0; i < this.tablist.length; i++) {
            new TabManager(this.tablist[i]);
        }
    }

    show(node) {
        node.classList.remove('hidden');
    }

    hide(node){
        node.classList.add('hidden');
    }

}


const imageGallery = document.querySelector('.transcription')
if (imageGallery) {
    new ImageGallery(imageGallery);
}

export default ImageGallery;