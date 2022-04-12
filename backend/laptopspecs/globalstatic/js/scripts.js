// Source: https://github.com/coding-in-public/light-dark/tree/main

const themeBtn = document.querySelector('.theme');

function getCurrentTheme(){
    let theme = window.matchMedia('(prefers-color-scheme: dark)')
        .matches ? "dark" : "light";
    
        localStorage.getItem('ltxp.theme') ? 
        theme = localStorage.getItem('ltxp.theme') : null;

    return theme;
}

function loadTheme(theme){
    const root = document.querySelector(':root');
    if (theme === "light"){
        themeBtn.innerHTML = `<img src=${sunset_img} alt="Sunset Image">`;
    } else {
        themeBtn.innerHTML = `<img src=${sunrise_img} alt="Sunrise Image">`;
    }

    root.setAttribute('color-theme', `${theme}`);
    localStorage.setItem('ltxp.theme', `${theme}`);
}

themeBtn.addEventListener('click', () => {
    let theme = getCurrentTheme();
    theme = theme === "dark" ? "light" : "dark";
    loadTheme(theme);
})

window.addEventListener('DOMContentLoaded', () => {
    loadTheme(getCurrentTheme());
})