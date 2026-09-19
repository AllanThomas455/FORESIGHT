// ==========================================
// FORESIGHT DASHBOARD
// COMPLETE JAVASCRIPT
// ==========================================

let monthlyChart = null;
let categoryChart = null;
let demandDistributionChart = null;
let modelErrorChart = null;
let modelR2Chart = null;


// ==========================================
// PAGE INITIALIZATION
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    updateClock();

    setInterval(updateClock, 1000);

    loadAnalytics();

    const predictButton = document.getElementById("predictButton");

    if (predictButton) {
        predictButton.addEventListener("click", predictDemand);
    }

});


// ==========================================
// LIVE CLOCK
// ==========================================

function updateClock() {

    const clock = document.getElementById("liveClock");

    if (!clock) {
        return;
    }

    const now = new Date();

    clock.textContent = now.toLocaleTimeString("en-IN", {
        hour12: true
    });

}


// ==========================================
// LOAD ANALYTICS
// ==========================================

async function loadAnalytics() {

    try {

        const response = await fetch("/analytics");

        const data = await response.json();

        if (!response.ok) {

            console.error("Analytics error:", data);

            return;
        }


        // ------------------------------
        // KPIs
        // ------------------------------

        if (data.kpis) {
            updateKpis(data.kpis);
        }


        // ------------------------------
        // INSIGHTS
        // ------------------------------

        if (data.insights) {
            updateInsights(data.insights);
        }


        // ------------------------------
        // LATEST DATE
        // ------------------------------

        const latestDate =
            document.getElementById("latestDataDate");

        if (latestDate && data.latest_date) {
            latestDate.textContent = data.latest_date;
        }


        // ------------------------------
        // MONTHLY CHART
        // ------------------------------

        if (data.monthly) {
            createMonthlyChart(data.monthly);
        }


        // ------------------------------
        // CATEGORY CHART
        // ------------------------------

        if (data.category) {
            createCategoryChart(data.category);
        }


        // ------------------------------
        // DEMAND DISTRIBUTION
        // ------------------------------

        if (data.demand_distribution) {
            createDemandDistributionChart(
                data.demand_distribution
            );
        }


        // ------------------------------
        // MODEL PERFORMANCE
        // ------------------------------

        if (data.model_performance) {

            updateModelPerformance(
                data.model_performance
            );

        }

    }
    catch (error) {

        console.error(
            "Unable to load analytics:",
            error
        );

    }

}


// ==========================================
// UPDATE KPI CARDS
// ==========================================

function updateKpis(kpis) {

    // Total Units

    const totalUnits =
        document.getElementById("totalUnits");

    if (totalUnits && kpis.total_units !== undefined) {

        totalUnits.textContent =
            Number(
                kpis.total_units
            ).toLocaleString("en-IN");

    }


    // Total Revenue

    const totalRevenue =
        document.getElementById("totalRevenue");

    if (
        totalRevenue &&
        kpis.total_revenue !== undefined
    ) {

        const revenueCrores =
            Number(kpis.total_revenue) / 10000000;

        totalRevenue.textContent =
            "₹" +
            revenueCrores.toFixed(2) +
            " Cr";

    }


    // Average Unit Price

    const averagePrice =
        document.getElementById("averagePrice");

    if (
        averagePrice &&
        kpis.average_unit_price !== undefined
    ) {

        averagePrice.textContent =
            "₹" +
            Number(
                kpis.average_unit_price
            ).toLocaleString(
                "en-IN",
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            );

    }


    // Unique SKUs

    const uniqueSkus =
        document.getElementById("uniqueSkus");

    if (
        uniqueSkus &&
        kpis.unique_skus !== undefined
    ) {

        uniqueSkus.textContent =
            Number(
                kpis.unique_skus
            ).toLocaleString("en-IN");

    }

}


// ==========================================
// UPDATE AI INSIGHTS
// ==========================================

