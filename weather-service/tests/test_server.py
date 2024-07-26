import unittest

from weather_service.utils import fetch_weather_data
from weather_service.main import CITIES, API_URL, OPENWEATHER_API_KEY


class APITestHandler(unittest.IsolatedAsyncioTestCase):
    async def test_get_weather_data(self):
        # Test the get_weather_data function
        for city in CITIES:
            weather_data = await fetch_weather_data(API_URL, OPENWEATHER_API_KEY, city)
            self.assertIsNotNone(weather_data)
            


if __name__ == '__main__':
    unittest.main()