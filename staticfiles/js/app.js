document.addEventListener("DOMContentLoaded", () => {
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

  function updateFlag(selectElement) {
    const currCode = selectElement.value;
    const countryCode = countryList[currCode];
    const img = selectElement.parentElement.querySelector("img");
    img.src = `https://flagsapi.com/${countryCode}/flat/64.png`;
  }

  async function updateExchangeRate() {
    let amtVal = parseFloat(amountInput.value);
    if (isNaN(amtVal) || amtVal < 1) amtVal = 1;

    const from = fromCurr.value.toLowerCase();
    const to = toCurr.value.toLowerCase();

    try {
      // Call our own DB-backed endpoint
      const res = await fetch(`/currency-converter/rates/?base=${from}`);
      const data = await res.json();

      if (data.error) {
        msg.innerText = "Exchange rate data unavailable. Please try again.";
        return;
      }

      const rate = data.rates[to];
      if (!rate) { msg.innerText = "Rate not available for selected currency."; return; }

      const finalAmount = amtVal * rate;
      msg.innerText = `${amtVal} ${fromCurr.value} = ${finalAmount.toFixed(2)} ${toCurr.value}`;
    } catch (err) {
      msg.innerText = "Error fetching exchange rate. Please try again later.";
    }
  }

  btn.addEventListener("click", updateExchangeRate);
  updateExchangeRate();
});


