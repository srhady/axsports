import requests
import os
import re
from io import BytesIO
try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False
    print("[!] ERROR: 'Pillow' library is not installed. Run 'pip install Pillow'")

BING_JSON_URL = "https://raw.githubusercontent.com/srhady/bingstream/refs/heads/main/playlist.json"
OUTPUT_DIR = "bing_posters" 
DEFAULT_CUSTOM_LOGO = "https://static.vecteezy.com/system/resources/previews/016/314/808/original/transparent-live-transparent-live-icon-free-png.png"
MAX_IMAGE_SIZE_KB = 100

# আপনার দেওয়া স্পোর্টস ক্যাটাগরির ডিফল্ট লোগো লিস্ট
DEFAULT_LOGOS = {
    "mma": "https://w7.pngwing.com/pngs/714/436/png-transparent-mma-logo-ultimate-fighting-championship-mixed-martial-arts-combat-bellator-mma-knockout-mma-hd-text-logo-monochrome-thumbnail.png",
    "auto racing": "https://thumbs.dreamstime.com/b/car-racing-logo-vector-icon-design-graphic-digital-print-media-modern-minimalist-featuring-clean-lines-bold-shapes-351924713.jpg",
    "football": "https://t3.ftcdn.net/jpg/16/40/17/22/360_F_1640172224_LE3IdZX5pPSlZCywBcz21BxOjMvD2Rlu.jpg",
    "cycling": "https://img.magnific.com/premium-vector/stylized-cycling-logo-sports-teams-events_1347451-390.jpg?semt=ais_hybrid&w=740&q=80",
    "tennis": "https://static.vecteezy.com/system/resources/previews/067/603/366/non_2x/logo-design-of-a-tennis-player-in-action-with-racket-and-ball-free-vector.jpg",
    "rugby": "https://thumbs.dreamstime.com/b/rugby-logo-american-logo-sport-sport-team-rugby-logo-american-logo-sport-108509744.jpg",
    "sailing": "https://upload.wikimedia.org/wikipedia/en/3/3c/World_Sailing_logo_local.svg",
    "darts": "https://media.istockphoto.com/id/1183783901/vector/darts-game-emblem.jpg?s=612x612&w=0&k=20&c=JX59kkZMYRO_DW0YsiDAnaZeLVAIWajzA4l6jwhxeDo=",
    "badminton": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTvB8ofwYTkpTbgh2XfHTDiZFFOo5zaSNHjbKBptd71Rg&s=10",
    "volleyball": "https://png.pngtree.com/thumb_back/fh260/background/20240119/pngtree-female-volleyball-player-hitting-the-ball-vintage-t-shirt-logo-post-image_15612064.jpg",
    "other": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQKx6oe6c7zzkeW4LWj8PFa9CZML4vlrJSY8fwqamguug&s=10"
}
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
        
        def make_circle(img):
            size = (260, 260)
            img = img.resize(size, Image.Resampling.LANCZOS)
            mask = Image.new('L', size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)
            circular_img = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
            circular_img.putalpha(mask)
            
            border_size = (280, 280)
            c = Image.new('RGBA', border_size, (0, 0, 0, 0))
            draw_c = ImageDraw.Draw(c)
            draw_c.ellipse((0, 0) + border_size, fill=(255, 255, 255, 255))
            offset = ((border_size[0] - size[0]) // 2, (border_size[1] - size[1]) // 2)
            c.paste(circular_img, offset, circular_img)
            
            shadow = Image.new('RGBA', (320, 320), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.ellipse((20, 20, 300, 300), fill=(0, 0, 0, 160))
            shadow = shadow.filter(ImageFilter.GaussianBlur(12))
            shadow.paste(c, (20, 20), c)
            return shadow

        logo1 = make_circle(home_img)
        logo2 = make_circle(away_img)
        
        font_path = "sports_font.ttf"
        if not os.path.exists(font_path):
            try:
                import urllib.request
                urllib.request.urlretrieve("https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf", font_path)
            except: pass
                
        try:
            font_vs = ImageFont.truetype(font_path, 100)
            font_title = ImageFont.truetype(font_path, 50)
        except:
            font_vs = ImageFont.load_default()
            font_title = ImageFont.load_default()

        canvas = Image.new('RGB', (1000, 562), color=(15, 15, 20))
        draw = ImageDraw.Draw(canvas)
        
        draw.polygon([(0,0), (450,0), (520,562), (0,562)], fill=(35, 35, 40))
        draw.polygon([(450,0), (1000,0), (1000,562), (520,562)], fill=(15, 25, 45))
        draw.polygon([(430,0), (470,0), (540,562), (500,562)], fill=(220, 20, 40))
        
        overlay = Image.new('RGBA', (1000, 562), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for x in range(0, 1000, 6):
            for y in range(0, 562, 6):
                overlay_draw.point((x, y), fill=(0, 0, 0, 30))
        overlay_draw.ellipse((425, 205, 585, 365), fill=(0, 0, 0, 160))
        overlay = overlay.filter(ImageFilter.GaussianBlur(10))
        canvas.paste(overlay, (0, 0), overlay)

        draw.rectangle([(0,0), (1000, 5)], fill=(200,200,200))
        draw.rectangle([(0,557), (1000, 562)], fill=(200,200,200))

        canvas.paste(logo1, (80, 110), logo1)
        canvas.paste(logo2, (600, 110), logo2)
        
        circle_bbox = (420, 200, 580, 360)
        draw.ellipse(circle_bbox, fill=(10, 10, 15), outline=(255, 255, 255), width=6)
        
        vs_text = "VS"
        try:
            vs_bbox = font_vs.getbbox(vs_text)
            vs_w = vs_bbox[2] - vs_bbox[0]
            vs_h = vs_bbox[3] - vs_bbox[1]
            vs_x = 500 - (vs_w / 2)
            vs_y = 280 - (vs_h / 2) - 15
            draw.text((vs_x + 3, vs_y + 3), vs_text, fill=(0, 0, 0, 180), font=font_vs)
            draw.text((vs_x, vs_y), vs_text, fill=(255, 255, 255), font=font_vs)
        except:
            draw.text((470, 260), vs_text, fill=(255, 255, 255))
        
        try:
            title_bbox = font_title.getbbox(match_name)
            title_w = title_bbox[2] - title_bbox[0]
            title_x = 500 - (title_w / 2)
            draw.text((title_x + 2, 480 + 2), match_name, fill=(0, 0, 0, 180), font=font_title)
            draw.text((title_x, 480), match_name, fill=(255, 255, 255), font=font_title)
        except:
            draw.text((350, 480), match_name, fill=(255, 255, 255))
        
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


def clean_old_posters(active_filenames):
    print("\n[*] STEP 3: Cleaning up old posters...")
    if not os.path.exists(OUTPUT_DIR): return

    files_in_dir = os.listdir(OUTPUT_DIR)
    deleted_count = 0
    
    for file in files_in_dir:
        
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
        
        active_poster_filenames = [] 
        
        for index, match in enumerate(matches):
            if not isinstance(match, dict):
                continue
                
            team1 = match.get("Team 1 Name", "Unknown")
            team2 = match.get("Team 2 Name", "Unknown")
            match_title = match.get("Match Title")
            
            if not match_title or match_title.strip() == "":
                match_title = f"{team1} VS {team2}"

            # --- আপনার দেওয়া লোগো রিপ্লেস করার লজিক এখানে যুক্ত করা হলো ---
            category_key = match.get("Category", "other").lower().strip()
            fallback_logo = DEFAULT_LOGOS.get(category_key, DEFAULT_LOGOS["other"])
                
            logo1 = match.get("Team 1 Logo", "").strip()
            logo2 = match.get("Team 2 Logo", "").strip()
            
            if not logo1: logo1 = fallback_logo
            if not logo2: logo2 = fallback_logo
            # ----------------------------------------------------------------
            
            safe_name = sanitize_filename(match_title)
            final_filename = f"{safe_name}.jpg"
            local_path = os.path.join(OUTPUT_DIR, final_filename)
            active_poster_filenames.append(final_filename)
            
            create_match_poster(match_title, logo1, logo2, local_path)
            
        clean_old_posters(active_poster_filenames)
            
        print("\n🎉 All posters generated and cleaned up successfully!")
        print(f"📂 Check the '{OUTPUT_DIR}' folder.")

    except Exception as e:
        print(f"\n[!] Fatal Error: Could not fetch or process JSON. {e}")

if __name__ == "__main__":
    main()
