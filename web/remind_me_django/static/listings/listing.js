const product_dates = document.querySelector(".inner-card-added-on");
const url_field = document.querySelector('#url-field');
const track_btn = document.querySelector('.track-btn');

const check_field = function(event) {
  const pattern = /^(http|https):\/\/(www\.)?amazon\.ca\/([a-zA-Z0-9-_]+\/)+/i
  const value = url_field.value.toLowerCase();
  const match = value.match(pattern);

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

url_field.addEventListener('keyup', check_field)
console.log(product_dates);

