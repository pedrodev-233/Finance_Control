const chartCanvas = document.querySelector("#finance-chart");
const chartDataElement = document.querySelector("#chart-data");

if (chartCanvas && chartDataElement) {
    const chartData = JSON.parse(chartDataElement.textContent);
    const emptyMessage = document.querySelector("#chart-empty");
    const hasEntries = chartData.some((item) => item.income > 0 || item.expenses > 0);
    const context = chartCanvas.getContext("2d");

    if (!hasEntries && emptyMessage) {
        emptyMessage.hidden = false;
    }

    const drawChart = () => {
        const bounds = chartCanvas.getBoundingClientRect();
        const pixelRatio = window.devicePixelRatio || 1;
        const width = bounds.width;
        const height = bounds.height;
        const padding = { top: 12, right: 8, bottom: 25, left: 48 };
        const plotWidth = width - padding.left - padding.right;
        const plotHeight = height - padding.top - padding.bottom;
        const maximum = Math.max(
            100,
            ...chartData.flatMap((item) => [item.income, item.expenses]),
        );
        const scale = 10 ** Math.floor(Math.log10(maximum));
        const axisMaximum = Math.ceil(maximum / scale) * scale;
        const groupWidth = plotWidth / chartData.length;
        const barWidth = Math.max(1, Math.min(7, groupWidth * 0.28));

        chartCanvas.width = Math.round(width * pixelRatio);
        chartCanvas.height = Math.round(height * pixelRatio);
        context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
        context.clearRect(0, 0, width, height);
        context.font = "9px DM Sans, sans-serif";
        context.textBaseline = "middle";

        for (let index = 0; index <= 4; index += 1) {
            const y = padding.top + (plotHeight * index) / 4;
            const value = axisMaximum * (1 - index / 4);
            context.strokeStyle = "#edf0f5";
            context.lineWidth = 1;
            context.beginPath();
            context.moveTo(padding.left, y);
            context.lineTo(width - padding.right, y);
            context.stroke();
            context.fillStyle = "#9aa1b0";
            context.textAlign = "right";
            context.fillText(
                value >= 1000 ? `${(value / 1000).toLocaleString("pt-BR")} mil` : value.toLocaleString("pt-BR"),
                padding.left - 8,
                y,
            );
        }

        chartData.forEach((item, index) => {
            const center = padding.left + groupWidth * index + groupWidth / 2;
            const incomeHeight = (item.income / axisMaximum) * plotHeight;
            const expenseHeight = (item.expenses / axisMaximum) * plotHeight;

            context.fillStyle = "#6875e9";
            context.beginPath();
            context.roundRect(
                center - barWidth - 1,
                padding.top + plotHeight - incomeHeight,
                barWidth,
                Math.max(incomeHeight, item.income ? 2 : 0),
                3,
            );
            context.fill();

            context.fillStyle = "#69c5a0";
            context.beginPath();
            context.roundRect(
                center + 1,
                padding.top + plotHeight - expenseHeight,
                barWidth,
                Math.max(expenseHeight, item.expenses ? 2 : 0),
                3,
            );
            context.fill();

            if (
                item.day === 1 ||
                item.day === chartData.length ||
                item.day % 5 === 0
            ) {
                context.fillStyle = "#9aa1b0";
                context.textAlign = "center";
                context.fillText(String(item.day), center, height - 9);
            }
        });
    };

    drawChart();
    window.addEventListener("resize", drawChart);

    document.querySelectorAll("[data-confirm-delete]").forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!window.confirm("Tem certeza de que deseja excluir este lançamento?")) {
                event.preventDefault();
            }
        });
    });
}
