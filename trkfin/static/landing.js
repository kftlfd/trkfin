// reveal (only if page is not scrolled down)
const body = document.querySelector('body');
let slideSections = document.querySelectorAll(".slide-reveal");
if (body.getBoundingClientRect().y == 0) {
  body.classList.add("reveal");
  function slideReveal() {
    slideSections.forEach(x => {
      if (x.getBoundingClientRect().y < window.screen.height * 0.95) {
        x.classList.add("done")
      }
    });
  }
  slideReveal()
  window.addEventListener("scroll", slideReveal);
} else {
  slideSections.forEach(x => x.classList.remove("slide-reveal"));
}
body.classList.remove("hide");
