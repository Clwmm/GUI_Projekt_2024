async function fetchCoins() {
  const response = await fetch('http://localhost:8000/coins');
  if (!response.ok) {
    throw new Error('Failed to fetch coins');
  }
  return await response.json();
}

async function fetchPairs() {
  const response = await fetch('http://localhost:8000/pairs');
  if (!response.ok) {
    throw new Error('Failed to fetch pairs');
  }
  return await response.json();
}

async function fetchChartData(p_from, p_to) {
  const response = await fetch('http://localhost:8000/chart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ p_from, p_to }),
  });
  const data = await response.json();
  return data.map(item => ({ time: item.time, value: item.value }));
}

async function fetchActualPrice(p_from, p_to) {
  const response = await fetch('http://localhost:8000/price', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ p_from, p_to }),
  });
  return await response.json();
}

function createChart(containerId, chartData) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  const chart = LightweightCharts.createChart(container, {
    width: container.offsetWidth,
    height: container.offsetHeight,
    layout: {
      textColor: 'white',
      background: { type: 'solid', color: '#17161c' },
    },
    grid: {
      vertLines: {
        color: 'transparent',
      },
      horzLines: {
        color: 'transparent',
      },
    },
    timeScale: {
      borderColor: 'transparent',
    },
  });
  const series = chart.addLineSeries({
    color: '#2962FF',
    lineWidth: 3,
  });
  series.setData(chartData);
  chart.timeScale().fitContent();

  function resizeChart() {
    chart.resize(container.offsetWidth, container.offsetHeight);
  }

  window.addEventListener('resize', resizeChart);

  container.cleanup = () => {
    window.removeEventListener('resize', resizeChart);
  };
}

function createCoinElement(coin) {
  const coinDiv = document.createElement('div');
  coinDiv.classList.add(
      'coin-item',
      'bg-gray-700',
      'p-6',
      'rounded-lg',
      'flex',
      'items-center',
      'justify-between',
      'transition-all',
      'duration-200',
      'hover:bg-gray-600',
      'border',
      'border-gray-600'
  );
  coinDiv.innerHTML = `
    <div class="flex items-center space-x-4">
      <div class="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
        ${coin.name.charAt(0).toUpperCase()}
      </div>
      <div>
        <div class="font-medium text-white">${coin.name.toUpperCase()}</div>
        <div class="text-sm text-gray-400">Balance</div>
      </div>
    </div>
    <div class="text-right">
      <div class="font-medium text-white">${coin.amount}</div>
      <div class="text-sm text-gray-400">Available</div>
    </div>
  `;
  return coinDiv;
}

