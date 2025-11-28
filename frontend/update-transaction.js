document.getElementById("transactionForm").addEventListener("submit", function (event) {
  event.preventDefault()
  const formData = new FormData(this)
  fetch("/update_transactions", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message || data.error)
    })
})

