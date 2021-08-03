const items = document.querySelectorAll('.image-browse__listing a');

Array.prototype.forEach.call(items, function (item, index) {
    item.dataset.link = index;
});
