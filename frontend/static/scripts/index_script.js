document.getElementById("logout_button").addEventListener("click", function() {
            window.location.href = "/logout"
        });

function initChart(containerId, data, candleData) {
    const chartOptions = { layout: { textColor: 'black', background: { type: 'solid', color: 'white' } } };
    const chart = createChart(document.getElementById(containerId), chartOptions);
    // const chart = LightweightCharts.createChart(document.getElementById(containerId), {
    //     width: 600,
    //     height: 400,
    //     layout: {
    //         backgroundColor: '#ffffff',
    //         textColor: '#000',
    //     },
    //     grid: {
    //         vertLines: { color: '#eee' },
    //         horzLines: { color: '#eee' },
    //     },
    // });
    // const lineSeries = chart.addLineSeries();
    // lineSeries.setData(data);

    const areaSeries = chart.addAreaSeries({
        lineColor: '#2962FF', topColor: '#2962FF',
        bottomColor: 'rgba(41, 98, 255, 0.28)',
    });

    areaSeries.setData(data);
    const candlestickSeries = chart.addCandlestickSeries({
        upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
        wickUpColor: '#26a69a', wickDownColor: '#ef5350',
    });

    candlestickSeries.setData(candleData);

    chart.timeScale().fitContent();
}
