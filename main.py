from flask import Flask, request, jsonify
from pymongo import MongoClient
from threading import Thread
import time
from scraper import WimbledonScraper
import os
app = Flask(__name__)

SECRET_KEY = os.getenv('MONGODB_URI')
# MongoDB Atlas connection

client = MongoClient(SECRET_KEY)
db = client['wimbledonDB']
collection = db['finalsData']

@app.route('/wimbledon', methods=['GET'])
def get_wimbledon_final():
    year = request.args.get('year')

    if not year:
        return jsonify({"error": "Please provide a year in the query parameter. Example: /wimbledon?year=2021"}), 400

    try:
        year = int(year)
    except ValueError:
        return jsonify({"error": "Year must be an integer."}), 400

    final = collection.find_one({'year': year}, {'_id': 0})

    if final:
        return jsonify(final), 200
    else:
        return jsonify({"error": f"No data found for Wimbledon final {year}."}), 404

def background_scraper():
    scraper = WimbledonScraper()
    while True:
        scraper.update_current_year_final()
        print("Sleeping for 24 hours...")
        time.sleep(24 * 60 * 60)  # Sleep for 24 hours

if __name__ == "__main__":
    # Start the background thread for scraping
    # scraper_thread = Thread(target=background_scraper, daemon=True)
    # scraper_thread.start()

    # Start Flask server
    app.run(host='0.0.0.0', port=5000, debug=True)
