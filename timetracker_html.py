# -*- coding: utf-8 -*-
import json
import datetime
from html import escape

# Load the data from the .timetracker file
with open('.timetracker', 'r') as f:
    data = json.load(f)

# Start the HTML output
html = """
<html>
<head>
	<meta charset="utf-8">
    <title>Υπολογισμός Κόστους</title>
    <style>
        table { border-collapse: collapse; }
        th, td { border: 1px solid black; padding: 5px; text-align: right; }
        th, td:first-child { text-align: left; }
        .total { border-top: 2px solid black; }
    </style>
</head>
<body>
    <h1>Time Tracker Data</h1>
    <table>
        <tr>
            <th>Αρχή</th>
            <th>Τέλος</th>
            <th>Διάρκεια (secs)</th>
            <th>Διάρκεια (mins)</th>
        </tr>
"""

total_seconds = 0
total_minutes = 0
hourly_rate = 40

# Add a row for each session
for session in data['sessions']:
    begin = datetime.datetime.fromisoformat(session['begin']).strftime('%d-%m-%Y %H:%M:%S')
    end = datetime.datetime.fromisoformat(session['end']).strftime('%d-%m-%Y %H:%M:%S')
    duration_seconds = session['duration']
    duration_minutes = round(duration_seconds / 60, 2)
    total_seconds += duration_seconds
    total_minutes += duration_minutes
    html += f"""
        <tr>
            <td style="text-align: left;">{escape(begin)}</td>
            <td style="text-align: left;">{escape(end)}</td>
            <td>{escape(str(duration_seconds))}</td>
            <td>{escape(str(duration_minutes))}</td>
        </tr>
    """

# Add a row for total seconds and minutes
html += f"""
    <tr class="Σύνολο">
        <td colspan="2" style="text-align: left;">Σύνολο</td>
        <td>{escape(str(total_seconds))}</td>
        <td>{escape(str(total_minutes))}</td>
    </tr>
"""

# Calculate cost
total_minutes = max(total_minutes, 30)  # If total minutes is less than 30, charge for 30
cost = hourly_rate * (total_minutes / 60)

# Add a row for hourly rate and cost
html += f"""
    <tr>
        <td colspan="2" style="text-align: left;">Ωριαία Χρέωση</td>
        <td colspan="2">{hourly_rate:.2f} €</td>
    </tr>
    <tr>
        <td colspan="2" style="text-align: left;">Κόστος</td>
        <td colspan="2">{cost:.2f} €</td>
    </tr>
"""

# Finish the HTML output
html += """
    </table>
	 <p style="text-align: right;">*Ελάχιστη χρέωση 30 λεπτά.</p>
</body>
</html>
"""

# Write the HTML to an output file
with open('output.html', 'w', encoding='utf-8') as f:
    f.write(html)