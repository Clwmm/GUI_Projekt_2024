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

    function createChart(containerId, chartData, currencyPair) {
      const container = document.getElementById(containerId);
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
      const btcData = await fetchChartData('usd', 'btc');
      createChart('btc-chart', btcData, 'BTC/USDT');

      const ethData = await fetchChartData('usd', 'eth');
      createChart('eth-chart', ethData, 'ETH/USDT');
    });