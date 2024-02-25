import "../global.scss";
import "./style.scss";
import { elementInSight } from "./utils";

const scrollOffset = 100;
var lastScrollOffset = 0;

const section4HeaderPair = {
    "sec-main": "sh-main",
    "sec-pros": "sh-pros",
    "sec-makemoney": "sh-makemoney",
    "footer": "sh-footer",
}

function handleHeaderScroll(){
    const hideHeader = $(".section.no-header").toArray().some((el) => {
        const rect = el.getBoundingClientRect();

        return (
            0 <= rect.bottom + scrollOffset && rect.top - scrollOffset <= 0
        );
    });
    
    if (hideHeader){
        $("#header:not(.hidden)").addClass("hidden");
    }else{
        $("#header.hidden").removeClass("hidden");
    }
}


function handleHeaderSelected(){
    const el = $(".section").toArray().reverse().find((el) => elementInSight(el));
    if (el === undefined || el === null) return;

    const selectedItem = $("#navigator > .item.selected")[0];
    const newSelection = section4HeaderPair[el.id];

    if (newSelection !== null && newSelection != selectedItem?.id){
        selectedItem?.classList?.remove("selected");
        $(`#navigator > .item#${newSelection}`).addClass("selected");
    }
}

function handleTransitSlider(){
    const slider = $("#sec-transit > #slider")[0];
    const thumb = slider.querySelector("#thumb");

    const height = window.innerHeight;
    const rect = slider.getBoundingClientRect();
    const offset = rect.top + (rect.height / 2);

    if (0 <= offset && offset <= height){
        // @ts-ignore
        const transform = parseInt((offset / height) * 100, 10) - 50;
        
        // @ts-ignore
        thumb.style.transform = `translateX(${transform}%)`;
    }
}

function handleFunctionsScroll(){
    const status = elementInSight(document.getElementById("sec-functions"));

    if (status){
        $("#sec-functions:not(.visited)").addClass("visited");
    }else{
        $("#sec-functions.visited").removeClass("visited");
    }
}

$(function() {
    $("#navigator > .item").on("click", (ev) => {
        const el = Object.entries(section4HeaderPair).find((el) => el[1] == ev.target.id)[0];
        if (el === undefined || el === null) return;
        $('#navigator:not(.hidden)').addClass("hidden");
        document.getElementById(el).scrollIntoView();
    });

    $(".download-btn").on("click", (ev) => {
        document.getElementById("sec-download").scrollIntoView();
    });

    // $("#sec-pros #actions .item").on("click", (ev) => {
    //     $('#sec-pros #actions .item.selected').removeClass("selected");
    //     ev.target.classList.add("selected");
    // });

    // $("#phone-viewer").on("click", (ev) => handleFunctionsSlider());

    $("#burger").on("click", (ev) => {
        $('#navigator').toggleClass("hidden");
    });

    $(window).on("scroll", (ev) => {
        lastScrollOffset = window.scrollY;
        
        handleHeaderScroll();
        handleHeaderSelected();
        handleTransitSlider();
        handleFunctionsScroll();
    });
});
