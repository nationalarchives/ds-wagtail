import ImageGallery from "./modules/image-gallery";
import RecordMatters from "./modules/record-matter";

const imageGallery = document.querySelector(".transcription");

if (imageGallery) {
    new ImageGallery(imageGallery);
}

const recordMatters = document.querySelector(".record-matters");

if (recordMatters) {
    new RecordMatters(recordMatters);
}
