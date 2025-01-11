async function fetchPairs() {
  try {
    const response = await fetch('http://localhost:8000/pairs');
    if (!response.ok) {
      throw new Error('Failed to fetch pairs');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching pairs:', error);
    return [];
  }
}

async function fetchChartData(p_from, p_to) {
  try {
    const response = await fetch('http://localhost:8000/chart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_from, p_to }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch chart data');
    }

    const data = await response.json();
    return data.map(item => ({ time: item.time, value: item.value }));
  } catch (error) {
    console.error('Error fetching chart data:', error);
    return [];
  }
}

function createChart(containerId, chartData) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  const chart = LightweightCharts.createChart(container, {
    width: container.offsetWidth,
    height: container.offsetHeight,
    layout: {
      backgroundColor: '#1f2937',
      textColor: '#d1d5db',
    },
    grid: {
      vertLines: { color: '#2d3748' },
      horzLines: { color: '#2d3748' },
    },
  });

  const series = chart.addLineSeries({
    color: '#00b5ad',
    lineWidth: 2,
  });

  series.setData(chartData);
  chart.timeScale().fitContent();
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

  const [initialFrom, initialTo] = pairs[0].split('/');
  const initialData = await fetchChartData(initialFrom, initialTo);
  createChart('crypto-chart', initialData);
  document.getElementById('chart-title').textContent = `Chart: ${pairs[0].toUpperCase()}`;

  pairSelector.addEventListener('change', async (event) => {
    const [p_from, p_to] = event.target.value.split('/');
    const chartData = await fetchChartData(p_from, p_to);
    createChart('crypto-chart', chartData);
    document.getElementById('chart-title').textContent = `Chart: ${event.target.value.toUpperCase()}`;
  });
});
