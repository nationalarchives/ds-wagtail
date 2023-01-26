import TabManager from './modules/tab_manager';


const tablists = document.querySelectorAll('[role=tablist].automatic');
for (var i = 0; i < tablists.length; i++) {
  new TabManager(tablists[i]);
}

//variables
    const previewImage = document.getElementById("previewImage");
    const showMoreButton = document.getElementById("showMoreButton");
    const transcript = document.getElementById("transcript-element");
    const closebutton = document.getElementById("closebutton");
    
    //if js enabled show relevant content
    transcript.style.display = "none";
    previewImage.style.display = "block";
    showMoreButton.style.display = "block";
    
    closebutton.style.display = "block";
    closebutton.style.padding = "1em";
    closebutton.style.color = "#fbd709";
    
    //actions
    showMoreButton.addEventListener("click", (event) => {
        //button clicked
        event.preventDefault();
        transcript.style.display = "block";
        previewImage.style.display = "none";
        showMoreButton.style.display = "none";
    
    })
    
    closebutton.addEventListener("click", (event) => {
        //close button
        event.preventDefault();
        transcript.style.display = "none";
        previewImage.style.display = "block";
        showMoreButton.style.display = "block";
    
    })