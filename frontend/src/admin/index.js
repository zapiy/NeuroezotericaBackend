// @ts-nocheck
import "../global.scss";
import "./style.scss";

function createElement(tag, {children, ...args} = {}){
    let el = Object.assign(document.createElement(tag), args);
    if (children) children.forEach((c) => el.appendChild(c));
    return el;
}

function closeModal(){
    $(".modal-overflow").addClass("hidden");
    $(".modal-overflow .modal").remove();
}

function showModal({title, content} = {}){
    $(".modal-overflow").removeClass("hidden");
    
    $(".modal-overflow").append(
        createElement("div", {
            classList: ["modal"],
            onclick: (ev) => ev.stopPropagation(),
            children: [
                createElement("div", {
                    id: "header",
                    children: [
                        createElement("div", {
                            id: "side",
                            children: [
                                createElement("img", {
                                    id: "logo",
                                    src: "/static/res/logo.svg"
                                }),
                                createElement("span", {
                                    id: "title",
                                    innerText: title ?? "Ошибка",
                                })
                            ]
                        }),
                        createElement("span", {
                            id: "close",
                            classList: ["material-symbols-outlined"],
                            innerText: "close",
                            onclick: (ev) => closeModal()
                        })
                    ]
                }),
                createElement("span", {
                    id: "content",
                    innerText: content ?? "Не указано!",
                })
            ]
        })
    );
}

$(function() {
    const cookies = (
        document.cookie === "" ? {} 
        : Object.fromEntries(document.cookie.split("; ").map(el => el.split('=')))
    );

    try {
        const url = new URL(window.location.href);
        if (url.searchParams.has("modal")){
            const modal = JSON.parse(url.searchParams.get('modal'));
            url.searchParams.delete("modal");
            showModal(modal);
            window.history.replaceState(null, null, url);
        }
    } catch {}
    
    $("#header #switch").on("click", (ev) => $('#header').toggleClass("show-nav"));
    $("#header #navigator").on("click", (ev) => $('#header').removeClass("show-nav"));
    $("#header #navigator > .inner").on("click", (ev) => ev.stopPropagation());

    $(".modal-overflow").on("click", (ev) => closeModal());

    $(".image-input .preview").on("click", 
        (ev) => ev.target.closest(".image-input").querySelector('.form-control').click());

    $(".image-input > .form-control").on("change", (ev) => {
        const preview = ev.target.closest(".image-input").querySelector('.preview');
        if (ev.target.files){
            const file = ev.target.files[0];

            if (file) {
                if (file.name.match(/\.(jpg|jpeg|png)$/)){
                    preview.src = URL.createObjectURL(file);
                } else {
                    alert('Не поддерживаемый тип файла!');
                }   
            } 
        } 
    });

    $("[a-linked]").on("click", (ev) => {
        ev.stopPropagation();
        const link = ev.target.closest("[a-linked]").getAttribute("a-linked");
        if (ev.target.hasAttribute("a-blank")) window.open(link);
        else window.location.assign(link);
    });

    $("button[type~='submit']").on("click", (ev) => {
        ev.preventDefault();
        ev.stopPropagation();

        const form = ev.target.closest("form");
        const method = form.getAttribute("method")?.toUpperCase() ?? "GET";

        if (["GET", "POST"].includes(method)){
            form.submit();
            return false;
        }

        form.dispatchEvent(new CustomEvent("custom-submit", {
            detail: {
                action: ev.target.getAttribute("action")
            }
        }));

        return false;
    });

    function onSubmit (ev) {
        ev.stopPropagation();
        var method = ev.target.getAttribute("method")?.toUpperCase() ?? "GET";
        if (!["GET", "POST", "POSTM", "DELETE", "PUT"].includes(method)){
            console.log("Form unknown method:", method);
            ev.preventDefault();
            return false;
        }

        if (method == "GET" || method == "POST") return true;
        else if (method == "POSTM"){
            method = "POST";
        }
        ev.preventDefault();

        (async function(){
            const location = ev.target.getAttribute("action") ?? window.location.pathname;
            const multipart = ev.target.getAttribute("enctype") == "multipart/form-data";
            const action = ev.detail?.action;

            const data = (
                multipart
                ? new FormData(ev.target)
                : new URLSearchParams(Object.fromEntries(new FormData(ev.target).entries()))
            );

            // try{
                const resp = await fetch(
                    location, {
                    method: method,
                    headers: {
                        'X-CSRF-TOKEN': cookies["admin_csrf_token"] ?? "none",
                        'X-ACTION': action ?? "default",
                    },
                    mode: "same-origin",
                    referrerPolicy: "same-origin",
                    body: data
                });
                
                if (resp.headers.get("Content-Type") !== "application/json"){
                    return window.location.reload();
                }
                
                const json = await resp.json();

                if (json == undefined) return;

                let redirect = json["redirect"];
                const reload = json["reload"];
                const modal = json["modal"];

                if (redirect){
                    if (modal){
                        redirect = new URL(
                            redirect.startsWith("http")
                            ? redirect
                            : window.location.origin + redirect
                        );
                        redirect.searchParams.set("modal", JSON.stringify(modal));
                    }
                    return window.location.assign(redirect);
                }
                else if (reload === true && modal){
                    const href = new URL(window.location.href);
                    href.searchParams.set("modal", JSON.stringify(modal));
                    return window.location.assign(href);
                }
                else if (modal){
                    return showModal(modal);
                }
                window.location.reload();
            // }
            // catch(err){
            //     console.error(err);
            // }
        })()

        return false;
    }

    $("form").on("submit", onSubmit);
    $("form").on("custom-submit", onSubmit);
});