function updateInsights(insights) {

    // ------------------------------
    // TOP CATEGORY
    // ------------------------------

    const topCategory =
        document.getElementById("topCategory");

    const topCategoryText =
        document.getElementById("topCategoryText");


    if (topCategory) {

        topCategory.textContent =
            insights.top_category || "N/A";

    }


    if (
        topCategoryText &&
        insights.top_category_units !== undefined
    ) {

        topCategoryText.textContent =
            Number(
                insights.top_category_units
            ).toLocaleString("en-IN") +
            " units sold in this category";

    }


    // ------------------------------
    // HIGHEST MONTH
    // ------------------------------

    const highestMonth =
        document.getElementById("highestMonth");

    const highestMonthText =
        document.getElementById("highestMonthText");


    if (highestMonth) {

        highestMonth.textContent =
            formatMonth(
                insights.highest_month
            );

    }


    if (
        highestMonthText &&
        insights.highest_month_units !== undefined
    ) {

        highestMonthText.textContent =
            Number(
                insights.highest_month_units
            ).toLocaleString("en-IN") +
            " units sold during this month";

    }


    // ------------------------------
    // LOWEST MONTH
    // ------------------------------

    const lowestMonth =
        document.getElementById("lowestMonth");

    const lowestMonthText =
        document.getElementById("lowestMonthText");


    if (lowestMonth) {

        lowestMonth.textContent =
            formatMonth(
                insights.lowest_month
            );

    }


    if (
        lowestMonthText &&
        insights.lowest_month_units !== undefined
    ) {

        lowestMonthText.textContent =
            Number(
                insights.lowest_month_units
            ).toLocaleString("en-IN") +
            " units sold during this month";

    }


    // ------------------------------
    // DOMINANT DEMAND
    // ------------------------------

    const dominantDemand =
        document.getElementById("dominantDemand");

    const dominantDemandText =
        document.getElementById("dominantDemandText");


    if (dominantDemand) {

        dominantDemand.textContent =
            insights.dominant_demand || "N/A";

    }


    if (
        dominantDemandText &&
        insights.dominant_demand_count !== undefined
    ) {

        dominantDemandText.textContent =
            Number(
                insights.dominant_demand_count
            ).toLocaleString("en-IN") +
            " sales records fall into this level";

    }

}


// ==========================================
// MODEL PERFORMANCE
// ==========================================

function updateModelPerformance(performance) {

    if (!performance) {
        return;
    }


    const models =
        Array.isArray(performance.models)
            ? performance.models
            : ["MLP", "LSTM"];


    const mae =
        Array.isArray(performance.mae)
            ? performance.mae
            : [2.5930, 2.4356];


    const rmse =
        Array.isArray(performance.rmse)
            ? performance.rmse
            : [3.6788, 3.6284];


    const r2 =
        Array.isArray(performance.r2)
            ? performance.r2
            : [0.7595, 0.7661];


    // ------------------------------
    // ACCURACY - WITHIN 10%
    // ------------------------------

    const within10 =
        document.getElementById(
            "within10Accuracy"
        );


    if (
        within10 &&
        performance.within_10 !== undefined
    ) {

        within10.textContent =
            Number(
                performance.within_10
            ).toFixed(2) +
            "%";

    }


    // ------------------------------
    // ACCURACY - WITHIN 20%
    // ------------------------------

    const within20 =
        document.getElementById(
            "within20Accuracy"
        );


    if (
        within20 &&
        performance.within_20 !== undefined
    ) {

        within20.textContent =
            Number(
                performance.within_20
            ).toFixed(2) +
            "%";

    }


    // ------------------------------
    // ERROR CHART
    // ------------------------------

    createModelErrorChart(
        models,
        mae,
        rmse
    );


    // ------------------------------
    // R2 CHART
    // ------------------------------

    createModelR2Chart(
        models,
        r2
    );

}


// ==========================================
// MODEL ERROR CHART
// ==========================================

