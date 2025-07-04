import requests
from bs4 import BeautifulSoup
import json
import re
from pymongo import MongoClient
from datetime import datetime
import os

SECRET_KEY = os.getenv('MONGODB_URI')


class WimbledonScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)


        self.mongo_client = MongoClient(SECRET_KEY)
        self.db = self.mongo_client['wimbledonDB'] 
        self.collection = self.db['finalsData'] 

    def scrape_from_tennis_x(self):
        """Scrape Wimbledon finals data from tennis-x.com"""
        url = "https://www.tennis-x.com/winners/mens/wimbledon.php"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            finals_data = []
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')

                for row in rows[1:]:
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        year_text = cells[0].get_text(strip=True)
                        champion = cells[1].get_text(strip=True)
                        runner_up = cells[2].get_text(strip=True)
                        score = cells[3].get_text(strip=True)

                        year_match = re.search(r'\d{4}', year_text)
                        if year_match:
                            year = int(year_match.group())

                            sets_count, has_tiebreak = self.parse_score(score)

                            final_data = {
                                "year": year,
                                "champion": champion,
                                "runner_up": runner_up,
                                "score": score,
                                "sets": sets_count,
                                "tiebreak": has_tiebreak
                            }

                            finals_data.append(final_data)

            return finals_data

        except Exception as e:
            print(f"Error scraping from tennis-x.com: {e}")
            return []

    def parse_score(self, score: str) -> tuple:
        """Parse tennis score to determine number of sets and if there was a tiebreak"""
        if not score or score.strip() == "":
            return 0, False

        sets_parts = [s.strip() for s in score.split(',') if s.strip()]
        sets_count = len(sets_parts)
        has_tiebreak = False

        if re.search(r'\(.*?\)', score):
            has_tiebreak = True

        return sets_count, has_tiebreak

    def update_current_year_final(self):
        """Scrape and update only the current year's final if available"""
        current_year = datetime.now().year
        print(f"Checking for {current_year} Wimbledon final...")

        data = self.scrape_from_tennis_x()
        if not data:
            print("Could not fetch data.")
            return


        for record in data:
            if record['year'] == current_year:
                print(f"{current_year} final found. Updating database...")
                self.collection.update_one(
                    {'year': current_year},
                    {'$set': record},
                    upsert=True
                )
                print(f"{current_year} final successfully updated in MongoDB Atlas.")
                print(json.dumps(record, indent=2))
                return

        print(f"{current_year} final not found yet on the website.")

def main():
    scraper = WimbledonScraper()
    scraper.update_current_year_final()

if __name__ == "__main__":
    main()
