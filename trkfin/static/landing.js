const navbar = document.querySelector("[data-navbar]");
const navSidebar = document.querySelector("[data-nav-sidebar]")
const navSidebarBg = document.querySelector("[data-nav-sidebar-bg]")

// reveals
let toReveal = document.querySelectorAll(".reveal");
if (window.scrollY > 0) {
  toReveal.forEach(x => x.classList.remove("reveal"));
  } else {
  toReveal.forEach(x => x.classList.add("reveal-done"));
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
  if (window.scrollY > 0) {
    navbar.classList.add('scroll')
  } else {
    navbar.classList.remove('scroll')
  }
}
navbarScroll()
window.addEventListener("scroll", navbarScroll);
