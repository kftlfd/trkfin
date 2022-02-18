const navbar = document.querySelector("[data-navbar]");
const navSidebar = document.querySelector("[data-nav-sidebar]")
const navSidebarBg = document.querySelector("[data-nav-sidebar-bg]")

// reveals (only if page is not scrolled down)
let toReveal = document.querySelectorAll("[data-reveal]");
let body = document.querySelector('body')
if (body.getBoundingClientRect().y >= 0) {
  toReveal.forEach(x => x.classList.add("reveal-done"));
} else {
  toReveal.forEach(x => x.classList.remove("reveal"));
}

// navbar open-close
function toggleNavSidebar() {
  navSidebar.classList.toggle('open');
  navSidebarBg.classList.toggle('open');
}
let toggles = document.querySelectorAll("[data-nav-sidebar-toggle]")
toggles.forEach(x => x.addEventListener("click", toggleNavSidebar));

// navbar change style on scroll
function navbarScroll() {
  if (window.scrollY === 0) {
    navbar.classList.remove('scroll')
  } else {
    navbar.classList.add('scroll')
  }
}
navbarScroll()
window.addEventListener("scroll", navbarScroll);
