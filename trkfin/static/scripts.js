if (document.forms[0]) {
  // no. of seconds to add to utc-timestamp to get users' local time
  let d = new Date()
  document.forms[0].tz_offset.value = d.getTimezoneOffset() * (-60)
}
