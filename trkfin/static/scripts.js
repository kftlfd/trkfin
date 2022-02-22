// nav-sidebar open-close
const navSidebar = document.querySelector("[data-nav-sidebar]")
const navSidebarBg = document.querySelector("[data-nav-sidebar-bg]")
function toggleNavSidebar() {
  navSidebar.classList.toggle('open');
  navSidebarBg.classList.toggle('open');
}
let toggles = document.querySelectorAll("[data-nav-sidebar-toggle]")
toggles.forEach(x => x.addEventListener("click", toggleNavSidebar));


// show and hide alert
const alert = document.querySelector("[data-alert]")
if (alert) {
  alert.classList.add("alert-show")
  function alertHide() {
    alert.classList.remove("alert-show")
  }
  const alertClose = document.querySelector("[data-alert-close]")
  alertClose.addEventListener("click", alertHide);
  setTimeout(alertHide, 10000)
}
