
export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export function elementInSight(el){
    const elementTop = el.getBoundingClientRect().top;
    return (
        elementTop <= 
        ((window.innerHeight || document.documentElement.clientHeight) - 300)
    );
};
