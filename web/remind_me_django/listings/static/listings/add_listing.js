const product_dates = document.querySelector(".inner-card-added-on");
const url_field = document.querySelector('#url-field');
const track_btn = document.querySelector('.track-btn');

// Semi-validate url field
const check_field = function(event) {
  // Mobile
  const split_array = url_field.value.split(' ');
  // console.log(split_array);
  if (split_array.length > 1) {
    url_field.value = split_array.at(-1);
    // console.log(url_field.value);
  }

  const pattern = /^(http|https):\/\/(www\.)?amazon\.ca\/([a-zA-Z0-9-_]+\/)+/i
  const value = url_field.value.toLowerCase();
  const match = value.trim().match(pattern);

  if (match){
    track_btn.classList.add('valid-input');
    track_btn.classList.remove('invalid-input');
    console.log('true');          

  } else {
    track_btn.classList.remove('valid-input');
    track_btn.classList.add('invalid-input');
    console.log('false');   
  }
};

url_field.addEventListener('change', check_field)
console.log(product_dates);

