# Google Sheet ID
SHEET_ID = "14d7-QMAdXBvCtVO-XKqHGZdtl6HrthCb2tqQoUXPOCk"

# Machine options
MACHINE_OPTIONS = ["ILAPAK", "SIG", "CHIMEI", "JINSUNG", "UNIFILL"]

# Status filter options
STATUS_OPTIONS = ["Semua", "Segera Jadwalkan Penggantian", "Segera Lakukan Pemesanan"]

# Required columns for dataframe
REQUIRED_COLUMNS = [
    "Mesin",
    "Kode Part",
    "Part",
    "Qty",
    "Category",
    "Lifetime (Bulan)",
    "Penggantian Terakhir",
    "Penggantian Selanjutnya",
    "STATUS",
    "Leadtime (Hari)",
]

# Page config
PAGE_CONFIG = {
    "page_title": "Dashboard Database Lifetime",
    "page_icon": ":eye:",
    "layout": "wide",
}
