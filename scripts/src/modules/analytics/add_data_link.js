const add_data_link = (selector) => {
    const items = document.querySelectorAll(selector);

    Array.prototype.forEach.call(items, (item, index) => {
        item.dataset.link = index;
    });
};

export default add_data_link;
