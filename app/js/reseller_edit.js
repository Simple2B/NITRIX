// custom javascript
$(document).ready(() => {
  let incommingResellerInfo = Array.from(document.querySelectorAll(".changeable")).map(el => (el.value));
  document.querySelectorAll(".redirector").forEach(button => button.addEventListener('click', e => {
    let targetLocation = e.currentTarget.href;
    let outgoingResellerInfo = Array.from(document.querySelectorAll(".changeable")).map(el => (el.value));
    if (JSON.stringify(incommingResellerInfo) != JSON.stringify(outgoingResellerInfo)) {
      e.preventDefault();
      let formElement = document.querySelector('#main-form');
      let formData = new FormData(formElement);
      formData.set("submit", "save_and_edit");
      fetch(formElement.action, {
        method: 'POST',
        body: formData
      })
        .then(response => {
          if (response.status == 200) {
            window.location.href = targetLocation;
          } else {
            alert('Server issues. Please, try this approach later!');
            throw Error(response.statusText);
          }
        }).catch(error => console.log(error));
    }
  }))
});
