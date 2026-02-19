"""
Believers Badminton Academy - Attendance Management System
Built with Streamlit
"""

import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd

# Page config
st.set_page_config(
    page_title="Believers Badminton Academy",
    page_icon="🏸",
    layout="wide"
)

import sqlite3
import os
from datetime import datetime, date

# Database path - works locally and on Render
DB_PATH = os.environ.get('DATABASE_PATH', 'believers_academy.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Centres table
    c.execute('''CREATE TABLE IF NOT EXISTS centres (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        address TEXT,
        monday_friday_slots TEXT,
        saturday_sunday_slots TEXT,
        is_active INTEGER DEFAULT 1
    )''')
    
    # Coaches table
    c.execute('''CREATE TABLE IF NOT EXISTS coaches (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        pin TEXT NOT NULL,
        role TEXT DEFAULT 'coach',
        assigned_centre_id INTEGER,
        FOREIGN KEY (assigned_centre_id) REFERENCES centres(id)
    )''')
    
    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        centre_id INTEGER,
        phone TEXT,
        parent_phone TEXT,
        join_date TEXT,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (centre_id) REFERENCES centres(id)
    )''')
    
    # Attendance table
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY,
        date TEXT NOT NULL,
        coach_id INTEGER,
        student_id INTEGER,
        centre_id INTEGER,
        time_slot TEXT NOT NULL,
        status TEXT DEFAULT 'Present',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (coach_id) REFERENCES coaches(id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (centre_id) REFERENCES centres(id)
    )''')
    
    conn.commit()
    return conn

def seed_data(conn):
    """Seed initial data if tables are empty"""
    c = conn.cursor()
    
    # Check if centres exist
    c.execute("SELECT COUNT(*) FROM centres")
    if c.fetchone()[0] == 0:
        # Seed centres
        centres = [
            ("Dadar Railways", "Dadar Railway Station, Dadar East", "4 PM - 5 PM, 5 PM - 6 PM, 6 PM - 7 PM, 7 PM - 8 PM", "11 AM - 12 PM, 12 PM - 1 PM, 1 PM - 2 PM, 2 PM - 3 PM", 1),
            ("Parsee Gymkhana", "Dadar West", "6 AM - 7 AM, 7 AM - 8 AM, 8 AM - 9 AM", "6 AM - 7 AM, 7 AM - 8 AM, 8 AM - 9 AM", 1),
            ("Nirmal Park", "Nirmal Nagar, Byculla", "", "", 0),  # Dormant
            ("Badhwar Park", "Colaba", "5 PM - 6 PM, 6 PM - 7 PM", "5 PM - 6 PM, 6 PM - 7 PM", 1),
        ]
        c.executemany("INSERT INTO centres (name, address, monday_friday_slots, saturday_sunday_slots, is_active) VALUES (?, ?, ?, ?, ?)", centres)
        
    # Check if coaches exist
    c.execute("SELECT COUNT(*) FROM coaches")
    if c.fetchone()[0] == 0:
        # Seed coaches (PIN: 4 digits)
        coaches = [
            ("Prathamesh", "1234", "admin", None),  # Admin
            ("Gautam", "5678", "coach", 2),          # Parsee Gymkhana
            ("Madhur", "9012", "coach", 1),          # Dadar Railways
            ("Sanket", "3456", "coach", 3),          # Nirmal Park (dormant)
            ("Arif", "7890", "partner", None),       # Can see all
            ("Manas", "2345", "partner", None),      # Can see all
            ("Darshak", "6789", "partner", None),   # Can see all
        ]
        c.executemany("INSERT INTO coaches (name, pin, role, assigned_centre_id) VALUES (?, ?, ?, ?)", coaches)
    
    # Check if students exist
    c.execute("SELECT COUNT(*) FROM students")
    if c.fetchone()[0] == 0:
        # Seed sample students
        students = [
            ("Aarav Sharma", 1, "9876543210", "9876543211", "2026-01-01"),
            ("Vihaan Patel", 1, "9876543212", "9876543213", "2026-01-01"),
            ("Arnav Singh", 1, "9876543214", "9876543215", "2026-01-05"),
            ("Sai Kulkarni", 2, "9876543216", "9876543217", "2026-01-02"),
            ("Reyansh Joshi", 2, "9876543218", "9876543219", "2026-01-03"),
            ("Ayaan Desai", 2, "9876543220", "9876543221", "2026-01-04"),
            ("Krishna Gawde", 4, "9876543222", "9876543223", "2026-01-06"),
            ("OM Shinde", 4, "9876543224", "9876543225", "2026-01-07"),
            ("Pranav Nair", 1, "9876543226", "9876543227", "2026-01-08"),
            ("Kartik Iyer", 2, "9876543228", "9876543229", "2026-01-09"),
        ]
        c.executemany("INSERT INTO students (name, centre_id, phone, parent_phone, join_date) VALUES (?, ?, ?, ?, ?)", students)
    
    conn.commit()

