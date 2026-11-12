#!/usr/bin/env python3
"""
Blood Donor Registration and Search System
A standalone Tkinter GUI application.
Zero external dependencies required - standard Python library only.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import csv
import re

# ==============================================================================
# BLOOD COMPATIBILITY & ELIGIBILITY RULES
# ==============================================================================

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# For a recipient of a given blood group, who can donate to them?
RECIPIENT_CAN_RECEIVE_FROM = {
    "O-": ["O-"],
    "O+": ["O+", "O-"],
    "A-": ["A-", "O-"],
    "A+": ["A+", "A-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "AB-": ["AB-", "A-", "B-", "O-"],
    "AB+": ["AB+", "AB-", "A+", "A-", "B+", "B-", "O+", "O-"],
}

# For a donor of a given blood group, who can they donate to?
DONOR_CAN_GIVE_TO = {
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],
}

DONATION_COOLDOWN_DAYS = 90
MIN_DONOR_AGE = 18
MAX_DONOR_AGE = 65
MIN_DONOR_WEIGHT_KG = 50.0


def check_eligibility(last_donation_date_str, age, weight=0.0, is_available=True):
    """Computes donor eligibility: (is_eligible, status_text, days_since_last)"""
    if not is_available:
        return False, "Unavailable", None
    if age < MIN_DONOR_AGE:
        return False, f"Underage (<{MIN_DONOR_AGE})", None
    if age > MAX_DONOR_AGE:
        return False, f"Overage (>{MAX_DONOR_AGE})", None
    if weight and weight < MIN_DONOR_WEIGHT_KG:
        return False, f"Underweight (<{MIN_DONOR_WEIGHT_KG}kg)", None
    if not last_donation_date_str:
        return True, "Eligible (First Time)", None

    try:
        last_dt = datetime.strptime(last_donation_date_str.strip(), "%Y-%m-%d").date()
        days_passed = (date.today() - last_dt).days
        if days_passed < 0:
            return False, "Invalid Future Date", None
        if days_passed >= DONATION_COOLDOWN_DAYS:
            return True, f"Eligible ({days_passed}d ago)", days_passed
        else:
            days_left = DONATION_COOLDOWN_DAYS - days_passed
            return False, f"Cooldown ({days_left}d left)", days_passed
    except ValueError:
        return True, "Eligible", None


# ==============================================================================
# IN-MEMORY DATA STORE & INITIAL SAMPLE DATA
# ==============================================================================

def get_initial_donors():
    today = date.today()
    d_120 = (today - timedelta(days=120)).strftime("%Y-%m-%d")
    d_45 = (today - timedelta(days=45)).strftime("%Y-%m-%d")
    d_200 = (today - timedelta(days=200)).strftime("%Y-%m-%d")
    d_15 = (today - timedelta(days=15)).strftime("%Y-%m-%d")

    return [
        {
            "id": 101,
            "full_name": "Aarav Sharma",
            "age": 28,
            "gender": "Male",
            "blood_group": "O+",
            "phone": "9876543210",
            "email": "aarav.sharma@example.com",
            "city": "Mumbai",
            "address": "402 Palm Heights, Andheri West",
            "last_donation_date": d_120,
            "weight_kg": 72.0,
            "is_available": True,
            "medical_notes": "Regular voluntary donor, non-smoker",
        },
        {
            "id": 102,
            "full_name": "Priya Patel",
            "age": 24,
            "gender": "Female",
            "blood_group": "A+",
            "phone": "9812345678",
            "email": "priya.patel@example.com",
            "city": "Ahmedabad",
            "address": "12 Shanti Nagar, Navrangpura",
            "last_donation_date": "",
            "weight_kg": 55.0,
            "is_available": True,
            "medical_notes": "First-time registered donor",
        },
        {
            "id": 103,
            "full_name": "Vikram Malhotra",
            "age": 35,
            "gender": "Male",
            "blood_group": "O-",
            "phone": "9823456789",
            "email": "vikram.m@example.com",
            "city": "Delhi",
            "address": "B-14 Hauz Khas",
            "last_donation_date": d_200,
            "weight_kg": 81.0,
            "is_available": True,
            "medical_notes": "Universal donor, ready for critical emergencies",
        },
        {
            "id": 104,
            "full_name": "Ananya Sengupta",
            "age": 29,
            "gender": "Female",
            "blood_group": "B+",
            "phone": "9834567890",
            "email": "ananya.s@example.com",
            "city": "Kolkata",
            "address": "88 Salt Lake Sector 1",
            "last_donation_date": d_45,
            "weight_kg": 59.0,
            "is_available": True,
            "medical_notes": "Donated at Red Cross blood drive",
        },
        {
            "id": 105,
            "full_name": "Rohan Iyer",
            "age": 31,
            "gender": "Male",
            "blood_group": "AB+",
            "phone": "9845678901",
            "email": "rohan.iyer@example.com",
            "city": "Bengaluru",
            "address": "25 Indiranagar 100ft Road",
            "last_donation_date": d_120,
            "weight_kg": 76.0,
            "is_available": True,
            "medical_notes": "Universal plasma donor",
        },
        {
            "id": 106,
            "full_name": "Sneha Reddy",
            "age": 22,
            "gender": "Female",
            "blood_group": "A-",
            "phone": "9856789012",
            "email": "sneha.reddy@example.com",
            "city": "Hyderabad",
            "address": "Plot 54 Jubilee Hills",
            "last_donation_date": "",
            "weight_kg": 53.5,
            "is_available": True,
            "medical_notes": "Youth volunteer club member",
        },
        {
            "id": 107,
            "full_name": "Kabir Das",
            "age": 42,
            "gender": "Male",
            "blood_group": "B-",
            "phone": "9867890123",
            "email": "kabir.das@example.com",
            "city": "Pune",
            "address": "15 Koregaon Park",
            "last_donation_date": d_15,
            "weight_kg": 68.0,
            "is_available": True,
            "medical_notes": "Currently in donation cooldown period",
        },
        {
            "id": 108,
            "full_name": "Meera Nair",
            "age": 27,
            "gender": "Female",
            "blood_group": "AB-",
            "phone": "9878901234",
            "email": "meera.nair@example.com",
            "city": "Chennai",
            "address": "102 Anna Nagar West",
            "last_donation_date": d_200,
            "weight_kg": 57.0,
            "is_available": True,
            "medical_notes": "Rare blood group registered",
        },
        {
            "id": 109,
            "full_name": "David Fernandes",
            "age": 38,
            "gender": "Male",
            "blood_group": "O+",
            "phone": "9889012345",
            "email": "david.f@example.com",
            "city": "Panaji",
            "address": "34 Miramar Beach Road",
            "last_donation_date": d_120,
            "weight_kg": 77.0,
            "is_available": True,
            "medical_notes": "Available on call on weekends",
        },
        {
            "id": 110,
            "full_name": "Sunita Verma",
            "age": 45,
            "gender": "Female",
            "blood_group": "O-",
            "phone": "9890123456",
            "email": "sunita.verma@example.com",
            "city": "Jaipur",
            "address": "8 Vaishali Nagar",
            "last_donation_date": "",
            "weight_kg": 64.0,
            "is_available": True,
            "medical_notes": "Universal donor, willing to donate locally",
        },
    ]


# ==============================================================================
# MAIN TKINTER APPLICATION CLASS
# ==============================================================================

class BloodDonorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Blood Donor Registration and Search System")
        self.geometry("1180x760")
        self.minsize(980, 640)

        # In-memory storage
        self.donors = get_initial_donors()
        self.next_id = 111
        self.editing_donor_id = None
        self.sort_column = "id"
        self.sort_reverse = False

        self._configure_styles()
        self._build_header()
        self._build_tabs()

        # Initial render
        self.refresh_search_results()
        self.update_statistics_cards()

    # --------------------------------------------------------------------------
    # Styling Configuration
    # --------------------------------------------------------------------------
    def _configure_styles(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        # Color Palette
        self.COLOR_PRIMARY = "#C62828"       # Deep Crimson Red
        self.COLOR_PRIMARY_DARK = "#8E0000"  # Dark Red
        self.COLOR_SECONDARY = "#37474F"     # Blue Grey
        self.COLOR_BG = "#F5F7FA"            # Soft background
        self.COLOR_CARD_BG = "#FFFFFF"       # White card
        self.COLOR_ACCENT = "#2E7D32"        # Emerald Green
        self.COLOR_TEXT = "#212121"          # Text Dark

        self.configure(bg=self.COLOR_BG)

        # Notebook (Tabs) styling
        self.style.configure("TNotebook", background=self.COLOR_BG, borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            font=("Helvetica", 11, "bold"),
            padding=[16, 8],
            background="#E0E0E0",
            foreground="#37474F",
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.COLOR_PRIMARY)],
            foreground=[("selected", "#FFFFFF")],
        )

        # Buttons
        self.style.configure(
            "Primary.TButton",
            font=("Helvetica", 10, "bold"),
            background=self.COLOR_PRIMARY,
            foreground="#FFFFFF",
            padding=[12, 6],
            borderwidth=0,
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", self.COLOR_PRIMARY_DARK)],
            foreground=[("active", "#FFFFFF")],
        )

        self.style.configure(
            "Success.TButton",
            font=("Helvetica", 10, "bold"),
            background=self.COLOR_ACCENT,
            foreground="#FFFFFF",
            padding=[14, 7],
            borderwidth=0,
        )
        self.style.map(
            "Success.TButton",
            background=[("active", "#1B5E20")],
            foreground=[("active", "#FFFFFF")],
        )

        self.style.configure(
            "Secondary.TButton",
            font=("Helvetica", 10),
            background="#607D8B",
            foreground="#FFFFFF",
            padding=[10, 5],
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#455A64")],
            foreground=[("active", "#FFFFFF")],
        )

        # Treeview styling
        self.style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground="#212121",
            rowheight=28,
            fieldbackground="#FFFFFF",
            font=("Helvetica", 10),
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Helvetica", 10, "bold"),
            background="#ECEFF1",
            foreground="#263238",
            padding=[6, 6],
        )
        self.style.map("Treeview", background=[("selected", "#FFE0B2")], foreground=[("selected", "#000000")])

    # --------------------------------------------------------------------------
    # Header Section
    # --------------------------------------------------------------------------
    def _build_header(self):
        header_frame = tk.Frame(self, bg=self.COLOR_PRIMARY, height=72)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title_box = tk.Frame(header_frame, bg=self.COLOR_PRIMARY)
        title_box.pack(side=tk.LEFT, padx=20, pady=10)

        title_lbl = tk.Label(
            title_box,
            text="🩸 Blood Donor Registration & Search System",
            font=("Helvetica", 18, "bold"),
            bg=self.COLOR_PRIMARY,
            fg="#FFFFFF",
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            title_box,
            text="Connecting donors with patients in need • Real-time compatibility & eligibility matching",
            font=("Helvetica", 10),
            bg=self.COLOR_PRIMARY,
            fg="#FFCDD2",
        )
        subtitle_lbl.pack(anchor="w")

        # Top-right quick emergency indicator
        badge_frame = tk.Frame(header_frame, bg="#8E0000", padx=12, pady=6)
        badge_frame.pack(side=tk.RIGHT, padx=20, pady=12)

        emergency_badge = tk.Label(
            badge_frame,
            text="⚡ Universal Donor: O- | Universal Recipient: AB+",
            font=("Helvetica", 10, "bold"),
            bg="#8E0000",
            fg="#FFFFFF",
        )
        emergency_badge.pack()

    # --------------------------------------------------------------------------
    # Tabs Setup
    # --------------------------------------------------------------------------
    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=14, pady=10)

        # Tab 1: Search & Donor Directory
        self.tab_search = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.notebook.add(self.tab_search, text="  🔍 Search & Directory  ")
        self._build_search_tab()

        # Tab 2: Donor Registration & Edit Form
        self.tab_register = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.notebook.add(self.tab_register, text="  📝 Donor Registration  ")
        self._build_register_tab()

        # Tab 3: Compatibility Guide & Statistics
        self.tab_matrix = tk.Frame(self.notebook, bg=self.COLOR_BG)
        self.notebook.add(self.tab_matrix, text="  📊 Compatibility Matrix & Stats  ")
        self._build_matrix_tab()

    # ==========================================================================
    # TAB 1: SEARCH & DIRECTORY
    # ==========================================================================
    def _build_search_tab(self):
        # 1. KPI Stats Summary Bar
        self.stats_bar = tk.Frame(self.tab_search, bg=self.COLOR_BG)
        self.stats_bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(6, 4))
        self._build_kpi_cards()

        # 2. Filter / Search Control Card
        search_card = tk.LabelFrame(
            self.tab_search,
            text=" Donor Search & Emergency Compatibility Filter ",
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_CARD_BG,
            fg=self.COLOR_PRIMARY,
            padx=14,
            pady=10,
            bd=1,
            relief=tk.SOLID,
        )
        search_card.pack(side=tk.TOP, fill=tk.X, padx=10, pady=4)

        # Row 1 of search: Blood Group + Mode + City + Search query
        r1 = tk.Frame(search_card, bg=self.COLOR_CARD_BG)
        r1.pack(fill=tk.X, pady=2)

        # Blood group selector
        tk.Label(r1, text="Blood Group:", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(side=tk.LEFT, padx=(0, 4))
        self.search_blood_var = tk.StringVar(value="All")
        blood_cb = ttk.Combobox(
            r1,
            textvariable=self.search_blood_var,
            values=["All"] + BLOOD_GROUPS,
            width=7,
            state="readonly",
            font=("Helvetica", 10),
        )
        blood_cb.pack(side=tk.LEFT, padx=(0, 15))
        blood_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_search_results())

        # Match mode: Exact vs Compatible
        self.search_mode_var = tk.StringVar(value="compatible")
        rb_comp = tk.Radiobutton(
            r1,
            text="Show All Compatible Donors (For Recipient)",
            variable=self.search_mode_var,
            value="compatible",
            bg=self.COLOR_CARD_BG,
            activebackground=self.COLOR_CARD_BG,
            font=("Helvetica", 10),
            command=self.refresh_search_results,
        )
        rb_comp.pack(side=tk.LEFT, padx=(0, 10))

        rb_exact = tk.Radiobutton(
            r1,
            text="Exact Group Only",
            variable=self.search_mode_var,
            value="exact",
            bg=self.COLOR_CARD_BG,
            activebackground=self.COLOR_CARD_BG,
            font=("Helvetica", 10),
            command=self.refresh_search_results,
        )
        rb_exact.pack(side=tk.LEFT, padx=(0, 20))

        # City Filter
        tk.Label(r1, text="City / Area:", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(side=tk.LEFT, padx=(0, 4))
        self.search_city_var = tk.StringVar()
        city_entry = ttk.Entry(r1, textvariable=self.search_city_var, width=14, font=("Helvetica", 10))
        city_entry.pack(side=tk.LEFT, padx=(0, 15))
        city_entry.bind("<Return>", lambda e: self.refresh_search_results())

        # Row 2 of search: Keyword search + Eligibility Check + Buttons
        r2 = tk.Frame(search_card, bg=self.COLOR_CARD_BG)
        r2.pack(fill=tk.X, pady=(6, 2))

        tk.Label(r2, text="Keyword Search:", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(side=tk.LEFT, padx=(0, 4))
        self.search_query_var = tk.StringVar()
        q_entry = ttk.Entry(r2, textvariable=self.search_query_var, width=22, font=("Helvetica", 10))
        q_entry.pack(side=tk.LEFT, padx=(0, 15))
        q_entry.bind("<Return>", lambda e: self.refresh_search_results())

        # Checkbox: Only Eligible Donors
        self.filter_eligible_var = tk.BooleanVar(value=False)
        cb_eligible = tk.Checkbutton(
            r2,
            text="Only Ready & Eligible Donors (>=90d cooldown)",
            variable=self.filter_eligible_var,
            bg=self.COLOR_CARD_BG,
            activebackground=self.COLOR_CARD_BG,
            font=("Helvetica", 10, "bold"),
            fg="#2E7D32",
            command=self.refresh_search_results,
        )
        cb_eligible.pack(side=tk.LEFT, padx=(0, 15))

        # Search & Reset buttons
        btn_search = ttk.Button(r2, text="🔍 Search Donors", style="Primary.TButton", command=self.refresh_search_results)
        btn_search.pack(side=tk.LEFT, padx=4)

        btn_reset = ttk.Button(r2, text="↺ Reset Filters", style="Secondary.TButton", command=self.reset_filters)
        btn_reset.pack(side=tk.LEFT, padx=4)

        # 3. Main Split View: Treeview on top, Details & Actions Card on bottom
        content_pane = tk.PanedWindow(self.tab_search, orient=tk.VERTICAL, bg=self.COLOR_BG, sashwidth=4)
        content_pane.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=4)

        # Top frame: Table container
        table_frame = tk.Frame(content_pane, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        content_pane.add(table_frame, minsize=200, stretch="always")

        # Treeview setup
        columns = ("id", "name", "blood", "age", "gender", "phone", "city", "last_donated", "status", "avail")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        col_config = [
            ("id", "ID", 50, tk.CENTER),
            ("name", "Full Name", 160, tk.W),
            ("blood", "Blood Group", 95, tk.CENTER),
            ("age", "Age", 55, tk.CENTER),
            ("gender", "Gender", 75, tk.CENTER),
            ("phone", "Contact Phone", 115, tk.W),
            ("city", "City / Area", 120, tk.W),
            ("last_donated", "Last Donation", 110, tk.CENTER),
            ("status", "Eligibility Status", 145, tk.W),
            ("avail", "Available", 85, tk.CENTER),
        ]

        for col_id, heading, width, align in col_config:
            self.tree.heading(col_id, text=heading, command=lambda c=col_id: self._sort_by_column(c))
            self.tree.column(col_id, width=width, anchor=align)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Row tag colors
        self.tree.tag_configure("eligible", background="#F1F8E9")  # subtle light green
        self.tree.tag_configure("cooldown", background="#FFF3E0")  # subtle amber
        self.tree.tag_configure("ineligible", background="#FFEBEE") # subtle red

        self.tree.bind("<<TreeviewSelect>>", self._on_donor_selected)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected_donor())

        # Bottom frame: Selected Donor Detail Card & Quick Actions
        bottom_frame = tk.Frame(content_pane, bg=self.COLOR_CARD_BG, bd=1, relief=tk.SOLID)
        content_pane.add(bottom_frame, minsize=140, stretch="never")

        self._build_donor_detail_panel(bottom_frame)

    def _build_kpi_cards(self):
        """Builds clean summary count cards across the top."""
        for widget in self.stats_bar.winfo_children():
            widget.destroy()

        stats = self._compute_stats()

        kpi_data = [
            ("👥 Total Registered Donors", str(stats["total"]), "#1565C0"),
            ("✅ Ready & Eligible Donors", str(stats["eligible"]), "#2E7D32"),
            ("⏳ Donors in Cooldown", str(stats["cooldown"]), "#E65100"),
            ("🩸 Universal Donors (O-)", str(stats["o_negative"]), "#C62828"),
            ("🏙️ Active Cities", str(stats["cities_count"]), "#455A64"),
        ]

        for i, (title, val, color) in enumerate(kpi_data):
            card = tk.Frame(self.stats_bar, bg=self.COLOR_CARD_BG, bd=1, relief=tk.SOLID, padx=12, pady=6)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            lbl_title = tk.Label(card, text=title, font=("Helvetica", 9), bg=self.COLOR_CARD_BG, fg="#546E7A")
            lbl_title.pack(anchor="w")

            lbl_val = tk.Label(card, text=val, font=("Helvetica", 15, "bold"), bg=self.COLOR_CARD_BG, fg=color)
            lbl_val.pack(anchor="w")

    def _build_donor_detail_panel(self, parent):
        """Detail inspection card and quick action buttons for selected donor."""
        top_bar = tk.Frame(parent, bg="#ECEFF1", padx=10, pady=4)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        self.detail_header_lbl = tk.Label(
            top_bar,
            text="👤 Selected Donor Information (Select a donor from the table to preview & manage)",
            font=("Helvetica", 10, "bold"),
            bg="#ECEFF1",
            fg="#263238",
        )
        self.detail_header_lbl.pack(side=tk.LEFT)

        # Action Buttons on the right of detail bar
        actions_frame = tk.Frame(parent, bg=self.COLOR_CARD_BG, padx=10, pady=6)
        actions_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.btn_donate_today = ttk.Button(
            actions_frame, text="🩸 Record Donation Today", style="Success.TButton", command=self.record_donation_today
        )
        self.btn_donate_today.pack(side=tk.LEFT, padx=4)

        self.btn_edit = ttk.Button(
            actions_frame, text="✏️ Edit Donor Details", style="Primary.TButton", command=self.edit_selected_donor
        )
        self.btn_edit.pack(side=tk.LEFT, padx=4)

        self.btn_delete = ttk.Button(
            actions_frame, text="🗑️ Delete Donor", style="Secondary.TButton", command=self.delete_selected_donor
        )
        self.btn_delete.pack(side=tk.LEFT, padx=4)

        self.btn_export = ttk.Button(
            actions_frame, text="📥 Export Visible to CSV", style="Secondary.TButton", command=self.export_csv
        )
        self.btn_export.pack(side=tk.RIGHT, padx=4)

        self.btn_new = ttk.Button(
            actions_frame, text="➕ Register New Donor", style="Primary.TButton", command=self.go_to_new_registration
        )
        self.btn_new.pack(side=tk.RIGHT, padx=4)

        # Details Grid
        self.details_grid = tk.Frame(parent, bg=self.COLOR_CARD_BG, padx=12, pady=6)
        self.details_grid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.lbl_det_name = tk.Label(self.details_grid, text="Name: —", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG)
        self.lbl_det_name.grid(row=0, column=0, sticky="w", padx=10, pady=2)

        self.lbl_det_blood = tk.Label(self.details_grid, text="Blood Group: —", font=("Helvetica", 10), bg=self.COLOR_CARD_BG)
        self.lbl_det_blood.grid(row=0, column=1, sticky="w", padx=10, pady=2)

        self.lbl_det_phone = tk.Label(self.details_grid, text="Phone: —", font=("Helvetica", 10), bg=self.COLOR_CARD_BG)
        self.lbl_det_phone.grid(row=0, column=2, sticky="w", padx=10, pady=2)

        self.lbl_det_email = tk.Label(self.details_grid, text="Email: —", font=("Helvetica", 10), bg=self.COLOR_CARD_BG)
        self.lbl_det_email.grid(row=1, column=0, sticky="w", padx=10, pady=2)

        self.lbl_det_address = tk.Label(self.details_grid, text="Address: —", font=("Helvetica", 10), bg=self.COLOR_CARD_BG)
        self.lbl_det_address.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        self.lbl_det_eligibility = tk.Label(self.details_grid, text="Status: —", font=("Helvetica", 10), bg=self.COLOR_CARD_BG)
        self.lbl_det_eligibility.grid(row=1, column=2, sticky="w", padx=10, pady=2)

        self.lbl_det_notes = tk.Label(
            self.details_grid, text="Medical Remarks: —", font=("Helvetica", 10, "italic"), bg=self.COLOR_CARD_BG, fg="#546E7A"
        )
        self.lbl_det_notes.grid(row=2, column=0, columnspan=3, sticky="w", padx=10, pady=2)

    # --------------------------------------------------------------------------
    # Search & Table Operations
    # --------------------------------------------------------------------------
    def refresh_search_results(self):
        """Filters in-memory donors based on blood group, mode, city, eligibility, and keyword."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_bg = self.search_blood_var.get()
        mode = self.search_mode_var.get()
        city_filter = self.search_city_var.get().strip().lower()
        query_filter = self.search_query_var.get().strip().lower()
        only_eligible = self.filter_eligible_var.get()

        # Determine target blood groups
        target_blood_groups = None
        if selected_bg != "All":
            if mode == "compatible":
                # Recipient needs `selected_bg`; who can donate to them?
                target_blood_groups = RECIPIENT_CAN_RECEIVE_FROM.get(selected_bg, [selected_bg])
            else:
                target_blood_groups = [selected_bg]

        matched = []
        for d in self.donors:
            # 1. Blood group filter
            if target_blood_groups and d["blood_group"] not in target_blood_groups:
                continue

            # 2. City filter
            if city_filter and city_filter not in d.get("city", "").lower():
                continue

            # 3. Query search (name, phone, email, address, id)
            if query_filter:
                combined_text = f"{d['id']} {d['full_name']} {d['phone']} {d.get('email','')} {d.get('address','')}".lower()
                if query_filter not in combined_text:
                    continue

            # 4. Eligibility check
            eligible, status_str, _ = check_eligibility(
                d.get("last_donation_date"), d["age"], d.get("weight_kg", 0.0), d.get("is_available", True)
            )

            if only_eligible and not eligible:
                continue

            tag = "eligible" if eligible else ("cooldown" if "Cooldown" in status_str else "ineligible")
            matched.append((d, status_str, tag))

        # Insert sorted into treeview
        for d, status_str, tag in matched:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    d["id"],
                    d["full_name"],
                    f"🩸 {d['blood_group']}",
                    d["age"],
                    d["gender"],
                    d["phone"],
                    d["city"],
                    d.get("last_donation_date") or "Never",
                    status_str,
                    "Yes" if d.get("is_available", True) else "No",
                ),
                tags=(tag,),
            )

        # Select first row if available
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self._on_donor_selected(None)
        else:
            self._clear_detail_panel()

    def reset_filters(self):
        self.search_blood_var.set("All")
        self.search_mode_var.set("compatible")
        self.search_city_var.set("")
        self.search_query_var.set("")
        self.filter_eligible_var.set(False)
        self.refresh_search_results()

    def _on_donor_selected(self, event):
        selected = self.tree.selection()
        if not selected:
            self._clear_detail_panel()
            return

        item = self.tree.item(selected[0])
        donor_id = item["values"][0]
        donor = self._find_donor_by_id(donor_id)
        if not donor:
            return

        eligible, status_str, days_passed = check_eligibility(
            donor.get("last_donation_date"), donor["age"], donor.get("weight_kg", 0.0), donor.get("is_available", True)
        )

        self.detail_header_lbl.config(
            text=f"👤 Donor Details: #{donor['id']} - {donor['full_name']} ({donor['blood_group']})"
        )
        self.lbl_det_name.config(text=f"Name: {donor['full_name']} ({donor['age']} yrs, {donor['gender']})")
        self.lbl_det_blood.config(text=f"Blood Group: 🩸 {donor['blood_group']}  |  Weight: {donor.get('weight_kg', 'N/A')} kg")
        self.lbl_det_phone.config(text=f"Phone: 📞 {donor['phone']}")
        self.lbl_det_email.config(text=f"Email: ✉️ {donor.get('email') or 'N/A'}")
        self.lbl_det_address.config(text=f"Address: 📍 {donor.get('address', '')}, {donor.get('city', '')}")
        self.lbl_det_eligibility.config(text=f"Status: {status_str} | Available: {'Yes' if donor.get('is_available') else 'No'}")
        self.lbl_det_notes.config(text=f"Medical Remarks: {donor.get('medical_notes') or 'None reported'}")

    def _clear_detail_panel(self):
        self.detail_header_lbl.config(text="👤 Selected Donor Information (No donor selected)")
        self.lbl_det_name.config(text="Name: —")
        self.lbl_det_blood.config(text="Blood Group: —")
        self.lbl_det_phone.config(text="Phone: —")
        self.lbl_det_email.config(text="Email: —")
        self.lbl_det_address.config(text="Address: —")
        self.lbl_det_eligibility.config(text="Status: —")
        self.lbl_det_notes.config(text="Medical Remarks: —")

    def _sort_by_column(self, col):
        """Sorts table rows when clicking column headers."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Try numeric sorting if possible
        try:
            items.sort(key=lambda t: int(t[0].replace("🩸", "").strip()), reverse=self.sort_reverse)
        except ValueError:
            items.sort(key=lambda t: t[0].lower(), reverse=self.sort_reverse)

        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)

        self.sort_reverse = not self.sort_reverse

    def record_donation_today(self):
        """Marks that the selected donor donated blood today."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a donor from the list to record a donation.")
            return

        donor_id = self.tree.item(selected[0])["values"][0]
        donor = self._find_donor_by_id(donor_id)
        if not donor:
            return

        today_str = date.today().strftime("%Y-%m-%d")
        confirm = messagebox.askyesno(
            "Confirm Blood Donation",
            f"Record whole blood donation for {donor['full_name']} today ({today_str})?\n\n"
            f"This will reset their cooldown period to {DONATION_COOLDOWN_DAYS} days.",
        )
        if confirm:
            donor["last_donation_date"] = today_str
            self.refresh_search_results()
            self.update_statistics_cards()
            messagebox.showinfo(
                "Donation Recorded",
                f"Thank you! Blood donation successfully recorded for {donor['full_name']}.\n"
                f"Next eligible date: {(date.today() + timedelta(days=DONATION_COOLDOWN_DAYS)).strftime('%Y-%m-%d')}.",
            )

    def delete_selected_donor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a donor from the list to delete.")
            return

        donor_id = self.tree.item(selected[0])["values"][0]
        donor = self._find_donor_by_id(donor_id)
        if not donor:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete donor record #{donor_id} ({donor['full_name']})?",
        )
        if confirm:
            self.donors = [d for d in self.donors if d["id"] != donor_id]
            self.refresh_search_results()
            self.update_statistics_cards()
            messagebox.showinfo("Deleted", f"Donor #{donor_id} deleted successfully.")

    def export_csv(self):
        """Exports currently visible search results to a CSV file."""
        children = self.tree.get_children()
        if not children:
            messagebox.showinfo("Export CSV", "No records currently visible to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files", "*.*")],
            initialfile=f"blood_donors_{date.today().strftime('%Y%m%d')}.csv",
            title="Save Donors as CSV",
        )
        if not file_path:
            return

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                headers = ["ID", "Name", "Blood Group", "Age", "Gender", "Phone", "City", "Last Donated", "Status", "Available"]
                writer.writerow(headers)

                for item in children:
                    vals = self.tree.item(item)["values"]
                    # clean blood group emoji
                    clean_vals = list(vals)
                    clean_vals[2] = str(clean_vals[2]).replace("🩸", "").strip()
                    writer.writerow(clean_vals)

            messagebox.showinfo("Export Successful", f"Exported {len(children)} donor records to:\n{file_path}")
        except Exception as ex:
            messagebox.showerror("Export Failed", f"Could not write CSV file:\n{ex}")

    # ==========================================================================
    # TAB 2: DONOR REGISTRATION & EDIT FORM
    # ==========================================================================
    def _build_register_tab(self):
        card = tk.LabelFrame(
            self.tab_register,
            text=" 📝 Donor Information Form ",
            font=("Helvetica", 12, "bold"),
            bg=self.COLOR_CARD_BG,
            fg=self.COLOR_PRIMARY,
            padx=25,
            pady=20,
            bd=1,
            relief=tk.SOLID,
        )
        card.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)

        # Mode banner (New vs Editing)
        self.form_mode_banner = tk.Label(
            card,
            text="➕ Register New Voluntary Blood Donor",
            font=("Helvetica", 13, "bold"),
            bg="#E8F5E9",
            fg="#2E7D32",
            pady=8,
        )
        self.form_mode_banner.pack(fill=tk.X, pady=(0, 15))

        # Two-column form body
        form_cols = tk.Frame(card, bg=self.COLOR_CARD_BG)
        form_cols.pack(fill=tk.BOTH, expand=True)

        left_col = tk.Frame(form_cols, bg=self.COLOR_CARD_BG)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        right_col = tk.Frame(form_cols, bg=self.COLOR_CARD_BG)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))

        # --- LEFT COLUMN FIELDS ---
        # Full Name
        tk.Label(left_col, text="Full Name *", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(4, 2))
        self.reg_name_var = tk.StringVar()
        ttk.Entry(left_col, textvariable=self.reg_name_var, font=("Helvetica", 10)).pack(fill=tk.X, pady=(0, 8))

        # Age & Gender (side-by-side)
        row_age_gender = tk.Frame(left_col, bg=self.COLOR_CARD_BG)
        row_age_gender.pack(fill=tk.X, pady=(0, 8))

        f_age = tk.Frame(row_age_gender, bg=self.COLOR_CARD_BG)
        f_age.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(f_age, text="Age (18-65) *", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        self.reg_age_var = tk.StringVar()
        ttk.Entry(f_age, textvariable=self.reg_age_var, font=("Helvetica", 10)).pack(fill=tk.X)

        f_gender = tk.Frame(row_age_gender, bg=self.COLOR_CARD_BG)
        f_gender.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(f_gender, text="Gender *", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        self.reg_gender_var = tk.StringVar(value="Male")
        ttk.Combobox(
            f_gender,
            textvariable=self.reg_gender_var,
            values=["Male", "Female", "Other"],
            state="readonly",
            font=("Helvetica", 10),
        ).pack(fill=tk.X)

        # Blood Group & Weight
        row_blood_wt = tk.Frame(left_col, bg=self.COLOR_CARD_BG)
        row_blood_wt.pack(fill=tk.X, pady=(0, 8))

        f_blood = tk.Frame(row_blood_wt, bg=self.COLOR_CARD_BG)
        f_blood.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Label(f_blood, text="Blood Group *", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        self.reg_blood_var = tk.StringVar(value="O+")
        ttk.Combobox(
            f_blood,
            textvariable=self.reg_blood_var,
            values=BLOOD_GROUPS,
            state="readonly",
            font=("Helvetica", 10, "bold"),
        ).pack(fill=tk.X)

        f_wt = tk.Frame(row_blood_wt, bg=self.COLOR_CARD_BG)
        f_wt.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))
        tk.Label(f_wt, text="Weight (kg) (Min 50)", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(0, 2))
        self.reg_weight_var = tk.StringVar(value="65.0")
        ttk.Entry(f_wt, textvariable=self.reg_weight_var, font=("Helvetica", 10)).pack(fill=tk.X)

        # Contact Phone
        tk.Label(left_col, text="Contact Phone Number *", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(4, 2))
        self.reg_phone_var = tk.StringVar()
        ttk.Entry(left_col, textvariable=self.reg_phone_var, font=("Helvetica", 10)).pack(fill=tk.X, pady=(0, 8))

        # Email Address
        tk.Label(left_col, text="Email Address", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(4, 2))
        self.reg_email_var = tk.StringVar()
        ttk.Entry(left_col, textvariable=self.reg_email_var, font=("Helvetica", 10)).pack(fill=tk.X, pady=(0, 8))

        # --- RIGHT COLUMN FIELDS ---
        # City / District
        tk.Label(right_col, text="City / District *", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(4, 2))
        self.reg_city_var = tk.StringVar()
        ttk.Entry(right_col, textvariable=self.reg_city_var, font=("Helvetica", 10)).pack(fill=tk.X, pady=(0, 8))

        # Street Address
        tk.Label(right_col, text="Street Address / Locality", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(4, 2))
        self.reg_address_var = tk.StringVar()
        ttk.Entry(right_col, textvariable=self.reg_address_var, font=("Helvetica", 10)).pack(fill=tk.X, pady=(0, 8))

        # Last Donation Date
        tk.Label(right_col, text="Last Donation Date (YYYY-MM-DD)", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(4, 2))
        row_date = tk.Frame(right_col, bg=self.COLOR_CARD_BG)
        row_date.pack(fill=tk.X, pady=(0, 8))

        self.reg_date_var = tk.StringVar()
        self.date_entry = ttk.Entry(row_date, textvariable=self.reg_date_var, font=("Helvetica", 10))
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.first_time_var = tk.BooleanVar(value=True)
        self.cb_first_time = tk.Checkbutton(
            row_date,
            text="First Time / Never Donated",
            variable=self.first_time_var,
            bg=self.COLOR_CARD_BG,
            font=("Helvetica", 9),
            command=self._toggle_first_time,
        )
        self.cb_first_time.pack(side=tk.RIGHT, padx=(8, 0))
        self._toggle_first_time()

        # Availability toggle
        self.reg_avail_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            right_col,
            text="Currently Available & Ready for Emergency Calls",
            variable=self.reg_avail_var,
            bg=self.COLOR_CARD_BG,
            font=("Helvetica", 10, "bold"),
            fg="#2E7D32",
        ).pack(anchor="w", pady=(4, 6))

        # Medical remarks
        tk.Label(right_col, text="Medical Remarks / Health Notes", font=("Helvetica", 10, "bold"), bg=self.COLOR_CARD_BG).pack(anchor="w", pady=(2, 2))
        self.reg_notes_text = tk.Text(right_col, height=3, font=("Helvetica", 10), relief=tk.SOLID, bd=1)
        self.reg_notes_text.pack(fill=tk.X, pady=(0, 10))

        # Bottom Buttons
        btn_bar = tk.Frame(card, bg=self.COLOR_CARD_BG)
        btn_bar.pack(fill=tk.X, pady=(15, 0))

        self.btn_submit_form = ttk.Button(
            btn_bar, text="💾 Save & Register Donor", style="Success.TButton", command=self.save_donor_form
        )
        self.btn_submit_form.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_clear_form = ttk.Button(
            btn_bar, text="🧹 Clear Form", style="Secondary.TButton", command=self.clear_registration_form
        )
        self.btn_clear_form.pack(side=tk.LEFT, padx=8)

        self.btn_cancel_edit = ttk.Button(
            btn_bar, text="❌ Cancel Editing", style="Secondary.TButton", command=self.cancel_editing
        )
        # Hidden initially; shown only while editing

    def _toggle_first_time(self):
        if self.first_time_var.get():
            self.reg_date_var.set("")
            self.date_entry.config(state="disabled")
        else:
            self.date_entry.config(state="normal")
            if not self.reg_date_var.get():
                self.reg_date_var.set((date.today() - timedelta(days=100)).strftime("%Y-%m-%d"))

    def go_to_new_registration(self):
        self.cancel_editing()
        self.notebook.select(self.tab_register)

    def edit_selected_donor(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a donor from the list to edit.")
            return

        donor_id = self.tree.item(selected[0])["values"][0]
        donor = self._find_donor_by_id(donor_id)
        if not donor:
            return

        self.editing_donor_id = donor["id"]

        # Populate form
        self.form_mode_banner.config(
            text=f"✏️ Editing Donor Record #{donor['id']} - {donor['full_name']}",
            bg="#FFF8E1",
            fg="#F57F17",
        )
        self.btn_submit_form.config(text="💾 Update Donor Details")
        self.btn_cancel_edit.pack(side=tk.LEFT, padx=8)

        self.reg_name_var.set(donor["full_name"])
        self.reg_age_var.set(str(donor["age"]))
        self.reg_gender_var.set(donor["gender"])
        self.reg_blood_var.set(donor["blood_group"])
        self.reg_weight_var.set(str(donor.get("weight_kg", 60.0)))
        self.reg_phone_var.set(donor["phone"])
        self.reg_email_var.set(donor.get("email", ""))
        self.reg_city_var.set(donor.get("city", ""))
        self.reg_address_var.set(donor.get("address", ""))

        last_dt = donor.get("last_donation_date")
        if last_dt:
            self.first_time_var.set(False)
            self.date_entry.config(state="normal")
            self.reg_date_var.set(last_dt)
        else:
            self.first_time_var.set(True)
            self.reg_date_var.set("")
            self.date_entry.config(state="disabled")

        self.reg_avail_var.set(donor.get("is_available", True))
        self.reg_notes_text.delete("1.0", tk.END)
        self.reg_notes_text.insert("1.0", donor.get("medical_notes", ""))

        # Switch to tab
        self.notebook.select(self.tab_register)

    def cancel_editing(self):
        self.editing_donor_id = None
        self.form_mode_banner.config(
            text="➕ Register New Voluntary Blood Donor",
            bg="#E8F5E9",
            fg="#2E7D32",
        )
        self.btn_submit_form.config(text="💾 Save & Register Donor")
        self.btn_cancel_edit.pack_forget()
        self.clear_registration_form()

    def clear_registration_form(self):
        self.reg_name_var.set("")
        self.reg_age_var.set("")
        self.reg_gender_var.set("Male")
        self.reg_blood_var.set("O+")
        self.reg_weight_var.set("65.0")
        self.reg_phone_var.set("")
        self.reg_email_var.set("")
        self.reg_city_var.set("")
        self.reg_address_var.set("")
        self.first_time_var.set(True)
        self.reg_date_var.set("")
        self.date_entry.config(state="disabled")
        self.reg_avail_var.set(True)
        self.reg_notes_text.delete("1.0", tk.END)

    def save_donor_form(self):
        """Validates input fields and saves new or updated donor."""
        name = self.reg_name_var.get().strip()
        age_str = self.reg_age_var.get().strip()
        phone = self.reg_phone_var.get().strip()
        city = self.reg_city_var.get().strip()
        blood_group = self.reg_blood_var.get()
        gender = self.reg_gender_var.get()
        email = self.reg_email_var.get().strip()
        address = self.reg_address_var.get().strip()
        weight_str = self.reg_weight_var.get().strip()
        notes = self.reg_notes_text.get("1.0", tk.END).strip()
        is_available = self.reg_avail_var.get()

        # Validation
        if not name:
            messagebox.showerror("Validation Error", "Full Name is required.")
            return

        if not age_str.isdigit():
            messagebox.showerror("Validation Error", "Age must be a valid whole number (between 18 and 65).")
            return
        age = int(age_str)
        if age < 18 or age > 65:
            messagebox.showerror("Validation Error", "Donor age must be between 18 and 65 for safe whole blood donation.")
            return

        try:
            weight = float(weight_str) if weight_str else 0.0
            if weight < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Weight must be a valid positive number in kg.")
            return

        if not phone:
            messagebox.showerror("Validation Error", "Contact Phone Number is required.")
            return

        clean_phone = re.sub(r"[^\d+]", "", phone)
        if len(clean_phone) < 7:
            messagebox.showerror("Validation Error", "Please provide a valid phone number (at least 7 digits).")
            return

        if not city:
            messagebox.showerror("Validation Error", "City / District is required.")
            return

        donation_date_str = ""
        if not self.first_time_var.get():
            raw_date = self.reg_date_var.get().strip()
            if raw_date:
                try:
                    parsed_d = datetime.strptime(raw_date, "%Y-%m-%d").date()
                    if parsed_d > date.today():
                        messagebox.showerror("Validation Error", "Last donation date cannot be in the future.")
                        return
                    donation_date_str = raw_date
                except ValueError:
                    messagebox.showerror("Validation Error", "Last donation date must be in YYYY-MM-DD format.")
                    return

        # Prepare record
        donor_data = {
            "full_name": name,
            "age": age,
            "gender": gender,
            "blood_group": blood_group,
            "phone": phone,
            "email": email,
            "city": city,
            "address": address,
            "last_donation_date": donation_date_str,
            "weight_kg": weight,
            "is_available": is_available,
            "medical_notes": notes,
        }

        if self.editing_donor_id:
            # Update existing
            existing = self._find_donor_by_id(self.editing_donor_id)
            if existing:
                existing.update(donor_data)
                messagebox.showinfo("Success", f"Donor record #{self.editing_donor_id} updated successfully!")
            self.cancel_editing()
        else:
            # Add new
            new_id = self.next_id
            self.next_id += 1
            donor_data["id"] = new_id
            self.donors.insert(0, donor_data)
            messagebox.showinfo("Success", f"Donor '{name}' registered successfully with ID #{new_id}!")
            self.clear_registration_form()

        self.refresh_search_results()
        self.update_statistics_cards()
        self.notebook.select(self.tab_search)

    # ==========================================================================
    # TAB 3: BLOOD COMPATIBILITY MATRIX & STATS
    # ==========================================================================
    def _build_matrix_tab(self):
        container = tk.Frame(self.tab_matrix, bg=self.COLOR_BG, padx=15, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Top Section: Donor Blood Group Distribution
        dist_frame = tk.LabelFrame(
            container,
            text=" 🩸 Current Donor Pool by Blood Group ",
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_CARD_BG,
            fg=self.COLOR_PRIMARY,
            padx=12,
            pady=8,
            bd=1,
            relief=tk.SOLID,
        )
        dist_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        self.blood_count_labels = {}
        for i, bg in enumerate(BLOOD_GROUPS):
            box = tk.Frame(dist_frame, bg="#FAFAFA", bd=1, relief=tk.SOLID, padx=10, pady=6)
            box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            lbl_bg = tk.Label(box, text=bg, font=("Helvetica", 12, "bold"), bg="#FAFAFA", fg=self.COLOR_PRIMARY)
            lbl_bg.pack()

            lbl_cnt = tk.Label(box, text="0 Donors", font=("Helvetica", 10), bg="#FAFAFA", fg="#37474F")
            lbl_cnt.pack()
            self.blood_count_labels[bg] = lbl_cnt

        # Middle Section: Interactive Compatibility Table
        matrix_frame = tk.LabelFrame(
            container,
            text=" 🧪 Red Blood Cell Compatibility Reference Guide ",
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_CARD_BG,
            fg=self.COLOR_PRIMARY,
            padx=15,
            pady=10,
            bd=1,
            relief=tk.SOLID,
        )
        matrix_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 10))

        # Table header
        tbl = tk.Frame(matrix_frame, bg="#B0BEC5")
        tbl.pack(fill=tk.BOTH, expand=True)

        cols = ["Blood Type", "Can Give Blood To (Recipients)", "Can Receive Blood From (Donors)", "Type Significance"]
        col_widths = [12, 32, 32, 28]

        for c_idx, title in enumerate(cols):
            h_lbl = tk.Label(
                tbl,
                text=title,
                font=("Helvetica", 10, "bold"),
                bg="#37474F",
                fg="#FFFFFF",
                padx=8,
                pady=6,
            )
            h_lbl.grid(row=0, column=c_idx, sticky="nsew", padx=1, pady=1)

        descriptions = {
            "O-": "🌟 Universal Red Cell Donor (Can give to all 8 types)",
            "O+": "Very common blood group (~38% of population)",
            "A-": "Can safely donate to A+, A-, AB+, AB-",
            "A+": "Very common blood group (~34% of population)",
            "B-": "Rare blood group (~1.5% of population)",
            "B+": "Can donate to B+ and AB+",
            "AB-": "Rare type, universal platelet donor",
            "AB+": "🌟 Universal Red Cell Recipient (Can receive from all)",
        }

        for r_idx, bg in enumerate(BLOOD_GROUPS, start=1):
            bg_color = "#FFFFFF" if r_idx % 2 == 0 else "#ECEFF1"

            can_give = ", ".join(DONOR_CAN_GIVE_TO[bg])
            can_recv = ", ".join(RECIPIENT_CAN_RECEIVE_FROM[bg])
            desc = descriptions.get(bg, "")

            lbl_b = tk.Label(tbl, text=f"🩸 {bg}", font=("Helvetica", 10, "bold"), bg=bg_color, fg=self.COLOR_PRIMARY, padx=8, pady=4)
            lbl_b.grid(row=r_idx, column=0, sticky="nsew", padx=1, pady=1)

            lbl_g = tk.Label(tbl, text=can_give, font=("Helvetica", 10), bg=bg_color, fg="#212121", padx=8, pady=4)
            lbl_g.grid(row=r_idx, column=1, sticky="nsew", padx=1, pady=1)

            lbl_r = tk.Label(tbl, text=can_recv, font=("Helvetica", 10), bg=bg_color, fg="#212121", padx=8, pady=4)
            lbl_r.grid(row=r_idx, column=2, sticky="nsew", padx=1, pady=1)

            lbl_d = tk.Label(tbl, text=desc, font=("Helvetica", 9), bg=bg_color, fg="#455A64", padx=8, pady=4)
            lbl_d.grid(row=r_idx, column=3, sticky="nsew", padx=1, pady=1)

        for col_idx in range(4):
            tbl.grid_columnconfigure(col_idx, weight=1)

        # Bottom Tools & Guidelines bar
        bottom_bar = tk.Frame(container, bg=self.COLOR_BG)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)

        lbl_guideline = tk.Label(
            bottom_bar,
            text="📌 Criteria: Age 18–65 • Weight ≥ 50kg • Minimum 90 days interval between whole blood donations.",
            font=("Helvetica", 9, "italic"),
            bg=self.COLOR_BG,
            fg="#455A64",
        )
        lbl_guideline.pack(side=tk.LEFT)

        btn_reload_sample = ttk.Button(
            bottom_bar, text="↺ Reset to Demo Data", style="Secondary.TButton", command=self.reset_to_demo_data
        )
        btn_reload_sample.pack(side=tk.RIGHT)

    def reset_to_demo_data(self):
        confirm = messagebox.askyesno("Reset Data", "Reload initial 10 demo donor records?")
        if confirm:
            self.donors = get_initial_donors()
            self.next_id = 111
            self.refresh_search_results()
            self.update_statistics_cards()
            messagebox.showinfo("Reset Complete", "Demo donor records reloaded successfully.")

    def update_statistics_cards(self):
        """Refreshes summary numbers and blood distribution counters."""
        self._build_kpi_cards()

        counts = {bg: 0 for bg in BLOOD_GROUPS}
        for d in self.donors:
            bg = d["blood_group"]
            if bg in counts:
                counts[bg] += 1

        for bg, lbl in self.blood_count_labels.items():
            c = counts.get(bg, 0)
            lbl.config(text=f"{c} Donor{'s' if c != 1 else ''}")

    def _compute_stats(self):
        total = len(self.donors)
        eligible = 0
        cooldown = 0
        o_neg = 0
        cities = set()

        for d in self.donors:
            is_el, _, _ = check_eligibility(
                d.get("last_donation_date"), d["age"], d.get("weight_kg", 0.0), d.get("is_available", True)
            )
            if is_el:
                eligible += 1
            else:
                cooldown += 1

            if d["blood_group"] == "O-":
                o_neg += 1

            if d.get("city"):
                cities.add(d["city"].strip().title())

        return {
            "total": total,
            "eligible": eligible,
            "cooldown": cooldown,
            "o_negative": o_neg,
            "cities_count": len(cities),
        }

    def _find_donor_by_id(self, donor_id):
        for d in self.donors:
            if d["id"] == donor_id:
                return d
        return None


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    app = BloodDonorApp()
    app.mainloop()
