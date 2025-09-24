document.addEventListener("DOMContentLoaded", () => {
  const BASE_URL = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies";

  const dropdowns = document.querySelectorAll(".dropdown select");
  const fromCurr = document.querySelector(".from select");
  const toCurr = document.querySelector(".to select");
  const msg = document.querySelector(".msg");
  const btn = document.getElementById("convertBtn");
  const amountInput = document.querySelector(".amount input");

  // Populate dropdowns
  for (let select of dropdowns) {
    for (let currCode in countryList) {
      const option = document.createElement("option");
      option.value = currCode;
      option.innerText = currCode;

      if (select.name === "from" && currCode === "USD") option.selected = true;
      if (select.name === "to" && currCode === "NPR") option.selected = true;

      select.append(option);
    }

    select.addEventListener("change", (e) => updateFlag(e.target));
  }

  // Update flag image
  function updateFlag(selectElement) {
    const currCode = selectElement.value;
    const countryCode = countryList[currCode];
    const img = selectElement.parentElement.querySelector("img");
    img.src = `https://flagsapi.com/${countryCode}/flat/64.png`;
  }

  // Fetch and display exchange rate
  async function updateExchangeRate() {
    let amtVal = parseFloat(amountInput.value);
    if (isNaN(amtVal) || amtVal < 1) amtVal = 1;

    const from = fromCurr.value.toLowerCase();
    const to = toCurr.value.toLowerCase();
    const URL = `${BASE_URL}/${from}.json`;

    try {
      const res = await fetch(URL);
      const data = await res.json();

      const rate = data[from][to];
      const finalAmount = amtVal * rate;

      msg.innerText = `${amtVal} ${fromCurr.value} = ${finalAmount.toFixed(2)} ${toCurr.value}`;
    } catch (err) {
      msg.innerText = "Error fetching exchange rate. Please try again later.";
      console.error(err);
    }
  }

  // Button click
  btn.addEventListener("click", updateExchangeRate);

  // Initial load
  updateExchangeRate();
});


