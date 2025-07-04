import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict
from pymongo import MongoClient
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

    def scrape_from_tennis_x(self) -> List[Dict]:
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

    def scrape_all_sources(self) -> List[Dict]:
        """Try scraping from multiple sources"""
        all_data = []

        print("Trying to scrape from tennis-x.com...")
        data = self.scrape_from_tennis_x()
        if data:
            all_data.extend(data)
            print(f"Successfully scraped {len(data)} records from tennis-x.com")

        time.sleep(2)

        unique_data = {}
        for item in all_data:
            year = item.get('year')
            if year and year not in unique_data:
                unique_data[year] = item

        return list(unique_data.values())

    def save_to_mongo(self, finals_data: List[Dict]):
        """Save the scraped data to MongoDB Atlas"""
        if not finals_data:
            print("No data to save.")
            return

        try:
            for record in finals_data:
                self.collection.update_one(
                    {'year': record['year']},
                    {'$set': record},
                    upsert=True
                )
            print("Data successfully saved to MongoDB Atlas.")
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")

def main():
    scraper = WimbledonScraper()

    print("Starting Wimbledon finals data scraping...")
    print("=" * 50)

    finals_data = scraper.scrape_all_sources()

    if finals_data:
        finals_data.sort(key=lambda x: x.get('year', 0))

        print(f"\nSuccessfully scraped {len(finals_data)} Wimbledon finals records:")
        print("=" * 50)

        for final in finals_data:
            print(json.dumps(final, indent=2))
            print("-" * 30)

        scraper.save_to_mongo(finals_data)

    else:
        print("No data could be scraped from any source.")

if __name__ == "__main__":
    main()
