#!/bin/bash
# Setup script for Render deployment
# Initialize database if it doesn't exist
if [ ! -f believers_academy.db ]; then
    echo "Initializing database..."
    python3 -c "
import sqlite3
conn = sqlite3.connect('believers_academy.db')
c = conn.cursor()

# Centres
centres = [
    ('Dadar Railways', 'Dadar Railway Station, Dadar East', '4 PM - 5 PM, 5 PM - 6 PM, 6 PM - 7 PM, 7 PM - 8 PM', '11 AM - 12 PM, 12 PM - 1 PM, 1 PM - 2 PM, 2 PM - 3 PM', 1),
    ('Parsee Gymkhana', 'Dadar West', '6 AM - 7 AM, 7 AM - 8 AM, 8 AM - 9 AM', '6 AM - 7 AM, 7 AM - 8 AM, 8 AM - 9 AM', 1),
    ('Nirmal Park', 'Nirmal Nagar, Byculla', '', '', 0),
    ('Badhwar Park', 'Colaba', '5 PM - 6 PM, 6 PM - 7 PM', '5 PM - 6 PM, 6 PM - 7 PM', 1),
]
c.executemany('INSERT INTO centres (name, address, monday_friday_slots, saturday_sunday_slots, is_active) VALUES (?, ?, ?, ?, ?)', centres)

# Coaches
coaches = [
    ('Prathamesh', '1234', 'admin', None),
    ('Gautam', '5678', 'coach', 2),
    ('Madhur', '9012', 'coach', 1),
    ('Sanket', '3456', 'coach', 3),
    ('Arif', '7890', 'partner', None),
    ('Manas', '2345', 'partner', None),
    ('Darshak', '6789', 'partner', None),
]
c.executemany('INSERT INTO coaches (name, pin, role, assigned_centre_id) VALUES (?, ?, ?, ?)', coaches)

# Sample students (empty for now - admin can upload)
conn.commit()
print('Database initialized!')
"
fi
