document.addEventListener("DOMContentLoaded", function () {

    console.log("FORESIGHT dashboard JavaScript loaded.");

    // ============================================================
    // SYSTEM CLOCK
    // ============================================================

    function updateSystemTime() {

        const systemTime =
            document.getElementById("systemTime");

        if (!systemTime) {

            console.warn(
                "systemTime element not found."
            );

            return;
        }

        const now = new Date();

        const timeString =
            now.toLocaleTimeString(
                "en-IN",
                {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true
                }
            );

        systemTime.textContent =
            timeString;
    }

    updateSystemTime();

    setInterval(
        updateSystemTime,
        1000
    );


    // ============================================================
    // HELPER FUNCTIONS
    // ============================================================

    function setText(
        id,
        value,
        fallback = "--"
    ) {

        const element =
            document.getElementById(id);

        if (!element) {

            console.warn(
                "Element not found:",
                id
            );

            return;
        }

        if (
            value === undefined ||
            value === null ||
            value === ""
        ) {

            element.textContent =
                fallback;

        } else {

            element.textContent =
                value;
        }
    }


    function formatNumber(
        value,
        decimals = 0
    ) {

        if (
            value === undefined ||
            value === null ||
            isNaN(value)
        ) {

            return "--";
        }

        return Number(value).toLocaleString(
            "en-IN",
            {
                minimumFractionDigits:
                    decimals,

                maximumFractionDigits:
                    decimals
            }
        );
    }


    function formatCurrency(value) {

        if (
            value === undefined ||
            value === null ||
            isNaN(value)
        ) {

            return "--";
        }

        return "₹" +
            Number(value).toLocaleString(
                "en-IN",
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            );
    }


    function formatCrore(value) {

        if (
            value === undefined ||
            value === null ||
            isNaN(value)
        ) {

            return "--";
        }

        const crore =
            Number(value) / 10000000;

        return "₹" +
            crore.toLocaleString(
                "en-IN",
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            ) +
            " Cr";
    }


    // ============================================================
    // LOAD ANALYTICS
    // ============================================================

    async function loadAnalytics() {

        try {

            console.log(
                "Loading analytics..."
            );


            const response =
                await fetch(
                    "/analytics?timestamp=" +
                    Date.now(),
                    {
                        method: "GET",
                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Analytics request failed: " +
                    response.status
                );
            }


            const data =
                await response.json();


            console.log(
                "Analytics data received:",
                data
            );


            updateKpis(data);

            updateDataCoverage(data);

            updateInsights(data);

            updateLatestDate(data);

            updateModelPerformance(data);


            // ====================================================
            // CHARTS
            // ====================================================
            // DO NOT MODIFY THESE CHART CALLS.
            // ====================================================

            createMonthlyDemandChart(data);

            createCategoryDemandChart(data);

            createDemandDistributionChart(data);

            createModelErrorChart(data);

            createModelR2Chart(data);


        } catch (error) {

            console.error(
                "Failed to load analytics:",
                error
            );
        }
    }


    // ============================================================
    // KPI SECTION
    // ============================================================

    function updateKpis(data) {

        if (!data || !data.kpis) {

            console.warn(
                "KPI data missing."
            );

            return;
        }


        const kpis =
            data.kpis;


        setText(
            "totalUnits",
            formatNumber(
                kpis.total_units
            )
        );


        setText(
            "totalRevenue",
            formatCrore(
                kpis.total_revenue
            )
        );


        setText(
            "averagePrice",
            formatCurrency(
                kpis.average_unit_price
            )
        );


        setText(
            "totalSkus",
            formatNumber(
                kpis.unique_skus
            )
        );
    }


    // ============================================================
    // DATA COVERAGE
    // ============================================================

    function updateDataCoverage(data) {

        console.log(
            "Updating data coverage..."
        );


        if (!data) {

            console.warn(
                "Analytics data missing for coverage."
            );

            return;
        }


        const coverage =
            data.data_coverage || {};


        const insights =
            data.insights || {};


        console.log(
            "Coverage object:",
            coverage
        );


        console.log(
            "Coverage first date:",
            coverage.first_date
        );


        console.log(
            "Coverage latest date:",
            coverage.latest_date
        );


        // --------------------------------------------------------
        // FIRST DATE
        // --------------------------------------------------------

        const firstDate =
            coverage.first_date ||
            insights.first_date ||
            data.first_date ||
            "--";


        // --------------------------------------------------------
        // LATEST DATE
        // --------------------------------------------------------

        const latestDate =
            coverage.latest_date ||
            insights.latest_date ||
            data.latest_date ||
            "--";


        // --------------------------------------------------------
        // NUMBER OF DAYS
        // --------------------------------------------------------

        const dataDays =
            coverage.data_period_days ||
            insights.data_period_days ||
            data.data_period_days ||
            "--";


        // --------------------------------------------------------
        // DISPLAY RANGE
        // --------------------------------------------------------

        let displayStart =
            coverage.display_start ||
            firstDate;


        let displayEnd =
            coverage.display_end ||
            latestDate;


        // --------------------------------------------------------
        // COVERAGE START
        // --------------------------------------------------------

        setText(
            "coverageStart",
            displayStart
        );


        // --------------------------------------------------------
        // COVERAGE END
        // --------------------------------------------------------

        setText(
            "coverageEnd",
            displayEnd
        );


        // --------------------------------------------------------
        // FIRST AVAILABLE DATA
        // --------------------------------------------------------

        setText(
            "firstDate",
            formatDisplayDate(
                firstDate
            )
        );


        // --------------------------------------------------------
        // LATEST AVAILABLE DATA
        // --------------------------------------------------------

        setText(
            "latestDate",
            formatDisplayDate(
                latestDate
            )
        );


        // --------------------------------------------------------
        // HISTORICAL PERIOD
        // --------------------------------------------------------

        setText(
            "dataDays",
            dataDays !== "--"
                ? formatNumber(
                    dataDays
                ) + " days"
                : "--"
        );


        // --------------------------------------------------------
        // FORECAST NOTE
        // --------------------------------------------------------

        setText(
            "forecastNote",
            coverage.forecast_note ||
            "Forecasts are generated from the latest available historical demand data."
        );


        console.log(
            "Data coverage updated:",
            {
                displayStart,
                displayEnd,
                firstDate,
                latestDate,
                dataDays
            }
        );
    }


    // ============================================================
    // DATE FORMATTER
    // ============================================================

    function formatDisplayDate(dateValue) {

        if (
            !dateValue ||
            dateValue === "--"
        ) {

            return "--";
        }


        // If already formatted, return it

        if (
            typeof dateValue === "string" &&
            (
                dateValue.includes("Jan") ||
                dateValue.includes("Feb") ||
                dateValue.includes("Mar") ||
                dateValue.includes("Apr") ||
                dateValue.includes("May") ||
                dateValue.includes("Jun") ||
                dateValue.includes("Jul") ||
                dateValue.includes("Aug") ||
                dateValue.includes("Sep") ||
                dateValue.includes("Oct") ||
                dateValue.includes("Nov") ||
                dateValue.includes("Dec")
            )
        ) {

            return dateValue;
        }


        const date =
            new Date(dateValue);


        if (
            isNaN(
                date.getTime()
            )
        ) {

            return dateValue;
        }


        return date.toLocaleDateString(
            "en-GB",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );
    }


    // ============================================================
    // LATEST DATA DATE
    // ============================================================

    function updateLatestDate(data) {

        const latestDate =
            data.latest_date ||
            (
                data.data_coverage
                    ? data.data_coverage.latest_date
                    : null
            );


        setText(
            "latestDataDate",
            formatDisplayDate(
                latestDate
            )
        );
    }


    // ============================================================
    // AI BUSINESS INSIGHTS
    // ============================================================

    function updateInsights(data) {

        if (
            !data ||
            !data.insights
        ) {

            console.warn(
                "Insights data missing."
            );

            return;
        }


        const insights =
            data.insights;


        // --------------------------------------------------------
        // HIGHEST DEMAND CATEGORY
        // --------------------------------------------------------

        setText(
            "highestCategory",
            insights.top_category
        );


        setText(
            "highestCategoryValue",
            insights.top_category_units !== undefined
                ? formatNumber(
                    insights.top_category_units
                ) +
                " units sold in this category"
                : "--"
        );


        // --------------------------------------------------------
        // PEAK DEMAND PERIOD
        // --------------------------------------------------------

        setText(
            "peakMonth",
            formatMonthName(
                insights.highest_month
            )
        );


        setText(
            "peakMonthValue",
            insights.highest_month_units !== undefined
                ? formatNumber(
                    insights.highest_month_units
                ) +
                " units sold during this month"
                : "--"
        );


        // --------------------------------------------------------
        // LOWEST DEMAND PERIOD
        // --------------------------------------------------------

        setText(
            "lowestMonth",
            formatMonthName(
                insights.lowest_month
            )
        );


        setText(
            "lowestMonthValue",
            insights.lowest_month_units !== undefined
                ? formatNumber(
                    insights.lowest_month_units
                ) +
                " units sold during this month"
                : "--"
        );


        // --------------------------------------------------------
        // DOMINANT DEMAND
        // --------------------------------------------------------

        setText(
            "dominantDemand",
            insights.dominant_demand
        );


        setText(
            "dominantDemandValue",
            insights.dominant_demand_count !== undefined
                ? formatNumber(
                    insights.dominant_demand_count
                ) +
                " sales records fall into this level"
                : "--"
        );
    }


    // ============================================================
    // MONTH NAME FORMATTER
    // ============================================================

    function formatMonthName(value) {

        if (!value) {

            return "--";
        }


        const date =
            new Date(
                value + "-01"
            );


        if (
            isNaN(
                date.getTime()
            )
        ) {

            return value;
        }


        return date.toLocaleDateString(
            "en-IN",
            {
                month: "long",
                year: "numeric"
            }
        );
    }


    // ============================================================
    // MODEL PERFORMANCE
    // ============================================================

    function updateModelPerformance(data) {

        if (
            !data ||
            !data.model_performance
        ) {

            console.warn(
                "Model performance data missing."
            );

            return;
        }


        const performance =
            data.model_performance;


        setText(
            "within10Accuracy",
            performance.within_10 !== undefined
                ? Number(
                    performance.within_10
                ).toFixed(2) + "%"
                : "--"
        );


        setText(
            "within20Accuracy",
            performance.within_20 !== undefined
                ? Number(
                    performance.within_20
                ).toFixed(2) + "%"
                : "--"
        );
    }


    // ============================================================
    // MONTHLY DEMAND CHART
    // ============================================================

    function createMonthlyDemandChart(data) {

        const canvas =
            document.getElementById(
                "monthlyDemandChart"
            );


        if (!canvas) {

            return;
        }


        if (
            !data.monthly ||
            data.monthly.length === 0
        ) {

            return;
        }


        const labels =
            data.monthly.map(
                item => item.date
            );


        const values =
            data.monthly.map(
                item => item.units
            );


        if (
            window.monthlyDemandChartInstance
        ) {

            window.monthlyDemandChartInstance.destroy();
        }


        window.monthlyDemandChartInstance =
            new Chart(
                canvas,
                {
                    type: "line",

                    data: {
                        labels: labels,

                        datasets: [
                            {
                                label:
                                    "Monthly Units Sold",

                                data: values,

                                tension: 0.35,

                                fill: true
                            }
                        ]
                    },

                    options: {
                        responsive: true,

                        maintainAspectRatio: false,

                        plugins: {
                            legend: {
                                display: false
                            }
                        },

                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                }
            );
    }


    // ============================================================
    // CATEGORY DEMAND CHART
    // ============================================================

    function createCategoryDemandChart(data) {

        const canvas =
            document.getElementById(
                "categoryDemandChart"
            );


        if (!canvas) {

            return;
        }


        if (
            !data.category ||
            data.category.length === 0
        ) {

            return;
        }


        const labels =
            data.category.map(
                item => item.category
            );


        const values =
            data.category.map(
                item => item.units
            );


        if (
            window.categoryDemandChartInstance
        ) {

            window.categoryDemandChartInstance.destroy();
        }


        window.categoryDemandChartInstance =
            new Chart(
                canvas,
                {
                    type: "bar",

                    data: {
                        labels: labels,

                        datasets: [
                            {
                                label:
                                    "Units Sold",

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
                            }
                        },

                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                }
            );
    }


    // ============================================================
    // DEMAND DISTRIBUTION CHART
    // ============================================================

    function createDemandDistributionChart(data) {

        const canvas =
            document.getElementById(
                "demandDistributionChart"
            );


        if (!canvas) {

            return;
        }


        if (
            !data.demand_distribution ||
            data.demand_distribution.length === 0
        ) {

            return;
        }


        const labels =
            data.demand_distribution.map(
                item => item.level
            );


        const values =
            data.demand_distribution.map(
                item => item.count
            );


        if (
            window.demandDistributionChartInstance
        ) {

            window.demandDistributionChartInstance.destroy();
        }


        window.demandDistributionChartInstance =
            new Chart(
                canvas,
                {
                    type: "doughnut",

                    data: {
                        labels: labels,

                        datasets: [
                            {
                                data: values
                            }
                        ]
                    },

                    options: {
                        responsive: true,

                        maintainAspectRatio: false,

                        plugins: {
                            legend: {
                                position: "bottom"
                            }
                        }
                    }
                }
            );
    }


    // ============================================================
    // MODEL ERROR CHART
    // ============================================================

    function createModelErrorChart(data) {

        const canvas =
            document.getElementById(
                "modelErrorChart"
            );


        if (!canvas) {

            return;
        }


        const performance =
            data.model_performance;


        if (!performance) {

            return;
        }


        if (
            window.modelErrorChartInstance
        ) {

            window.modelErrorChartInstance.destroy();
        }


        window.modelErrorChartInstance =
            new Chart(
                canvas,
                {
                    type: "bar",

                    data: {
                        labels:
                            performance.models,

                        datasets: [
                            {
                                label: "MAE",

                                data:
                                    performance.mae
                            },

                            {
                                label: "RMSE",

                                data:
                                    performance.rmse
                            }
                        ]
                    },

                    options: {
                        responsive: true,

                        maintainAspectRatio: false,

                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                }
            );
    }


    // ============================================================
    // MODEL R2 CHART
    // ============================================================

    function createModelR2Chart(data) {

        const canvas =
            document.getElementById(
                "modelR2Chart"
            );


        if (!canvas) {

            return;
        }


        const performance =
            data.model_performance;


        if (!performance) {

            return;
        }


        if (
            window.modelR2ChartInstance
        ) {

            window.modelR2ChartInstance.destroy();
        }


        window.modelR2ChartInstance =
            new Chart(
                canvas,
                {
                    type: "bar",

                    data: {
                        labels:
                            performance.models,

                        datasets: [
                            {
                                label: "R² Score",

                                data:
                                    performance.r2
                            }
                        ]
                    },

                    options: {
                        responsive: true,

                        maintainAspectRatio: false,

                        scales: {
                            y: {
                                beginAtZero: true,

                                max: 1
                            }
                        }
                    }
                }
            );
    }


    // ============================================================
    // SKU PREDICTION
    // ============================================================

    const predictButton =
        document.getElementById(
            "predictButton"
        );


    if (predictButton) {

        predictButton.addEventListener(
            "click",
            async function () {

                const skuSelect =
                    document.getElementById(
                        "sku"
                    );


                if (!skuSelect) {

                    console.error(
                        "SKU selector not found."
                    );

                    return;
                }


                const sku =
                    skuSelect.value;


                if (!sku) {

                    alert(
                        "Please select an SKU first."
                    );

                    return;
                }


                try {

                    // ------------------------------------------------
                    // BUTTON LOADING STATE
                    // ------------------------------------------------

                    predictButton.disabled =
                        true;


                    predictButton.textContent =
                        "Predicting...";


                    console.log(
                        "Predicting SKU:",
                        sku
                    );


                    // ------------------------------------------------
                    // SEND REQUEST
                    // ------------------------------------------------

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


                    const result =
                        await response.json();


                    console.log(
                        "Prediction result:",
                        result
                    );


                    if (!response.ok) {

                        throw new Error(
                            result.error ||
                            "Prediction failed."
                        );
                    }


                    // ------------------------------------------------
                    // DISPLAY RESULT
                    // ------------------------------------------------

                    displayPrediction(
                        result
                    );


                } catch (error) {

                    console.error(
                        "Prediction error:",
                        error
                    );


                    alert(
                        error.message
                    );


                } finally {

                    predictButton.disabled =
                        false;


                    predictButton.textContent =
                        "Predict Demand";
                }
            }
        );
    }


    // ============================================================
    // DISPLAY PREDICTION
    // ============================================================

    function displayPrediction(result) {

        console.log(
            "Displaying prediction cards:",
            result
        );


        // --------------------------------------------------------
        // SHOW PREDICTION DETAILS
        // --------------------------------------------------------

        const predictionDetails =
            document.getElementById(
                "predictionDetails"
            );


        if (predictionDetails) {

            predictionDetails.style.display =
                "block";

            predictionDetails.hidden =
                false;
        }


        // --------------------------------------------------------
        // SUCCESS MESSAGE
        // --------------------------------------------------------

        const predictionResult =
            document.getElementById(
                "predictionResult"
            );


        if (predictionResult) {

            predictionResult.innerHTML = `
                <div class="prediction-success">
                    <strong>Forecast generated successfully</strong>
                    for ${result.sku}.
                </div>
            `;
        }


        // --------------------------------------------------------
        // BASIC FORECAST
        // --------------------------------------------------------

        setText(
            "predictionSku",
            result.sku
        );


        setText(
            "predictedUnits",
            formatNumber(
                result.predicted_units
            )
        );


        setText(
            "lastAvailableDate",
            formatDisplayDate(
                result.last_date
            )
        );


        setText(
            "forecastDate",
            formatDisplayDate(
                result.forecast_date
            )
        );


        setText(
            "demandCategory",
            result.demand_category
        );


        // --------------------------------------------------------
        // INVENTORY INTELLIGENCE
        // --------------------------------------------------------

        const inventory =
            result.inventory_intelligence;


        if (!inventory) {

            console.warn(
                "Inventory intelligence missing."
            );

            return;
        }


        // --------------------------------------------------------
        // RISK LEVEL
        // --------------------------------------------------------

        setText(
            "riskLevel",
            inventory.risk_level
        );


        // --------------------------------------------------------
        // RISK SCORE
        // --------------------------------------------------------

        setText(
            "riskScore",
            formatNumber(
                inventory.risk_score,
                2
            )
        );


        // --------------------------------------------------------
        // INVENTORY RISK TYPE
        // --------------------------------------------------------

        setText(
            "inventoryRiskType",
            inventory.risk_type
        );


        // --------------------------------------------------------
        // DEMAND TREND
        // --------------------------------------------------------

        setText(
            "demandTrend",
            inventory.demand_trend
        );


        // --------------------------------------------------------
        // DEMAND PRESSURE
        // --------------------------------------------------------

        setText(
            "demandPressure",
            inventory.demand_pressure
        );


        // --------------------------------------------------------
        // 7-DAY DEMAND
        // --------------------------------------------------------

        setText(
            "sevenDayDemand",
            formatNumber(
                inventory.rolling_mean_7,
                2
            )
        );


        // --------------------------------------------------------
        // SAFETY STOCK
        // --------------------------------------------------------

        setText(
            "safetyStock",
            formatNumber(
                inventory.safety_stock,
                2
            )
        );


        // --------------------------------------------------------
        // RECOMMENDED INVENTORY
        // --------------------------------------------------------

        setText(
            "recommendedInventory",
            formatNumber(
                inventory.recommended_inventory_target,
                2
            )
        );


        // --------------------------------------------------------
        // DEMAND VOLATILITY
        // --------------------------------------------------------

        setText(
            "demandVolatility",
            inventory.volatility_pct !== undefined
                ? Number(
                    inventory.volatility_pct
                ).toFixed(2) + "%"
                : "--"
        );


        // --------------------------------------------------------
        // RECENT DEMAND CHANGE
        // --------------------------------------------------------

        setText(
            "recentDemandChange",
            inventory.demand_change_pct !== undefined
                ? Number(
                    inventory.demand_change_pct
                ).toFixed(2) + "%"
                : "--"
        );


        // --------------------------------------------------------
        // INVENTORY RECOMMENDATION
        // --------------------------------------------------------

        setText(
            "inventoryRecommendation",
            inventory.recommendation
        );


        // --------------------------------------------------------
        // DATA LIMITATION
        // --------------------------------------------------------

        setText(
            "inventoryDataLimitation",
            inventory.data_limitation
        );


        // --------------------------------------------------------
        // SCROLL TO PREDICTION
        // --------------------------------------------------------

        if (predictionDetails) {

            predictionDetails.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    }


    // ============================================================
    // START DASHBOARD
    // ============================================================

    loadAnalytics();

});