# Inbound Carriers Dashboard

A modern, real-time dashboard for displaying inbound carrier information with a sleek black and green color scheme.

## Features

- **Modern UI**: Clean, responsive design with black and green color scheme
- **Real-time Data**: Auto-refreshes every 30 seconds
- **Multiple Windows**: Each carrier displayed in its own window/card
- **Complete Information**: All carrier fields displayed including:
  - Load ID
  - Origin and Destination
  - Pickup and Delivery times
  - Equipment type
  - Loadboard rate
  - Weight and dimensions
  - Commodity type
  - Number of pieces
  - Miles
  - Notes

## Database Schema

The application uses SQLite with the following table structure:

```sql
CREATE TABLE carriers (
    load_id TEXT PRIMARY KEY,
    origin TEXT,
    destination TEXT,
    pickup_datetime TEXT,
    delivery_datetime TEXT,
    equipment_type TEXT,
    loadboard_rate REAL,
    notes TEXT,
    weight REAL,
    commodity_type TEXT,
    num_of_pieces INTEGER,
    miles REAL,
    dimensions TEXT
);
```

## API Endpoints

- `GET /carriers/` - Main dashboard page
- `GET /carriers/api/carriers` - Get all carriers (JSON)
- `GET /carriers/api/carriers/<load_id>` - Get specific carrier
- `POST /carriers/api/carriers` - Add new carrier
- `PUT /carriers/api/carriers/<load_id>` - Update carrier
- `DELETE /carriers/api/carriers/<load_id>` - Delete carrier

## Sample Data

The application comes with 5 sample carriers:
- **LOAD001**: Electronics from LA to Phoenix
- **LOAD002**: Frozen Foods from Chicago to Detroit
- **LOAD003**: Industrial Equipment from Dallas to Houston
- **LOAD004**: General Merchandise from Miami to Orlando
- **LOAD005**: Trailer from Seattle to Portland

## Running the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Access the dashboard:
   ```
   https://localhost:8443/carriers/
   ```

3. The dashboard will automatically load carrier information and refresh every 30 seconds.

## Technologies Used

- **Backend**: Flask, SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with modern gradients and animations
- **Database**: SQLite with automatic sample data generation

## Design Features

- **Responsive Design**: Works on desktop and mobile devices
- **Modern Animations**: Hover effects and shimmer animations
- **Color Scheme**: Black background with green accents (#00ff41)
- **Glass Morphism**: Backdrop blur effects and transparency
- **Grid Layout**: Responsive grid for multiple carrier windows
- **Real-time Updates**: Automatic refresh and manual refresh button

## File Structure

```
├── app.py                 # Main Flask application
├── database.py           # Database management
├── routes/
│   └── carriers.py       # API routes for carriers
├── templates/
│   └── carriers.html     # Main dashboard template
└── carriers.db           # SQLite database
``` 