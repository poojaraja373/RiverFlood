# River Flood Early-Warning System

This project simulates a simple river flood early-warning system for the SIH 2026 practical assessment. It stores water-level readings, derives a warning status on the server, and presents a control-room dashboard for search, filtering, and review.

## Problem in two lines
A riverside block needs a simple, low-cost way to monitor river levels continuously and warn residents before flooding becomes dangerous. This project provides a lightweight web-based dashboard and simulator that capture readings, flag risk, and preserve historical trend data.

## Fields and values
- reading_id: auto-generated integer primary key.
- location: monitoring point name such as North Bank, South Bank, East Jetty, or West Ford.
- water_level_m: numeric river level in meters. Valid range is 0 to 12 m. A few awkward sample values are included on purpose, including a missing value and an impossible spike.
- status: manually entered status from the form, such as Safe, Warning, Danger, or Unknown.
- recorded_at: timestamp for each reading.
- device_id: unique device identifier, for example NODE-01.
- derived_status: server-calculated status from the water level.
- trend: server-calculated trend from the previous reading.
- delta_m: change from the previous reading at the same location.

## How the derived figure is calculated
The dashboard uses the server to calculate:
- derived_status: Safe below 1.5 m, Warning at 1.5 to 2.99 m, and Danger at 3.0 m or above.
- trend: Rising when the current reading is more than 0.2 m above the previous reading, Falling when it is more than 0.2 m below, and Stable otherwise.
- delta_m: current reading minus the previous reading at the same location.

## How to run
1. Install Python 3.10+.
2. Open the project folder.
3. Install Flask: pip install flask
4. Start the app: python app.py
5. Open http://127.0.0.1:5000/

## What is not finished
The current build is a simulation-only prototype. It does not yet connect to real hardware or send data over a live network.

## Screenshots
Use the running app in a browser to capture screenshots of the dashboard, registration form, and populated table.
