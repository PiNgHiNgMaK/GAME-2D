import urllib.request
import os

def go():
    target = os.path.join("assets", "sound", "crystal_break.mp3")
    url = "https://www.orangefreesounds.com/wp-content/uploads/2016/02/Plate-smashing-sound-effect.mp3"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = urllib.request.Request(url, headers=headers)
        data = urllib.request.urlopen(req).read()
        with open(target, "wb") as f:
            f.write(data)
        print(f"DONE: {os.path.getsize(target)}")
    except Exception as e:
        print(f"ERR: {e}")

if __name__ == "__main__":
    go()
