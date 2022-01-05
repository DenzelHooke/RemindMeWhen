let product_dates = document.querySelectorAll('#inner-card-added-on');

const calendar = {
  months: {
    0:'Jan',
    1: 'Feb',
    2: 'Mar',
    3: 'Apr',
    4: 'May',
    5: 'Jun',
    6: 'Jul',
    7: 'Aug',
    8: 'Sep',
    9: 'Oct',
    10: 'Nov',
    11: 'Dec',
  },
};

product_dates.forEach(function(i) {
  // Split on the 'on' keyword within the str
  const item = i.textContent.split('on')[1].slice(1);
  // convert utc string into dt
  // automatically converts string into dt with the browsers timezone applied.
  const date_obj = new Date(`${item}`);
  i.textContent = `Added on ${calendar.months[date_obj.getMonth()]} ${date_obj.getDate()}, ${date_obj.getFullYear()}`
  console.log(date_obj);
  console.log(item);
})

console.log(product_dates);