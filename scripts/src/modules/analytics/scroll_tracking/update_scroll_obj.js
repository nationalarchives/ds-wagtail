import get_scroll_percentage from "./get_scroll_percentage";

let highestPercentageReached = get_scroll_percentage();

const update_scroll_obj = (currentScrollPercentageIncrement, scrollObj) => {
    if (currentScrollPercentageIncrement > highestPercentageReached) {
        highestPercentageReached = currentScrollPercentageIncrement;
        scrollObj.highestScrollPercentage = highestPercentageReached;
        sessionStorage.setItem(window.location.href, highestPercentageReached);
    } else {
        scrollObj.highestScrollPercentage = highestPercentageReached;
    }
    return scrollObj;
};

export default update_scroll_obj;
