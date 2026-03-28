import requests
import os
import re
from io import BytesIO
try:
    from PIL import Image
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False
    print("[!] ERROR: 'Pillow' library is not installed. Run 'pip install Pillow'")

# ==========================================
# কনফিগারেশন
# ==========================================
BING_JSON_URL = "https://raw.githubusercontent.com/srhady/bingstream/refs/heads/main/playlist.json"
OUTPUT_DIR = "bing_posters" 
DEFAULT_CUSTOM_LOGO = "https://static.vecteezy.com/system/resources/previews/016/314/808/original/transparent-live-transparent-live-icon-free-png.png"
MAX_IMAGE_SIZE_KB = 100
# ==========================================

def sanitize_filename(name):
    clean_name = re.sub(r'[\\/*?:"<>|]', "", name)
    return clean_name.strip()

def download_and_save_default(save_path):
    try:
        res = requests.get(DEFAULT_CUSTOM_LOGO, timeout=10)
        if res.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(res.content)
            return True
    except:
        pass
    return False

def create_match_poster(match_name, home_logo_url, away_logo_url, local_path):
    if not PILLOW_INSTALLED:
        return

    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        print(f"    [=] Poster already exists for: {match_name}")
        return

    if not home_logo_url or not away_logo_url or ".svg" in home_logo_url.lower() or ".svg" in away_logo_url.lower():
        print(f"    [-] Missing/SVG logo for '{match_name}'. Using custom default poster.")
        download_and_save_default(local_path)
        return

    try:
        print(f"    [*] Creating poster for: {match_name}...")
        img_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://google.com/"
        }
        
        home_res = requests.get(home_logo_url, headers=img_headers, timeout=10)
        away_res = requests.get(away_logo_url, headers=img_headers, timeout=10)
        
        if home_res.status_code != 200 or away_res.status_code != 200:
            print(f"    [!] Download failed. Using custom default poster.")
            download_and_save_default(local_path)
            return
        
        home_img = Image.open(BytesIO(home_res.content)).convert('RGBA')
        away_img = Image.open(BytesIO(away_res.content)).convert('RGBA')
        
        final_home = Image.new("RGB", home_img.size, (255, 255, 255))
        final_home.paste(home_img, mask=home_img.split()[3] if len(home_img.split()) == 4 else None)
        
        final_away = Image.new("RGB", away_img.size, (255, 255, 255))
        final_away.paste(away_img, mask=away_img.split()[3] if len(away_img.split()) == 4 else None)
        
        size = (300, 300)
        final_home = final_home.resize(size, Image.Resampling.LANCZOS)
        final_away = final_away.resize(size, Image.Resampling.LANCZOS)
        
        canvas = Image.new('RGB', (700, 300), color=(0, 0, 0))
        canvas.paste(final_home, (0, 0))
        canvas.paste(final_away, (400, 0))
        
        quality = 90
        while True:
            canvas.save(local_path, "JPEG", quality=quality, optimize=True)
            file_size_kb = os.path.getsize(local_path) / 1024
            if file_size_kb < MAX_IMAGE_SIZE_KB or quality <= 50:
                print(f"    [+] Success! Size: {file_size_kb:.1f} KB")
                break
            quality -= 5 

    except Exception as e:
        print(f"    [!] Error processing '{match_name}': {e}. Using default.")
        download_and_save_default(local_path)

# 💥 দ্য অটো-ডিলিট ফাংশন (পুরোনো ছবি মুছে ফেলার জন্য)
def clean_old_posters(active_filenames):
    print("\n[*] STEP 3: Cleaning up old posters...")
    if not os.path.exists(OUTPUT_DIR): return

    files_in_dir = os.listdir(OUTPUT_DIR)
    deleted_count = 0
    
    for file in files_in_dir:
        # শুধু .jpg ফাইল চেক করবে এবং যেটা বর্তমান লিস্টে নেই সেটা ডিলিট করবে
        if file.endswith('.jpg') and file not in active_filenames:
            try:
                os.remove(os.path.join(OUTPUT_DIR, file))
                deleted_count += 1
            except: pass
            
    print(f"   [+] Deleted {deleted_count} old posters to save repo space.")

def main():
    print(f"🚀 Starting Bing Poster Generator...")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created directory: {OUTPUT_DIR}")

    try:
        print(f"📥 Fetching JSON from {BING_JSON_URL}...")
        res = requests.get(BING_JSON_URL, timeout=15)
        data = res.json()
        
        matches = []
        if isinstance(data, dict):
            if "channels" in data:
                matches = data["channels"]
            else:
                matches = list(data.values())
        elif isinstance(data, list):
            matches = data
            
        print(f"📊 Found {len(matches)} total matches in 'channels'. Starting processing...\n")
        
        active_poster_filenames = [] # 💥 বর্তমানে যে ছবিগুলো লাগবে তার লিস্ট
        
        for index, match in enumerate(matches):
            if not isinstance(match, dict):
                continue
                
            team1 = match.get("Team 1 Name", "Unknown")
            team2 = match.get("Team 2 Name", "Unknown")
            match_title = match.get("Match Title")
            
            if not match_title or match_title.strip() == "":
                match_title = f"{team1} VS {team2}"
                
            logo1 = match.get("Team 1 Logo", "")
            logo2 = match.get("Team 2 Logo", "")
            
            # ফাইলের নাম তৈরি এবং লিস্টে অ্যাড করা
            safe_name = sanitize_filename(match_title)
            final_filename = f"{safe_name}.jpg"
            local_path = os.path.join(OUTPUT_DIR, final_filename)
            active_poster_filenames.append(final_filename)
            
            create_match_poster(match_title, logo1, logo2, local_path)
            
        # 💥 সব ম্যাচ প্রসেস হওয়ার পর পুরোনো ছবি ক্লিন করা
        clean_old_posters(active_poster_filenames)
            
        print("\n🎉 All posters generated and cleaned up successfully!")
        print(f"📂 Check the '{OUTPUT_DIR}' folder.")

    except Exception as e:
        print(f"\n[!] Fatal Error: Could not fetch or process JSON. {e}")

if __name__ == "__main__":
    main()