document.addEventListener('DOMContentLoaded', async () => {
  const pairs = await fetchPairs();
  const pairSelector = document.getElementById('pair-selector');
  pairs.forEach(pair => {
    const option = document.createElement('option');
    option.value = pair;
    option.textContent = pair.toUpperCase();
    pairSelector.appendChild(option);
  });

  let transactionType = "";
  function updateTransactionType(type, value) {
    transactionType = type;

    const buyButton = document.getElementById("buy-button");
    const sellButton = document.getElementById("sell-button");

    if (type === "buy") {
      buyButton.classList.add("ring-4", "ring-green-400");
      sellButton.classList.remove("ring-4", "ring-red-400");

      const amount_from = document.getElementById("transaction-amount");
      const spanElement_from = amount_from.parentElement.querySelector("span");
      const amount_to = document.getElementById("transaction-result-amount");
      const spanElement_to = amount_to.parentElement.querySelector("span");
      const selectedPair = value ? value : document.getElementById('pair-selector').value;
      const [from, to] = selectedPair.split('/');
      spanElement_from.innerHTML = to.toUpperCase();
      spanElement_to.innerHTML = from.toUpperCase();


    } else if (type === "sell") {
      sellButton.classList.add("ring-4", "ring-red-400");
      buyButton.classList.remove("ring-4", "ring-green-400");

      const amount_from = document.getElementById("transaction-amount");
      const spanElement_from = amount_from.parentElement.querySelector("span");
      const amount_to = document.getElementById("transaction-result-amount");
      const spanElement_to = amount_to.parentElement.querySelector("span");
      const selectedPair = value ? value : document.getElementById('pair-selector').value;
      const [from, to] = selectedPair.split('/');
      spanElement_from.innerHTML = from.toUpperCase();
      spanElement_to.innerHTML = to.toUpperCase();
    }
  }

  const transactionAmountElement = document.getElementById('transaction-amount');

  async function updateTransactionResultAmount(value) {
    if (transactionType === "") return;

    let exchange_rate = 0;
    const selectedPair = document.getElementById('pair-selector').value;
    const [from, to] = selectedPair.split('/');

    if (transactionType === "buy") {
      exchange_rate = await fetchActualPrice(to, from);
    }
    if (transactionType === "sell") {
      exchange_rate = await fetchActualPrice(from, to);
    }

    const result = exchange_rate * value;
    const ele = document.getElementById('transaction-result-amount');
    ele.innerHTML = result.toString();
  }

  transactionAmountElement.addEventListener('blur', (event) => {
    const value = parseFloat(event.target.value);
    if (!isNaN(value)) {
      updateTransactionResultAmount(value);
    }
  });


  const [initialFrom, initialTo] = pairs[0].split('/');
  const initialData = await fetchChartData(initialFrom, initialTo);
  createChart('crypto-chart', initialData);

  pairSelector.addEventListener('change', async (event) => {
    const [p_from, p_to] = event.target.value.split('/');
    const chartData = await fetchChartData(p_from, p_to);
    createChart('crypto-chart', chartData);
    updateTransactionType(transactionType, event.target.value)
  });

  const coins = await fetchCoins();
  const coinsContainer = document.getElementById('coins-container');
  coinsContainer.innerHTML = '';
  coins.forEach(coin => {
    coinsContainer.appendChild(createCoinElement(coin));
  });

  const buyButton = document.getElementById("buy-button");
  const sellButton = document.getElementById("sell-button");

  buyButton.addEventListener("click", () => updateTransactionType("buy"));
  sellButton.addEventListener("click", () => updateTransactionType("sell"));


  document.getElementById('confirm-transaction').addEventListener('click', async () => {
    const selectedPair = document.getElementById('pair-selector').value;
    const [coin, _] = selectedPair.split('/');
    const amount = parseFloat(document.getElementById('transaction-amount').value);

    if (!amount || amount <= 0) {
      showNotification('Please enter a valid amount.', 3000, 'error');
      return;
    }

    if (coin.toLowerCase() === 'usd') {
      showNotification('Cannot trade USD for USD.', 3000, 'error');
      return;
    }

    try {
      const coins = await fetchCoins();
      const coinData = coins.find(c => c.name.toLowerCase() === coin.toLowerCase());
      const usdData = coins.find(c => c.name.toLowerCase() === 'usd');

      if (transactionType === 'buy') {
        if (!usdData || usdData.amount < amount) {
          showNotification('Insufficient USD balance to complete the transaction.', 3000, 'error');
          return;
        }
      } else if (transactionType === 'sell') {
        if (!coinData || coinData.amount < amount) {
          showNotification(`Insufficient ${coin.toUpperCase()} balance to complete the transaction.`, 3000, 'error');
          return;
        }
      }

      let transactionData;
      if (transactionType === 'buy') {
        transactionData = {
          t_from: 'usd',
          t_to: coin,
          amount_from: amount
        };
      } else {
        transactionData = {
          t_from: coin,
          t_to: 'usd',
          amount_from: amount
        };
      }

      const transactionResponse = await fetch('http://localhost:8000/transaction', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transactionData),
      });

      if (!transactionResponse.ok) {
        const errorData = await transactionResponse.json();
        throw new Error(errorData.detail || 'Transaction failed');
      }

      const transactionResult = await transactionResponse.json();
      showNotification('Transaction completed successfully.', 2000);

      const updatedCoins = await fetchCoins();
      const coinsContainer = document.getElementById('coins-container');
      coinsContainer.innerHTML = '';
      updatedCoins.forEach(coin => {
        coinsContainer.appendChild(createCoinElement(coin));
      });

    } catch (error) {
      showNotification(error.message, 3000, 'error');
      console.error('Transaction error:', error);
    }
  });

});


function showNotification(message, duration = 3000, type = 'success') {
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 bg-${
      type === 'success' ? 'green' : 'red'
  }-500 text-white px-6 py-3 rounded-lg shadow-lg opacity-0 transition-opacity duration-500 transform translate-x-full z-50`;
  notification.textContent = message;

  const container = document.getElementById('notificationContainer');
  container.appendChild(notification);

  setTimeout(() => {
    notification.classList.remove('opacity-0', 'translate-x-full');
    notification.classList.add('opacity-100', 'translate-x-0');
  }, 10);

  setTimeout(() => {
    notification.classList.remove('opacity-100', 'translate-x-0');
    notification.classList.add('opacity-0', 'translate-x-full');
    setTimeout(() => {
      container.removeChild(notification);
    }, 500);
  }, duration);
}