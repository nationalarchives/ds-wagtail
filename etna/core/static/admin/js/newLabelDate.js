document.addEventListener("DOMContentLoaded", function () {
    var label = document.getElementById("panel-child-promote-child-new_label-child-newly_published_at-label");
    if (label) {
        label.innerHTML = "New label current expiry date:";
    }
    var element = document.querySelector('[aria-labelledby="panel-child-promote-child-new_label-child-newly_published_at-label"]');
    if (element) {
        if (element.innerHTML.replace(/\s/g, '') != "None") {
            var newDate = new Date(element.innerHTML);
            newDate.setDate(newDate.getDate() + 21);
            if (newDate >= new Date().setHours(0, 0, 0, 0)) {
                element.innerHTML = newDate.toLocaleDateString('en-GB');
            } else {
                element.innerHTML = "Expired on " + newDate.toLocaleDateString('en-GB');
            }
        } else {
            element.innerHTML = "N/A";
        }
    }
});