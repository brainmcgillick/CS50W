if (!localStorage.getItem("counter")) {
    localStorage.setItem("counter", 0);
}

function count() {
    let counter = localStorage.getItem("counter");
    counter ++;
    document.querySelector("h1").innerHTML = counter;
    localStorage.setItem("counter", counter);
}

function reset() {
    counter = 0;
    document.querySelector("h1").innerHTML = counter;
    localStorage.setItem("counter", counter);
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelector("h1").innerHTML = localStorage.getItem("counter");
    document.querySelector("#count").onclick = count;
    document.querySelector("#reset").onclick = reset;
});