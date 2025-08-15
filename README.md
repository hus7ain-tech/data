# 🚗 Vehicle Registration Analysis Dashboard

An interactive dashboard built with **Streamlit** to analyze vehicle registration data from an **investor's perspective**.  
It provides key metrics like **Year-over-Year (YoY)**, **Quarter-over-Quarter (QoQ)**, and **Month-over-Month (MoM)** growth to help stakeholders understand market trends.

---

## 🔧 Setup Instructions

### **Prerequisites**# 🚗 Vehicle Registration Analysis Dashboard

An interactive dashboard built with **Streamlit** to analyze vehicle registration data from an **investor's perspective**.
It provides key metrics like **Year-over-Year (YoY)**, **Quarter-over-Quarter (QoQ)**, and **Month-over-Month (MoM)** growth to help stakeholders understand market trends.

---

## 🔧 Setup Instructions

To run this dashboard locally, follow these steps:

### **Prerequisites**
- Python **3.7+**
- `pip` package manager

---

### **1. Clone the Repository**
Get all the project files, including the `dashboard.py` script and the data folders.

### **2. Install Required Libraries**
Open your terminal or command prompt and run the following command to install the necessary Python packages:
```bash
pip install streamlit pandas plotly-express
```

### **3. Organize Your Data**
Ensure your data files are organized in the correct folder structure. The script expects to find the data in year-specific folders, which should be in the same directory as the `dashboard.py` script.
```
.
├── 2023/
│   ├── 2023-JAN.csv
│   ├── 2023-FEB.csv
│   └── ...
├── 2024/
│   ├── 2024-JAN.csv
│   └── ...
├── 2025/
│   └── ...
└── dashboard.py
```

### **4. Run the Application**
Navigate to the project's root directory in your terminal and run the following command:
```bash
streamlit run dashboard.py
```
A new tab should automatically open in your web browser with the running application.

---

## 📊 Data Assumptions

The application makes the following assumptions about the data:

- **File Naming Convention**: Data for each month is stored in a separate CSV file named in the format `YYYY-MON.csv` (e.g., `2024-JAN.csv`, `2024-FEB.csv`).
- **Folder Structure**: The CSV files are located inside folders named after the corresponding year (e.g., all 2024 files are in a folder named `2024`).
- **CSV File Content**: Each CSV file must contain the following columns:
  - `Maker`: The name of the vehicle manufacturer.
  - `2W`: The number of two-wheeler registrations.
  - `3W`: The number of three-wheeler registrations.
  - `4W`: The number of four-wheeler registrations.

---

## 🗺️ Feature Roadmap

If this project were to be continued, here are some potential features and improvements that could be added:

### **Advanced Manufacturer Analysis**
- Calculate and visualize changes in market share over time for each manufacturer.

### **Geographic Analysis**
- If state-level data becomes available, add a map visualization to show registration hotspots.
- Filters to drill down into specific states or regions.


### **Fuel Type Analysis**
- Incorporate data on fuel types (Petrol, Diesel, EV) to track the adoption of electric vehicles.
- Add filters and charts to compare EV vs. ICE vehicle registration trends.


### **Technical Improvements**
- Deploy the application to a cloud service (like Streamlit Community Cloud or AWS) for public access.
- Set up a more robust data pipeline to automatically fetch and update the data from the Vahan Dashboard source.

  