# Initialize
conn = init_db()
seed_data(conn)

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "coach" not in st.session_state:
    st.session_state.coach = None

# CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a5f;
        text-align: center;
        margin-bottom: 2rem;
    }
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    .logo-container img {
        max-height: 100px;
        border-radius: 10px;
    }
    .coach-name {
        font-size: 1.5rem;
        color: #2e7d32;
    }
    .centre-header {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .student-card {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
    }
    .present { color: #2e7d32; font-weight: bold; }
    .absent { color: #c62828; font-weight: bold; }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def login():
    try:
        st.image("logo.jpg", width=150)
    except:
        st.markdown("🏸")
    st.markdown('<p class="main-header" style="color: #FF6B35;">🏸 Believers Badminton Academy</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Coach Login")
        
        # Get all coaches
        c = conn.cursor()
        c.execute("SELECT name FROM coaches ORDER BY name")
        coaches = [row[0] for row in c.fetchall()]
        
        coach_name = st.selectbox("Select Your Name", coaches)
        pin = st.text_input("Enter 4-digit PIN", type="password")
        
        if st.button("Login", type="primary"):
            c.execute("SELECT id, name, pin, role, assigned_centre_id FROM coaches WHERE name = ?", (coach_name,))
            coach = c.fetchone()
            
            if coach and coach[2] == pin:
                st.session_state.logged_in = True
                st.session_state.coach = {
                    "id": coach[0],
                    "name": coach[1],
                    "role": coach[3],
                    "assigned_centre_id": coach[4]
                }
                st.rerun()
            else:
                st.error("Invalid PIN. Please try again.")

def get_time_slots(centre_id, selected_date):
    """Get time slots based on centre and day of week"""
    c = conn.cursor()
    c.execute("SELECT monday_friday_slots, saturday_sunday_slots FROM centres WHERE id = ?", (centre_id,))
    row = c.fetchone()
    
    if not row:
        return []
    
    day = selected_date.weekday()  # 0=Monday, 6=Sunday
    slots_str = row[1] if day >= 5 else row[0]  # Sat/Sun or Mon-Fri
    
    if not slots_str:
        return []
    
    return [s.strip() for s in slots_str.split(",")]

def mark_attendance_page():
    try:
        st.image("logo.jpg", width=100)
    except:
        st.markdown("🏸")
    coach = st.session_state.coach
    
    # Initialize session state for attendance
    if "attendance_list" not in st.session_state:
        st.session_state.attendance_list = []
    if "current_slot" not in st.session_state:
        st.session_state.current_slot = None
    
    # Get accessible centres
    c = conn.cursor()
    if coach["role"] == "admin" or coach["role"] == "partner":
        c.execute("SELECT id, name, address FROM centres WHERE is_active = 1")
    else:
        c.execute("SELECT id, name, address FROM centres WHERE id = ? AND is_active = 1", (coach["assigned_centre_id"],))
    
    centres = c.fetchall()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Welcome, {coach['name']}! 👋")
    with col2:
        if st.button("Logout", type="secondary", key="logout_main"):
            st.session_state.logged_in = False
            st.session_state.coach = None
            st.session_state.attendance_list = []
            st.rerun()
    
    st.markdown("---")
    
    # Centre selection
    if not centres:
        st.warning("No centres assigned to you.")
        return
    
    centre_names = {c[0]: c[1] for c in centres}
    centre_options = [f"{c[0]} - {c[1]} - {c[2]}" for c in centres]
    
    selected_centre_option = st.selectbox("Select Centre", centre_options)
    selected_centre_id = int(selected_centre_option.split(" - ")[0].strip())
    
    # Date selection (default today)
    selected_date = st.date_input("Select Date", value=date.today(), min_value=date(2025, 1, 1))
    
    # Get time slots
    time_slots = get_time_slots(selected_centre_id, selected_date)
    
    if not time_slots:
        st.warning("No time slots configured for this centre on this day.")
        return
    
    # Time slot selection (BATCH FIRST)
    selected_slot = st.selectbox("Select Batch/Time Slot", time_slots, key="slot_select")
    
    # Get all students for this centre for the dropdown
    c.execute("SELECT id, name FROM students WHERE centre_id = ? AND is_active = 1 ORDER BY name", (selected_centre_id,))
    all_students = c.fetchall()
    student_options = {s[1]: s[0] for s in all_students}  # name -> id
    
    # Reset attendance list when slot changes
    if selected_slot != st.session_state.current_slot:
        st.session_state.current_slot = selected_slot
        st.session_state.attendance_list = []
    
    # Check what's already saved for this slot
    c.execute("""
        SELECT student_id, status FROM attendance 
        WHERE centre_id = ? AND date = ? AND time_slot = ?
    """, (selected_centre_id, selected_date.isoformat(), selected_slot))
    existing = {row[0]: row[1] for row in c.fetchall()}
    
    # Pre-populate from existing records
    if st.session_state.attendance_list == [] and existing:
        for student_id, status in existing.items():
            c.execute("SELECT name FROM students WHERE id = ?", (student_id,))
            row = c.fetchone()
            if row:
                st.session_state.attendance_list.append({
                    "student_id": student_id,
                    "name": row[0],
                    "status": status
                })
    
    st.markdown("### Mark Attendance")
    st.markdown(f"**Centre:** {centre_names[selected_centre_id]} | **Date:** {selected_date} | **Slot:** {selected_slot}")
    
    if not all_students:
        st.warning("No students registered for this centre yet.")
        return
    
    # Searchable student dropdown
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search Student", placeholder="Type name to search...")
    with col2:
        st.markdown("###")  # spacing
    
    # Filter students based on search
    if search_query:
        filtered_students = [s for s in all_students if search_query.lower() in s[1].lower()]
    else:
        filtered_students = all_students
    
    student_dropdown = [s[1] for s in filtered_students]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_student = st.selectbox("Select Student", student_dropdown, key="student_select")
    with col2:
        if st.button("➕ Add Student", type="primary"):
            if selected_student:
                # Check if already added
                already_added = any(s["name"] == selected_student for s in st.session_state.attendance_list)
                if not already_added:
                    st.session_state.attendance_list.append({
                        "student_id": student_options[selected_student],
                        "name": selected_student,
                        "status": "Present"
                    })
                else:
                    st.warning(f"{selected_student} already added!")
    
    st.markdown("---")
    st.markdown("#### Students in this Batch")
    
    # Display added students with status
    if st.session_state.attendance_list:
        for i, student in enumerate(st.session_state.attendance_list):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{student['name']}**")
            with col2:
                new_status = st.selectbox(
                    "Status",
                    ["Present", "Absent", "Leave"],
                    index=["Present", "Absent", "Leave"].index(student["status"]),
                    key=f"status_{i}_{selected_slot}",
                    label_visibility="collapsed"
                )
                st.session_state.attendance_list[i]["status"] = new_status
            with col3:
                if st.button("🗑️", key=f"del_{i}_{selected_slot}"):
                    st.session_state.attendance_list.pop(i)
                    st.rerun()
        
        st.markdown("---")
        if st.button("💾 Save Attendance", type="primary", use_container_width=True):
            date_str = selected_date.isoformat()
            for student in st.session_state.attendance_list:
                student_id = student["student_id"]
                status = student["status"]
                
                # Check if entry exists
                c.execute("""
                    SELECT id FROM attendance 
                    WHERE student_id = ? AND centre_id = ? AND date = ? AND time_slot = ?
                """, (student_id, selected_centre_id, date_str, selected_slot))
                existing_entry = c.fetchone()
                
                if existing_entry:
                    c.execute("""
                        UPDATE attendance SET status = ?, coach_id = ? 
                        WHERE student_id = ? AND centre_id = ? AND date = ? AND time_slot = ?
                    """, (status, coach["id"], student_id, selected_centre_id, date_str, selected_slot))
                else:
                    c.execute("""
                        INSERT INTO attendance (student_id, centre_id, date, time_slot, status, coach_id)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (student_id, selected_centre_id, date_str, selected_slot, status, coach["id"]))
            
            conn.commit()
            st.success(f"✅ Attendance saved for {selected_slot}!")
            st.session_state.attendance_list = []
            st.rerun()
    else:
        st.info("👆 Select a batch above, search for students, and click 'Add Student' to mark attendance.")

def admin_dashboard():
    try:
        st.image("logo.jpg", width=100)
    except:
        st.markdown("🏸")
    st.markdown('<p class="main-header" style="color: #FF6B35;">🏸 Believers Badminton Academy - Admin Dashboard</p>', unsafe_allow_html=True)
    
    coach = st.session_state.coach
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Welcome, {coach['name']}! 👋")
    with col2:
        if st.button("Logout", type="secondary", key="logout_admin"):
            st.session_state.logged_in = False
            st.session_state.coach = None
            st.rerun()
    
    st.markdown("---")
    
    # Tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Attendance Reports", "👥 Manage Students", "🏸 Manage Centres", "🔐 Manage Coaches"])
    
    with tab1:
        # Attendance Reports
        c = conn.cursor()
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From Date", value=date.today().replace(day=1))
        with col2:
            end_date = st.date_input("To Date", value=date.today())
        
        # Centre filter
        c.execute("SELECT id, name FROM centres")
        all_centres = c.fetchall()
        centre_filter = st.selectbox("Filter by Centre", ["All"] + [c[1] for c in all_centres])
        
        # Build query
        query = """
            SELECT a.date, c.name as centre, s.name as student, a.time_slot, a.status, co.name as coach
            FROM attendance a
            JOIN centres c ON a.centre_id = c.id
            JOIN students s ON a.student_id = s.id
            JOIN coaches co ON a.coach_id = co.id
            WHERE a.date BETWEEN ? AND ?
        """
        params = [start_date.isoformat(), end_date.isoformat()]
        
        if centre_filter != "All":
            query += " AND c.name = ?"
            params.append(centre_filter)
        
        query += " ORDER BY a.date DESC, c.name, a.time_slot"
        
        c.execute(query, params)
        records = c.fetchall()
        
        if records:
            df = pd.DataFrame(records, columns=["Date", "Centre", "Student", "Time Slot", "Status", "Coach"])
            
            # Summary stats
            total = len(df)
            present = len(df[df["Status"] == "Present"])
            absent = len(df[df["Status"] == "Absent"])
            leave = len(df[df["Status"] == "Leave"])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Records", total)
            col2.metric("Present", present, f"{present/total*100:.1f}%" if total > 0 else "0%")
            col3.metric("Absent", absent, f"{absent/total*100:.1f}%" if total > 0 else "0%")
            col4.metric("Leave", leave, f"{leave/total*100:.1f}%" if total > 0 else "0%")
            
            st.dataframe(df, use_container_width=True)
            
            # Download CSV
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Report CSV", csv, "attendance_report.csv", "text/csv")
        else:
            st.info("No attendance records found for the selected period.")
    
    with tab2:
        # Manage Students
        st.markdown("### 👥 Student Management")
        
        # Upload students
        with st.expander("📤 Upload Students (CSV)"):
            st.markdown("""
            **CSV Format:** `name, phone, parent_phone`
            
            Example:
            ```
            Rahul Sharma, 9876543210, 9876543211
            Aditi Patel, 9876543212, 9876543213
            ```
            """)
            csv_text = st.text_area("Paste CSV data (or enter manually)", height=150)
            centre_for_upload = st.selectbox("Centre", [c[1] for c in all_centres])
            
            if st.button("Upload Students"):
                if csv_text:
                    lines = csv_text.strip().split("\n")
                    for line in lines:
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 1:
                            name = parts[0]
                            phone = parts[1] if len(parts) > 1 else ""
                            parent_phone = parts[2] if len(parts) > 2 else ""
                            try:
                                c.execute("""
                                    INSERT INTO students (name, centre_id, phone, parent_phone, join_date)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (name, int(centre_for_upload.split(" - ")[0]) if " - " in centre_for_upload else 1, phone, parent_phone, date.today().isoformat()))
                            except:
                                pass  # Skip duplicates
                    conn.commit()
                    st.success(f"Uploaded {len(lines)} students!")
                    st.rerun()
        
        # View/Edit students
        c.execute("""
            SELECT s.id, s.name, c.name as centre, s.phone, s.parent_phone, s.join_date, s.is_active
            FROM students s
            JOIN centres c ON s.centre_id = c.id
            ORDER BY c.name, s.name
        """)
        student_records = c.fetchall()
        
        if student_records:
            df_students = pd.DataFrame(student_records, columns=["ID", "Name", "Centre", "Phone", "Parent Phone", "Join Date", "Active"])
            st.dataframe(df_students, use_container_width=True)
            
            # Delete student
            st.markdown("#### 🗑️ Remove Student")
            student_to_delete = st.selectbox("Select Student to Remove", [f"{s[1]} - {s[2]}" for s in student_records])
            if st.button("Remove Student", type="primary"):
                student_id = int(student_to_delete.split(" - ")[0].split(".")[0].strip())
                c.execute("UPDATE students SET is_active = 0 WHERE id = ?", (student_id,))
                conn.commit()
                st.success("Student removed!")
                st.rerun()
    
    with tab3:
        # Manage Centres
        st.markdown("### 🏸 Centre Management")
        
        c.execute("SELECT id, name, address, monday_friday_slots, saturday_sunday_slots, is_active FROM centres")
        centre_records = c.fetchall()
        
        for centre in centre_records:
            with st.expander(f"{'✅' if centre[5] else '❌'} {centre[1]} - {centre[2]}"):
                st.markdown(f"**Mon-Fri Slots:** {centre[3]}")
                st.markdown(f"**Sat-Sun Slots:** {centre[4]}")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Name", value=centre[1], key=f"name_{centre[0]}")
                with col2:
                    new_address = st.text_input("Address", value=centre[2], key=f"addr_{centre[0]}")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_mf_slots = st.text_input("Mon-Fri Slots", value=centre[3], key=f"mf_{centre[0]}")
                with col2:
                    new_ss_slots = st.text_input("Sat-Sun Slots", value=centre[4], key=f"ss_{centre[0]}")
                
                if st.button("Update Centre", key=f"upd_{centre[0]}"):
                    c.execute("""
                        UPDATE centres SET name = ?, address = ?, monday_friday_slots = ?, saturday_sunday_slots = ?
                        WHERE id = ?
                    """, (new_name, new_address, new_mf_slots, new_ss_slots, centre[0]))
                    conn.commit()
                    st.success("Centre updated!")
                    st.rerun()
    
    with tab4:
        # Manage Coaches
        st.markdown("### 🔐 Coach Management")
        
        c.execute("SELECT id, name, pin, role, assigned_centre_id FROM coaches")
        coach_records = c.fetchall()
        
        # Show coaches
        for coach_rec in coach_records:
            c.execute("SELECT name FROM centres WHERE id = ?", (coach_rec[4],))
            centre_name = c.fetchone()[0] if coach_rec[4] else "All Centres"
            
            with st.expander(f"👤 {coach_rec[1]} - {coach_rec[3].upper()}"):
                col1, col2 = st.columns(2)
                with col1:
                    new_pin = st.text_input("New PIN", value=coach_rec[2], key=f"pin_{coach_rec[0]}", type="password")
                with col2:
                    new_role = st.selectbox("Role", ["admin", "coach", "partner"], 
                                           index=["admin", "coach", "partner"].index(coach_rec[3]),
                                           key=f"role_{coach_rec[0]}")
                
                c.execute("SELECT id, name FROM centres")
                all_c = c.fetchall()
                centre_options = [(None, "All Centres")] + all_c
                centre_idx = 0
                for i, oc in enumerate(centre_options):
                    if oc[0] == coach_rec[4]:
                        centre_idx = i
                        break
                new_centre = st.selectbox("Assigned Centre", [oc[1] for oc in centre_options], 
                                         index=centre_idx, key=f"centre_{coach_rec[0]}")
                
                if st.button("Update Coach", key=f"updc_{coach_rec[0]}"):
                    assigned = None if new_centre == "All Centres" else int(new_centre.split(" - ")[0]) if " - " in new_centre else None
                    c.execute("UPDATE coaches SET pin = ?, role = ?, assigned_centre_id = ? WHERE id = ?",
                            (new_pin, new_role, assigned, coach_rec[0]))
                    conn.commit()
                    st.success("Coach updated!")
                    st.rerun()

def partner_dashboard():
    """Partners can see all centres but can't manage students/centres/coaches"""
    try:
        st.image("logo.jpg", width=100)
    except:
        st.markdown("🏸")
    st.markdown('<p class="main-header" style="color: #FF6B35;">🏸 Believers Badminton Academy</p>', unsafe_allow_html=True)
    
    coach = st.session_state.coach
    
    st.markdown("---")
    st.info("You have partner access - you can mark attendance for any centre.")
    
    # Same as mark_attendance but with all centres
    mark_attendance_page()

# Main app flow
if not st.session_state.logged_in:
    login()
else:
    coach = st.session_state.coach
    
    if coach["role"] == "admin":
        # Show menu for admin
        menu = st.sidebar.selectbox("Menu", ["Mark Attendance", "Admin Dashboard"])
        if menu == "Admin Dashboard":
            admin_dashboard()
        else:
            mark_attendance_page()
    elif coach["role"] == "partner":
        partner_dashboard()
    else:
        mark_attendance_page()
