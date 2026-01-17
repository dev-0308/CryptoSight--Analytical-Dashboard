# CryptoBoard--Analytical-Dashboard

## Table of Contents
- [Project Overview](#project-overview)
- [Objectives](#objectives)
- [Key Features](#key-features)
- [Installation](#installation)
- [Usage](#usage)
- [Future Work](#future-work)
- [Disclaimer](#disclaimer)
- [Author](#author)

## Project Overview
CryptoBoard is an interactive cryptocurrency analytics dashboard developed using Python. The application fetches historical cryptocurrency market data from a public API, stores it locally using SQLite, and presents analytical insights through a web-based dashboard. The project demonstrates an end-to-end data analytics workflow including data ingestion, storage, processing, visualization, and basic predictive analysis.

## Objectives
- Build an end-to-end analytics application using Python  
- Fetch and persist real-world cryptocurrency market data  
- Visualize historical price trends interactively  
- Apply a basic machine learning technique for trend estimation  
- Enable users to export filtered datasets for further analysis  

## Key Features
- Historical price visualization for selected cryptocurrencies  
- Persistent local storage using SQLite  
- Time-based data filtering (7, 30, 180, 365 days)  
- Linear regression–based trend estimation using historical prices  
- Interactive charts created with Plotly  
- Tabular data view with pagination  
- CSV export of filtered data  
- Web-based dashboard built using Panel  

## Installation
### Prerequisites
- Python 3.10 or higher  
- Internet connection for fetching market data  

### Setup Instructions
1. Clone the repository  
   git clone https://github.com/your-username/cryptosight-dashboard.git  
   cd cryptosight-dashboard  

2. Create a virtual environment  
   python -m venv venv  

3. Activate the virtual environment  

   Windows  
   venv\Scripts\activate  

   macOS / Linux  
   source venv/bin/activate  

4. Install dependencies  
   pip install -r requirements.txt  

## Usage
1. Run the application  

2. The dashboard will open automatically in your default web browser.

3. Use the controls to select a cryptocurrency and time duration.

4. View price trends, analytical insights, and historical data in tabular format.

5. Export the filtered dataset using the CSV download option.

## Future Work
- Implement multi-cryptocurrency comparison within a single dashboard  
- Add technical indicators such as moving averages and volatility  
- Improve forecasting using advanced time-series models  
- Introduce user authentication and personalized dashboards  
- Deploy the application on a cloud platform  
- Build a Streamlit-based version for broader accessibility  

## Disclaimer
This project is intended for educational and analytical purposes only. It does not constitute financial or investment advice.

## Author
Dev Tyagi  
BCA Graduate | Aspiring Data / Business Analyst
