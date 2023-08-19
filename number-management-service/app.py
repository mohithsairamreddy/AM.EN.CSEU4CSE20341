from flask import Flask, request, jsonify
import asyncio
import aiohttp
import uvloop  # A faster event loop implementation
import os

app = Flask(__name__)

# Asynchronous function to fetch data from a URL
async def fetch_numbers_async(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()  # Raise exception for non-200 status codes
            data = await response.json()  # Parse JSON data
            return data
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None

# Route to handle the /numbers endpoint
@app.route('/numbers', methods=['GET'])
async def get_numbers():
    urls = request.args.getlist('url')  # Get list of URLs from query parameters

    if not urls:
        return jsonify(error="No URLs provided"), 400

    results = []

    # Create an aiohttp session with a connection pool
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit_per_host=len(urls))) as session:
        # Create a list of asynchronous tasks
        tasks = [fetch_numbers_async(session, url) for url in urls]
        results = await asyncio.gather(*tasks)  # Gather results from tasks

    return jsonify(results)

if __name__ == '__main__':
    if 'MODE' in os.environ and os.environ['MODE'] == 'production':
        uvloop.install()  # Use uvloop for the event loop in production mode
        app.run(host='0.0.0.0', port=8008)  # Run the app on all available network interfaces
    else:
        app.run(host='localhost', port=8008)  # Run the app on localhost for development
