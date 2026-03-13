console.log("script.js loaded");
let lastScrollTop = 0
const delta = 5
const navbar = document.querySelector(".navbar")
const navbarHeight = navbar.offsetHeight

window.addEventListener("scroll", () => {

    const scrollTop = window.pageYOffset

    // 忽略小滚动
    if (Math.abs(lastScrollTop - scrollTop) <= delta) return

    // 向下滚
    if (scrollTop > lastScrollTop && scrollTop > navbarHeight) {
        navbar.classList.add("navbar-hidden")
    }
    else {
        // 向上滚
        navbar.classList.remove("navbar-hidden")
    }

    lastScrollTop = scrollTop
})