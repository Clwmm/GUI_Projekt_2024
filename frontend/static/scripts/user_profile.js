// 1. Fetch and display balance (coins):
async function fetchCoins() {
  const response = await fetch('http://localhost:8000/coins');
  if (!response.ok) {
    throw new Error('Failed to fetch coins.');
  }
  return await response.json();
}

// (opcjonalnie) Dedykowana funkcja do odświeżania salda w UI
async function fetchUserBalance() {
  try {
    const coins = await fetchCoins();
    // Tutaj powinieneś uwzględnić aktualizację wyświetlanego salda / portfela
    console.log('Fetched coins:', coins);
    // np. updateUI(coins);
  } catch (error) {
    console.error('Failed to fetch user balance:', error);
  }
}

// 2. Fetch and display transaction history:
async function fetchTransactions() {
  try {
    const response = await fetch('/all_transaction');
    if (!response.ok) {
      throw new Error('Failed to fetch transactions.');
    }
    const transactions = await response.json();

    // Example structure of `transactions`:
    // [ { id: 1, type: 'deposit', amount: 100, date: '2025-01-01' }, ... ]

    const list = document.getElementById('transactionsList');
    list.innerHTML = ''; // clear the list

    transactions.forEach(tx => {
      const li = document.createElement('li');
      li.className = 'p-3 border border-gray-200 rounded';
      li.textContent = `#${tx.id} | ${tx.type.toUpperCase()} | ${tx.amount} USD | ${tx.date}`;
      list.appendChild(li);
    });
  } catch (error) {
    console.error(error);
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
    const amount = prompt('Enter withdrawal amount:');
    if (!amount) return;

    const response = await fetch('/withdraw', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: parseFloat(amount) })
    });
    if (!response.ok) {
      throw new Error('Failed to execute withdrawal.');
    }
    alert('Withdrawal successful!');

    // After the withdrawal, refresh balance and transactions
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
