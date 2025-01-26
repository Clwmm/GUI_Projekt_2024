document.addEventListener('DOMContentLoaded', async function () {
    const usersTableBody = document.getElementById('usersTableBody');
    const transactionsTableBody = document.getElementById('transactionsTableBody');

    async function fetchUsers() {
        try {
            const response = await fetch('http://localhost:8000/get_all_users');
            const users = await response.json();
            usersTableBody.innerHTML = users.map(user => `
                <tr class="border-b border-gray-700 hover:bg-gray-700 transition duration-200">
                    <td class="px-6 py-4 text-sm font-medium text-gray-200">${user}</td>
                    <td class="px-6 py-4 text-sm font-medium">
                        <button onclick="banUser('${user}')" class="bg-red-600 text-white py-1 px-3 rounded-lg hover:bg-red-700 transition duration-200">
                            <i class="fas fa-ban"></i> Ban
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error fetching users:', error);
        }
    }

    async function fetchTransactions() {
        try {
            const response = await fetch('http://localhost:8000/get_users_transactions');
            const transactions = await response.json();
            transactionsTableBody.innerHTML = transactions.map(transaction => `
                <tr class="border-b border-gray-700 hover:bg-gray-700 transition duration-200">
                    <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.currency_from}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.currency_to}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.amount_from}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.amount_to}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.timestamp}</td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-200">${transaction.email}</td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error fetching transactions:', error);
        }
    }

    window.banUser = async function (email) {
        try {
            const response = await fetch('http://localhost:8000/ban_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({email}),
            });
            const result = await response.json();
            if (result.status_code === 200) {
                alert(`User ${email} banned successfully.`);
                fetchUsers();
            } else {
                alert(`Failed to ban user: ${result.detail}`);
            }
        } catch (error) {
            console.error('Error banning user:', error);
        }
    }

    await fetchUsers();
    await fetchTransactions();
});