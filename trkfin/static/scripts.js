
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



// ********** WALLETS **********

const addWalletForm = document.forms["AddWalletform"];
if (addWalletForm) {

  // ***** helper functions *****

  function hide_group_input(select, input) {
    if (select.value == '*New') {
      input.classList.remove('form-hide');
    } else {
      input.classList.add('form-hide');
    }
  }

  function grey_out_groups(select) {
    if (select.value == "" || select.value == "*New") {
      select.classList.add('group-greyed-out');
    } else {
      select.classList.remove('group-greyed-out');
    }
  }

  // ***** Forms *****

  // highlight header buttons ("Add new" and "Edit") on activation
  const headerBttns = document.querySelectorAll('[data-header-bttn]')
  headerBttns.forEach(x => {
    x.addEventListener('click', () => {
      x.classList.toggle('active');
    });
  });

  // hide group input and grey out None and New in forms
  const groupSelectors = document.querySelectorAll('[data-group-select]')
  groupSelectors.forEach(s => {
    let i = document.querySelector('[data-group-input="' + s.dataset.groupSelect + '"]')

    hide_group_input(s, i);
    grey_out_groups(s);

    s.addEventListener('change', () => {
      hide_group_input(s, i);
      grey_out_groups(s);
    });
  });

  // ***** Wallet controls Modals *****

  // show controls
  const editSwitch = document.querySelector('[data-edit-switch]')
  const editBtns = document.querySelectorAll('[data-edit-btn]')
  editSwitch.addEventListener('click', function() {
    document.querySelectorAll('[data-unnamed-group]').forEach(x => {
      x.classList.toggle('group-unnamed')
    });
    editBtns.forEach(x => {
      x.classList.toggle('show-btn');
    });
  });

  // open and close modals
  const modalToggles = document.querySelectorAll('[data-modal-toggle]')
  modalToggles.forEach(x => {
    x.addEventListener('click', function() {
      let select = '[data-modal = "' + x.dataset.modalToggle + '"]'
      document.querySelectorAll(select).forEach(m => {
        m.classList.toggle('modal-show')
      });
    });
  });

  // prevent closing modal by clicking on content
  const modalContents = document.querySelectorAll('[data-modal-content]')
  modalContents.forEach(x => {
    x.addEventListener('click', (y) => {
      y.cancelBubble = true;
    });
  });

}



// ********** ACCOUNT **********

const updTimezone = document.forms["change-timezone"];
if (updTimezone) {
  
  // display user's saved timezone
  function parseTimezone(offset) {
    let direction = '+';
    if (offset < 0) {
      direction = '-';
      offset *= -1;
    }
    let hours = offset / 60;
    if (hours < 10) {hours = '0' + hours;}
    let minutes = offset % 60;
    if (minutes < 10) {minutes = '0' + minutes;}
    return ('GMT' + direction + hours + ':' + minutes);
  }
  let userTz = document.querySelector('[data-timezone]');
  userTz.innerText = parseTimezone(Number(userTz.dataset.timezone) / 60);

  // record user's current timezone
  let currentTz = new Date();
  document.querySelector('[data-new-tz]').value = currentTz.getTimezoneOffset() * -60;

}

const chgReports = document.forms["change-reports"];
if (chgReports) {
  
  let repFqSelect = document.querySelector('[data-rep-freq-select]')
  let repFqInput = document.querySelector('[data-rep-freq-input]')
  let repFq = document.querySelector('[data-rep-freq]')
  
  repFqSelect.addEventListener("change", () => {
    if (repFqSelect.value == "other") {
      repFqInput.classList.remove('form-hide');
    } else {
      repFqInput.classList.add('form-hide');
    }
  });

  repFq.selected = true;

}



// ********** CONFIRM **********

const toConfirm = document.querySelectorAll('[data-confirm-action]');
toConfirm.forEach(x => {
  x.addEventListener('submit', (event) => {
    let message = x.dataset.confirmAction;
    if (!confirm(message)) {
      event.preventDefault();
    }
  });
});
