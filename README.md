# FORESIGHT
## Customer Buying Trends Prediction Dashboard

FORESIGHT is an AI-powered customer purchasing analytics and demand prediction dashboard designed to analyze historical sales data, identify purchasing trends, and predict future product demand.

The project combines data analytics, machine learning, deep learning, and Flask-based web development into a single interactive dashboard.

---

## Project Overview

The objective of FORESIGHT is to transform historical customer and product sales data into useful business insights and future demand predictions.

The system performs four major tasks:

- Historical sales analysis
- Customer and product demand analysis
- Demand prediction using deep learning
- Interactive visualization through a web dashboard

The dashboard allows users to explore sales trends, category performance, demand distribution, model performance, and SKU-level future demand predictions.

---

## Key Features

### 1. Sales Analytics

The dashboard provides important business KPIs including:

- Total Units Sold
- Total Revenue
- Average Unit Price
- Number of Unique SKUs
- Monthly sales trends
- Category-level sales performance

---

### 2. AI-Powered Insights

FORESIGHT automatically identifies important patterns from the sales data, including:

- Highest-performing product category
- Highest-demand month
- Lowest-demand month
- Dominant demand level
- Overall data coverage period

---

### 3. Demand Classification

Sales records are categorized into four demand levels:

| Demand Level | Units Sold |
|--------------|------------|
| Low | 0–5 |
| Medium | 6–10 |
| High | 11–20 |
| Very High | Above 20 |

This classification helps visualize the distribution of product demand.

---

### 4. Machine Learning Models

Two deep learning approaches are included in the project:

#### MLP — Multi-Layer Perceptron

The MLP model uses engineered numerical and time-based features to predict product demand.

Features include:

- Unit price
- Unit cost
- List price
- Product age
- Year
- Month
- Day of week
- Day of month
- Week of year
- Quarter
- Weekend indicator
- Lag features
- Rolling averages
- Rolling standard deviation
- Promotion information
- Discount information

---

#### LSTM — Long Short-Term Memory

The LSTM model is designed to capture sequential demand patterns.

The model uses the latest 30 observations to predict future demand.

LSTM input features include:

- Units sold
- Unit price
- Promotion flag
- Product age
- Day of week
- Month
- Weekend indicator

---

## Model Architecture

### MLP Architecture

```text
Input Layer
     ↓
Dense Layer — 64 neurons
     ↓
Dropout — 20%
     ↓
Dense Layer — 32 neurons
     ↓
Dropout — 20%
     ↓
Dense Layer — 16 neurons
     ↓
Output Layer
     ↓
Predicted Units Sold