function createModelErrorChart(
    models,
    maeValues,
    rmseValues
) {

    const canvas =
        document.getElementById(
            "modelErrorChart"
        );


    if (!canvas) {
        return;
    }


    if (
        typeof Chart === "undefined"
    ) {

        console.error(
            "Chart.js is not loaded."
        );

        return;
    }


    const ctx =
        canvas.getContext("2d");


    if (modelErrorChart) {

        modelErrorChart.destroy();

        modelErrorChart = null;
    }


    modelErrorChart =
        new Chart(
            ctx,
            {
                type: "bar",

                data: {

                    labels: models,

                    datasets: [

                        {
                            label: "MAE",

                            data: maeValues,

                            borderWidth: 1
                        },

                        {
                            label: "RMSE",

                            data: rmseValues,

                            borderWidth: 1
                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    interaction: {

                        intersect: false,

                        mode: "index"

                    },

                    plugins: {

                        legend: {

                            display: true,

                            position: "top"

                        },

                        tooltip: {

                            callbacks: {

                                label: function (
                                    context
                                ) {

                                    return (
                                        context.dataset.label +
                                        ": " +
                                        Number(
                                            context.raw
                                        ).toFixed(4)
                                    );

                                }

                            }

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            title: {

                                display: true,

                                text: "Error"

                            }

                        },

                        x: {

                            title: {

                                display: true,

                                text: "Model"

                            }

                        }

                    }

                }

            }
        );

}


// ==========================================
// R2 SCORE CHART
// ==========================================

function createModelR2Chart(
    models,
    r2Values
) {

    const canvas =
        document.getElementById(
            "modelR2Chart"
        );


    if (!canvas) {
        return;
    }


    if (
        typeof Chart === "undefined"
    ) {

        console.error(
            "Chart.js is not loaded."
        );

        return;
    }


    const ctx =
        canvas.getContext("2d");


    if (modelR2Chart) {

        modelR2Chart.destroy();

        modelR2Chart = null;
    }


    modelR2Chart =
        new Chart(
            ctx,
            {
                type: "bar",

                data: {

                    labels: models,

                    datasets: [

                        {

                            label: "R² Score",

                            data: r2Values,

                            borderWidth: 1

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            display: false

                        },

                        tooltip: {

                            callbacks: {

                                label: function (
                                    context
                                ) {

                                    return (
                                        "R² Score: " +
                                        Number(
                                            context.raw
                                        ).toFixed(4)
                                    );

                                }

                            }

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            min: 0,

                            max: 1,

                            ticks: {

                                callback: function (
                                    value
                                ) {

                                    return Number(
                                        value
                                    ).toFixed(2);

                                }

                            },

                            title: {

                                display: true,

                                text: "R² Score"

                            }

                        },

                        x: {

                            title: {

                                display: true,

                                text: "Model"

                            }

                        }

                    }

                }

            }
        );

}


// ==========================================
// FORMAT MONTH
// ==========================================

function formatMonth(monthString) {

    if (!monthString) {

        return "Unknown";

    }


    const parts =
        String(monthString).split("-");


    if (parts.length !== 2) {

        return monthString;

    }


    const year =
        parts[0];


    const month =
        Number(parts[1]);


    const monthNames = [

        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December"

    ];


    if (
        month < 1 ||
        month > 12
    ) {

        return monthString;

    }


    return (
        monthNames[month - 1] +
        " " +
        year
    );

}


// ==========================================
// MONTHLY DEMAND CHART
// ==========================================

function createMonthlyChart(monthlyData) {

    const canvas =
        document.getElementById(
            "monthlyDemandChart"
        );


    if (!canvas) {
        return;
    }


    if (
        typeof Chart === "undefined"
    ) {

        console.error(
            "Chart.js is not loaded."
        );

        return;
    }


    if (
        !Array.isArray(monthlyData) ||
        monthlyData.length === 0
    ) {

        return;

    }


    const labels =
        monthlyData.map(
            function (item) {
                return item.date;
            }
        );


    const values =
        monthlyData.map(
            function (item) {
                return Number(item.units);
            }
        );


    const ctx =
        canvas.getContext("2d");


    if (monthlyChart) {

        monthlyChart.destroy();

        monthlyChart = null;
    }


    monthlyChart =
        new Chart(
            ctx,
            {
                type: "line",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Units Sold",

                            data: values,

                            borderWidth: 3,

                            tension: 0.3,

                            fill: true,

                            pointRadius: 3,

                            pointHoverRadius: 6

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    interaction: {

                        intersect: false,

                        mode: "index"

                    },

                    plugins: {

                        legend: {

                            display: true

                        },

                        tooltip: {

                            callbacks: {

                                label: function (
                                    context
                                ) {

                                    return (
                                        "Units Sold: " +
                                        Number(
                                            context.raw
                                        ).toLocaleString(
                                            "en-IN"
                                        )
                                    );

                                }

                            }

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                callback: function (
                                    value
                                ) {

                                    return Number(
                                        value
                                    ).toLocaleString(
                                        "en-IN"
                                    );

                                }

                            }

                        }

                    }

                }

            }
        );

}


// ==========================================
// CATEGORY CHART
// ==========================================

