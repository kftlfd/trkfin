// reveal (only if page is not scrolled down)
const body = document.querySelector('body');
let slideSections = document.querySelectorAll(".slide-reveal");
if (body.getBoundingClientRect().y >= 0) {
  body.classList.add("reveal");
  function slideReveal() {
    slideSections.forEach(x => {
      if (x.getBoundingClientRect().y < window.screen.height + 50) {
        x.classList.add("done")
      }
    });
  }
  slideReveal()
  window.addEventListener("scroll", slideReveal);
} else {
  body.classList.remove("hide");
  slideSections.forEach(x => x.classList.remove("slide-reveal"));
}


// navbar remove bg if scrolled to top of page
const navbar = document.querySelector("[data-navbar]");
function navbarRemoveBg() {
  if (body.getBoundingClientRect().y >= 0) {
    navbar.classList.add('no-bg');
  } else {
    navbar.classList.remove('no-bg');
  }
}
navbarRemoveBg()
window.addEventListener("scroll", navbarRemoveBg);
