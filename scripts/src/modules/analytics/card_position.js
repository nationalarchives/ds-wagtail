const add_analytics_data_card_position = (selector) => {
    const items = document.querySelectorAll(selector);

    Array.prototype.forEach.call(items, (item, index) => {
        item.dataset.cardPosition = index;
    });
};

export default add_analytics_data_card_position;