function createCategoryChart(categoryData) {

    const canvas =
        document.getElementById(
            "categoryChart"
        );


    if (!canvas) {
        return;
    }


    if (
        typeof Chart === "undefined"
    ) {

        console.error(
            "Chart.js is not loaded."
        );

        return;
    }


    if (
        !Array.isArray(categoryData) ||
        categoryData.length === 0
    ) {

        return;

    }


    const labels =
        categoryData.map(
            function (item) {
                return item.category;
            }
        );


    const values =
        categoryData.map(
            function (item) {
                return Number(item.units);
            }
        );


    const ctx =
        canvas.getContext("2d");


    if (categoryChart) {

        categoryChart.destroy();

        categoryChart = null;
    }


    categoryChart =
        new Chart(
            ctx,
            {
                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Units Sold",

                            data: values,

                            borderWidth: 1

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {

                        legend: {

                            display: false

                        },

                        tooltip: {

                            callbacks: {

                                label: function (
                                    context
                                ) {

                                    return (
                                        "Units Sold: " +
                                        Number(
                                            context.raw
                                        ).toLocaleString(
                                            "en-IN"
                                        )
                                    );

                                }

                            }

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            ticks: {

                                callback: function (
                                    value
                                ) {

                                    return Number(
                                        value
                                    ).toLocaleString(
                                        "en-IN"
                                    );

                                }

                            }

                        }

                    }

                }

            }
        );

}


// ==========================================
// DEMAND DISTRIBUTION CHART
// ==========================================

function createDemandDistributionChart(
    demandData
) {

    const canvas =
        document.getElementById(
            "demandDistributionChart"
        );


    if (!canvas) {
        return;
    }


    if (
        typeof Chart === "undefined"
    ) {

        console.error(
            "Chart.js is not loaded."
        );

        return;
    }


    if (
        !Array.isArray(demandData) ||
        demandData.length === 0
    ) {

        return;

    }


    const labels =
        demandData.map(
            function (item) {
                return item.level;
            }
        );


    const values =
        demandData.map(
            function (item) {
                return Number(item.count);
            }
        );


    const ctx =
        canvas.getContext("2d");


    if (demandDistributionChart) {

        demandDistributionChart.destroy();

        demandDistributionChart = null;
    }


    demandDistributionChart =
        new Chart(
            ctx,
            {
                type: "doughnut",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label: "Sales Records",

                            data: values,

                            borderWidth: 2

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    cutout: "62%",

                    plugins: {

                        legend: {

                            position: "bottom"

                        },

                        tooltip: {

                            callbacks: {

                                label: function (
                                    context
                                ) {

                                    return (
                                        context.label +
                                        ": " +
                                        Number(
                                            context.raw
                                        ).toLocaleString(
                                            "en-IN"
                                        ) +
                                        " records"
                                    );

                                }

                            }

                        }

                    }

                }

            }
        );

}


// ==========================================
// LSTM DEMAND PREDICTION
// ==========================================

async function predictDemand() {

    const skuElement =
        document.getElementById("sku");


    const button =
        document.getElementById(
            "predictButton"
        );


    const result =
        document.getElementById(
            "predictionResult"
        );


    if (!skuElement) {

        console.error(
            "SKU selection element was not found."
        );

        return;
    }


    if (!button) {

        console.error(
            "Prediction button was not found."
        );

        return;
    }


    if (!result) {

        console.error(
            "Prediction result element was not found."
        );

        return;
    }


    const sku =
        skuElement.value;


    if (!sku) {

        result.innerHTML = `

            <div class="prediction-card">

                <p>
                    Please select an SKU first.
                </p>

            </div>

        `;

        return;
    }


    button.disabled = true;

    button.textContent = "Predicting...";


    result.innerHTML = `

        <div class="prediction-card">

            <p>
                AI model is analyzing the
                latest 30 days of demand...
            </p>

        </div>

    `;


    try {

        const response =
            await fetch(
                "/predict",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({
                            sku: sku
                        })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            result.innerHTML = `

                <div class="prediction-card">

                    <p>
                        Error:
                        ${data.error || "Prediction failed."}
                    </p>

                </div>

            `;

            return;
        }


        result.innerHTML = `

            <div class="prediction-card">

                <h3>
                    ${data.sku}
                </h3>

                <p>

                    Last Available Date:

                    <strong>
                        ${data.last_date}
                    </strong>

                </p>

                <p>

                    Forecast Date:

                    <strong>
                        ${data.forecast_date}
                    </strong>

                </p>

                <p>

                    Predicted Demand:

                    <strong>
                        ${data.predicted_units}
                        units
                    </strong>

                </p>

                <p>

                    Demand Category:

                    <strong>
                        ${data.demand_category}
                    </strong>

                </p>

            </div>

        `;

    }
    catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        result.innerHTML = `

            <div class="prediction-card">

                <p>
                    Unable to connect to
                    the prediction server.
                </p>

            </div>

        `;

    }
    finally {

        button.disabled = false;

        button.textContent =
            "Predict Demand";

    }

}