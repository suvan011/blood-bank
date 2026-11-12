# BloodBridge

A blood donor registration and emergency search system built with Python and Tkinter, made for 21CSC203P Advanced Programming Practice (SRM KTR). It is a front end only: there is no backend, and all donor records and compatibility checks are simulated in memory.

![BloodBridge Interface](docs/screenshot.png)

## Run

```bash
python3 bloodbridge.py
```

It uses only the Python standard library (`tkinter`, `datetime`, `csv`, `re`), so there is nothing to install. On macOS, use a Python from python.org, Homebrew, or uv: Apple's built-in Python ships an old Tk 8.5 that shows a blank window.

## Features

- **Top banner with emergency indicator**: Displays quick rules for universal donor ($O^-$) and universal recipient ($AB^+$).
- **KPI summary cards**: Real-time counters for Total Registered Donors, Ready & Eligible Donors, Donors in Cooldown, Universal Donors ($O^-$), and Active Cities.
- **Search & emergency compatibility filter**: Match donors by exact blood group or by recipient compatibility (e.g. searching for patient $B^+$ displays $B^+$, $B^-$, $O^+$, and $O^-$ donors).
- **Multi-parameter filters**: City/location filter, keyword search (name, phone, email, address), and a toggle to show only ready and eligible donors.
- **Interactive donor directory table**: Custom `ttk.Treeview` with color badges (green for eligible, orange for cooldown, red for ineligible), sortable columns, and row click selection.
- **Donor inspection & action panel**: Detail card for selected donor with buttons to record a blood donation today (resets cooldown to 90 days), edit records, delete records, or export visible records to CSV.
- **Donor registration & edit form**: Clean two-column form with live input validation for age (18–65), minimum weight ($\ge 50\text{ kg}$), contact phone, and donation history date with "First Time Donor" toggle.
- **Compatibility matrix & guidelines**: Reference matrix detailing ABO and Rh red blood cell compatibility, current donor pool distribution, and standard donation criteria.

## Layout

The window has stacked functional bands: header banner, navigation tabs, KPI summary cards, filter controls, donor table, and details action panel. Panels fill a connected grid with clean borders that stretch when the window is resized.

```text
+---------------------------------------------------------------------------------------+
| 🩸 BloodBridge: Blood Donor Registration & Search System    | O- Universal / AB+ Recv |
+---------------------------------------------------------------------------------------+
| [ 🔍 Search & Directory ]   |   [ 📝 Donor Registration ]   |  [ 📊 Compatibility ]   |
+---------------------------------------------------------------------------------------+
| Total: 10  |  Ready & Eligible: 8  |  Cooldown: 2  |  Universal O-: 2  |  Cities: 10  |
+---------------------------------------------------------------------------------------+
| Search: [Blood Group ▼] [◉ Compatible / ○ Exact] [City:       ] [🔍 Search] [↺ Reset] |
+---------------------------------------------------------------------------------------+
| ID  | Full Name      | Blood | Age | Gender | Phone      | City      | Status         |
| 101 | Aarav Sharma   | 🩸 O+ | 28  | Male   | 9876543210 | Mumbai    | Eligible       |
| 102 | Priya Patel    | 🩸 A+ | 24  | Female | 9812345678 | Ahmedabad | Eligible       |
| 103 | Vikram Malhotra| 🩸 O- | 35  | Male   | 9823456789 | Delhi     | Eligible       |
| 104 | Ananya Sengupta| 🩸 B+ | 29  | Female | 9834567890 | Kolkata   | Cooldown (45d) |
| 107 | Kabir Das      | 🩸 B- | 42  | Male   | 9867890123 | Pune      | Cooldown (75d) |
+---------------------------------------------------------------------------------------+
| Selected Donor: Aarav Sharma (O+) | [🩸 Record Donation] [✏️ Edit] [🗑️ Delete] [📥 CSV] |
+---------------------------------------------------------------------------------------+
```

## Project Structure

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── bloodbridge.py      # Standalone Tkinter application (frontend + in-memory store)
└── docs/
    ├── screenshot.png  # Application interface preview
    └── screenshot.svg  # Vector graphics source
```

## Academic Information

- **Course**: 21CSC203P – Advanced Programming Practice
- **Institution**: SRM Institute of Science and Technology, Kattankulathur (SRM KTR)
- **Author**: Raghav Maheshwari
