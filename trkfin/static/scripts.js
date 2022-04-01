
// ********** NAVBAR **********

// dropdown
const navDropdown = document.querySelectorAll('[data-nav-dropdown]');
const navDropdownToggle = document.querySelectorAll('[data-nav-dropdown-toggle]');
navDropdownToggle.forEach(x => {
  x.addEventListener('click', () => {
    navDropdown.forEach(y => {
      y.classList.toggle('nav-dropdown-show');
    });
  });
}); 

// sidebar
const navSidebar = document.querySelectorAll("[data-nav-sidebar]")
const navSidebarToggles = document.querySelectorAll("[data-nav-sidebar-toggle]")
navSidebarToggles.forEach(x => {
  x.addEventListener('click', () => {
    navSidebar.forEach(y => {
      y.classList.toggle('nav-sidebar-open');
    });
  });
});



// ********** ALERTS **********

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



// ********** REGISTRATION **********

// get user timezone
const tzInput = document.forms["registerform"]?.tz_offset;
if (tzInput) {
  let d = new Date();
  tzInput.value = d.getTimezoneOffset() * (-60)
}



// ********** HOME **********

const mainForm = document.forms["MainForm"];
if (mainForm) {
  let src = document.querySelector('[data-form-field="source"');
  let dest = document.querySelector('[data-form-field="destination"');
  mainForm.addEventListener('click', function() {
    let select = mainForm.action.value;
    if (select == 'Spending') {
      src.classList.remove('form-hide');
      dest.classList.add('form-hide');
    }
    else if (select == 'Income') {
      src.classList.add('form-hide');
      dest.classList.remove('form-hide');
    }
    else { // 'transfer'
      src.classList.remove('form-hide');
      dest.classList.remove('form-hide');
    }
  });
  // select 'spending' as default
  mainForm.action.item(0).click();
}

// wallet title active on click
document.querySelectorAll('[data-wallet-title]').forEach(x => {
  x.addEventListener('click', () => {
    x.classList.toggle('active');
  });
});
