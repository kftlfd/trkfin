document.addEventListener("DOMContentLoaded", function() {

  // add leading zeros
  function lz(n) {
    if (n <= 9) {
      return "0" + n;
    }
    return n;
  }

  // add leading zeros to miliseconds
  function lzms(n) {
    if (n <= 9) {
      return "00" + n;
    }
    else if (n <= 99) {
      return "0" + n;
    }
    return n;
  }

  // input timestamp on form submit
  function getLocalTime() {
    let date = new Date();
    return date.getFullYear() + "-" + lz(date.getMonth() + 1) + "-" + lz(date.getDate()) + " " +
          lz(date.getHours()) + ":" + lz(date.getMinutes()) + ":" + lz(date.getSeconds()) + ":" +
          lzms(date.getMilliseconds());
  }

  if (document.forms[0]) {
    document.forms[0].addEventListener('submit', function() {
      document.forms[0].timestamp.value = getLocalTime();
      
    });


    // no. of seconds to add to utc-timestamp to get users local time
    let d = new Date();
    document.forms[0].tz_offset.value = d.getTimezoneOffset() * (-60);
  }

});