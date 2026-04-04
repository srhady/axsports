import requests
import json
from datetime import datetime

url = "https://www.fancode.com/graphql"

headers = {
    "authority": "www.fancode.com",
    "accept": "*/*",
    "content-type": "application/json",
    "cookie": "dh_user_id=c2766dd0-1ada-11f1-b7c8-5f5d7ef9b5b8; WZRK_G=22eddc9bffc349bf97a08327005c622c; WZRK_S_W84-8RR-RR5Z=%7B%22p%22%3A11%2C%22s%22%3A1773022719%2C%22t%22%3A1773025016%7D",
    "fc-device-type": "mobile",
    "fc-x-country-code": "BD",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36"
}

params = {
    "extensions": '{"persistedQuery":{"version":1,"sha256Hash":"3cd8aef512f61ce11d8fd48f117423632c901595b154d92dbfe89dfccf379e5a"}}',
    "operation": "query",
    "operationName": "LiveNowMatches",
    "variables": '{"limit":12,"countryId":6668}'
}

try:
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        raw_data = response.json()
        edges = raw_data.get('data', {}).get('liveNowMatches', {}).get('edges', [])

        formatted_list = []
        seen_ids = set() # ডবল প্রিন্ট বন্ধ করার জন্য ফিল্টার

        for edge in edges:
            for match_item in edge.get('topMatches', []):
                match_id = match_item.get('id')

                # যদি ম্যাচটি আগেই লিস্টে যোগ করা হয়ে থাকে, তবে এটি এড়িয়ে যাবে
                if match_id in seen_ids:
                    continue
                seen_ids.add(match_id)

                match_data = match_item.get('match', {})
                teams = match_data.get('teams', [])

                t1 = teams[0].get('name', 'N/A') if len(teams) > 0 else 'N/A'
                t2 = teams[1].get('name', 'N/A') if len(teams) > 1 else 'N/A'

                # আপনার কাঙ্ক্ষিত ফরম্যাটে ডেটা সাজানো
                obj = {
                    "event_category": match_item.get('tour', {}).get('slug', '').split('-')[0].capitalize(),
                    "title": f"{t1} vs {t2}",
                    "src": match_item.get('features', {}).get('matchSportyBgImage', ''),
                    "team_1": t1,
                    "team_2": t2,
                    "status": "LIVE",
                    "event_name": match_item.get('tour', {}).get('name', ''),
                    "match_name": match_data.get('name', ''),
                    "match_id": match_id,
                    "startTime": "11:30:00 PM 08-03-2026", # টেম্পলেট টাইম
                    "dai_url": f"https://fancode.com/match/{match_id}",
                    "adfree_url": f"https://fancode.com/match/{match_id}"
                }
                formatted_list.append(obj)

        # জেসন ফরম্যাটে ডেটা তৈরি
        output_data = json.dumps(formatted_list, indent=4)
        print("Data Scraped Successfully!")
        
        # গিটহাবে পুশ করার জন্য ফাইলে সেভ করা
        with open("fancode_matches.json", "w", encoding="utf-8") as f:
            f.write(output_data)

    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
