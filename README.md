# 🔧 Sparepart Lifetime Dashboard 📊

## 🌟 Project Overview

This Streamlit-based dashboard helps track and monitor spare part lifetimes across different machines, providing a comprehensive view of spare part management and maintenance schedules.

## ✨ Features

### 🖥️ Dashboard Capabilities
- **Machine-Specific Tracking**: Monitor spare parts for multiple machine types
- **KPI Summary**: Quick overview of spare part statistics
- **Urgent Notifications**: Highlight critical and overdue parts
- **Visualization**: Bar chart showing part overdue by machine

### 🔍 Key Functionalities
- Filter spare parts by status
- Search and filter vital parts
- Track replacement schedules
- Visualize part replacement trends

## 🛠️ Technologies Used
- Python
- Streamlit
- Pandas
- Plotly
- Google Sheets API
- Google Cloud Services

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Streamlit
- Google Cloud Service Account

### Setup Steps
1. Clone the repository
```bash
git clone https://github.com/your-username/sparepart-lifetime-dashboard.git
cd sparepart-lifetime-dashboard
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure Google Sheets Credentials
- Create a `.streamlit/secrets.toml` file
- Add your Google Cloud service account credentials

4. Run the application
```bash
streamlit run app/main.py
```

## 📋 Configuration

### 🔑 Key Configuration Files
- `config.py`: Application settings and constants
- `.streamlit/secrets.toml`: Google Sheets credentials
- `app/config.py`: Machine options and page configurations

## 📊 Data Structure
- Mesin (Machine)
- Kode Part (Part Code)
- Part
- Qty
- Category
- Lifetime (Bulan)
- Penggantian Terakhir (Last Replacement)
- Penggantian Selanjutnya (Next Replacement)
- STATUS
- Leadtime (Hari)

## 🔒 Security
- Uses service account authentication
- Minimal API requests
- Cached data loading
