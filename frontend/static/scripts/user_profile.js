document.addEventListener('DOMContentLoaded', async () => {
  try {
    const coinsResponse = await fetch('http://localhost:8000/coins');
    if (!coinsResponse.ok) {
      throw new Error('Błąd podczas pobierania coinów: ' + coinsResponse.statusText);
    }

    const coins = await coinsResponse.json();
    console.log('Otrzymane coiny:', coins); // Debug

    const tableBody = document.querySelector('#coinsTable tbody');
    if (!tableBody) {
      console.error('Nie znaleziono #coinsTable tbody w HTML!');
      return;
    }

    tableBody.innerHTML = '';

    coins.forEach(coin => {
      let amountFormatted = parseFloat(coin.amount);
      if (coin.name.toLowerCase() === 'usd') {
        amountFormatted = amountFormatted.toFixed(2);
      } else {
        amountFormatted = amountFormatted.toFixed(6);
      }

      const tr = document.createElement('tr');
      tr.classList.add('hover:bg-gray-700');

      const coinTd = document.createElement('td');
      coinTd.classList.add('py-2', 'px-4', 'font-bold', 'text-white-400');
      coinTd.textContent = coin.name.toUpperCase();
      tr.appendChild(coinTd);

      const amountTd = document.createElement('td');
      amountTd.classList.add('py-2', 'px-4', 'text-white-300');
      amountTd.textContent = amountFormatted;
      tr.appendChild(amountTd);

      tableBody.appendChild(tr);
    });
  } catch (error) {
    console.error('Error fetching coins:', error);
  }
});

// 2. Fetch and display transaction history:
async function fetchTransactions() {
  try {
    const response = await fetch('http://localhost:8000/all_transaction');
    const transactions = await response.json();
    transactionsTableBody.innerHTML = transactions.map(transaction => `
               <tr class="border-b border-gray-700 hover:bg-gray-700 transition duration-200">
                   <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.currency_from}</td>
                   <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.currency_to}</td>
                   <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.amount_from}</td>
                   <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.amount_to}</td>
                   <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.timestamp}</td>
               </tr>
           `).join('');
  } catch (error) {
    console.error('Error fetching transactions:', error);
  }
}

// 3. Deposit
async function deposit() {
  try {
    const amount = prompt('Enter deposit amount:');
    if (!amount) return;

    const response = await fetch('/deposit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: parseFloat(amount) })
    });
    if (!response.ok) {
      throw new Error('Failed to execute deposit.');
    }
    alert('Deposit successful!');

    // After the deposit, refresh balance and transactions
    await fetchUserBalance();
    await fetchTransactions();
  } catch (error) {
    console.error(error);
  }
}

// 4. Withdraw
async function withdraw() {
  try {
    const amountInput = prompt('Enter withdrawal amount:');
    if (!amountInput) return;

    const amount = parseFloat(amountInput);

    const response = await fetch('/withdraw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount })
    });
    const data = await response.json();

    if (data.status_code === 400) {
      alert('Withdrawal unsuccessful!');
      return;
    }
    alert('Withdrawal successful!');
    await fetchUserBalance();
    await fetchTransactions();

  } catch (error) {
    console.error(error);
  }
}

// 5. Event listeners for buttons
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('depositBtn').addEventListener('click', deposit);
  document.getElementById('withdrawBtn').addEventListener('click', withdraw);

  // On page load, fetch balance and transactions
  fetchUserBalance();
  fetchTransactions();
});
