document.addEventListener("DOMContentLoaded", function () {
    var label = document.getElementById("panel-child-promote-child-new_label-child-newly_published_at-label");
    label.innerHTML = "New label current expiry date:";
    var element = document.querySelector('[aria-labelledby="panel-child-promote-child-new_label-child-newly_published_at-label"]');
    if (element.innerHTML.replace(/\s/g, '') != "None") {
        var newDate = new Date(element.innerHTML);
        newDate.setDate(newDate.getDate() + 21);
        element.innerHTML = newDate.toLocaleDateString('en-GB');
    } else {
        element.innerHTML = "N/A";
    }
});