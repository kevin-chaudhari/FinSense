document.getElementById("queryForm").addEventListener("submit", function (event) {
  event.preventDefault()
  const formData = new FormData(this)
  fetch("/query", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.response || data.error)
    })
})

