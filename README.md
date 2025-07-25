# Wimbledon Finals API with Automated Scraper

This project provides a Flask-based REST API to retrieve Wimbledon Men’s Singles final results by year from a MongoDB Atlas database. It includes an automated web scraper that runs every 24 hours in the background to check for the latest year’s final and update the database if new data is found.

The project is deployable on platforms like **Render.com**, which supports persistent background processes.

[Endpoint](https://wimbledon-finals.onrender.com/wimbledon?year=1999)

---

## Features

* API endpoint to retrieve Wimbledon finals data by year.
* Background scraper that automatically checks every 24 hours for the latest year’s final.
* MongoDB Atlas integration to store and update data in the cloud.
* Persistent deployment supported on Render’s free web services.
* Fully automated database updates without manual intervention.

---

## Project Structure

```
.
├── main.py               # Flask API with background scraper
├── scraper.py            # Web scraper logic
├── requirements.txt      # Python dependencies
├── prev_result_scraper   # Was used to Scrape data and store to Mongodb
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/wimbledon-api.git
cd wimbledon-api
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure MongoDB

In both `main.py` and `scraper.py`, update the following line with your own MongoDB Atlas connection string:

```python
MongoClient("your-mongodb-connection-string")
```

Alternatively, you can configure this using environment variables if preferred.

### 4. Run Locally

```bash
python main.py
```

The API will be available at:

```
http://localhost:5000/wimbledon?year=2021
```

---

## API Usage

### Endpoint

```
GET /wimbledon?year=<YEAR>
```

### Example Request

```
GET /wimbledon?year=2002
```

### Successful Response

```json
{
  "year": 2002,
  "champion": "Lleyton Hewitt (AUS)",
  "runner_up": "David Nalbandian (ARG)",
  "score": "6-1, 6-3, 6-2",
  "sets": 3,
  "tiebreak": false
}
```

### Error Responses

* `400 Bad Request` – If the year is missing or not an integer.
* `404 Not Found` – If no data is found for the provided year.

---

## Background Scraper

* Runs automatically every 24 hours.
* Checks for the current year’s Wimbledon final.
* Updates the MongoDB Atlas database if new data is found.
* Runs as a background thread within the Flask server.

---

## Deployment on Render

### Steps to Deploy

1. Push the project to GitHub.
2. Go to [https://dashboard.render.com/](https://dashboard.render.com/).
3. Click "New Web Service" and connect your GitHub repository.
4. Leave the build command blank or use `pip install -r requirements.txt` if prompted.
5. Use the following start command:

   ```bash
   python main.py
   ```
6. Select the free plan.

Render will deploy the Flask API and the background scraper will run continuously.

---

## Future Improvements

* Add environment variable support for MongoDB credentials.
* Add CORS headers to support frontend integrations.
* Add a health check endpoint.
* Optionally, move to a task scheduler like APScheduler for better control.

---

## Credits

* Data Source: [Tennis-X Wimbledon Winners](https://www.tennis-x.com/winners/mens/wimbledon.php)
* Web scraping using BeautifulSoup and requests.
