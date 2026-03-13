# 🎮 Jao Ting Nong — 2D Action Game

เกม 2D Action สไตล์ Side-Scroller ที่พัฒนาด้วย Python และ pygame-ce ผู้เล่นจะรับบทเป็นอัศวิน ต้องต่อสู้กับมอนสเตอร์และบอส เพื่อผ่านด่านทั้ง 4 ฉาก

---

## 👥 ทีมพัฒนา

**ชื่อทีม:** Game2D Dev Team

| ลำดับ | ชื่อ-นามสกุล | บทบาท |
|-------|--------------|-------|
| 1 | สมาชิกคนที่ 1 | Game Developer |
| 2 | สมาชิกคนที่ 2 | Game Developer |

> ⚠️ กรุณาแก้ไขชื่อสมาชิกให้ตรงกับทีมจริงด้านบน

---

## 🕹️ วิธีการเล่น

| ปุ่ม | การกระทำ |
|------|----------|
| `←` / `→` หรือ `A` / `D` | เดินซ้าย / ขวา |
| `Shift` + ทิศทาง | วิ่ง (ใช้ Stamina) |
| `Space` / `W` / `↑` | กระโดด |
| `Z` หรือ คลิกซ้าย | โจมตีท่าที่ 1 (ใช้ Stamina 50%) |
| `C` หรือ `Shift` + คลิกซ้าย | โจมตีท่าที่ 2 (ใช้ Stamina 25%) |
| `X` หรือ คลิกขวา | ป้องกัน (ลดดาเมจ 90%) |
| `ESC` | หยุดเกม / เล่นต่อ |

---

## ⚙️ ความต้องการของระบบ

- Python **3.14** หรือสูงกว่า
- [uv](https://github.com/astral-sh/uv) (แนะนำ) หรือ pip

---

## 🚀 วิธีการติดตั้งและรันเกม

### วิธีที่ 1 — ใช้ `uv` (แนะนำ)

```bash
# 1. ติดตั้ง uv (ถ้ายังไม่มี)
pip install uv

# 2. ติดตั้ง dependencies
uv sync

# 3. รันเกม
uv run main.py
```

### วิธีที่ 2 — ใช้ `pip` + `venv`

```bash
# 1. สร้าง Virtual Environment
python -m venv .venv

# 2. เปิดใช้งาน Virtual Environment
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. ติดตั้ง dependencies จาก requirements.txt
pip install -r requirements.txt

# 4. รันเกม
python main.py
```

---

## 📁 โครงสร้างโปรเจกต์

```
Game2d/
├── main.py          # ไฟล์หลัก — Game Loop และ Scene Management
├── player.py        # คลาส Player และระบบ Stamina / Combat
├── monster.py       # คลาส Necromancer (มอนสเตอร์)
├── boss.py          # คลาส DemonSlimeBoss และ BossUI
├── menu.py          # ระบบ Menu ทั้งหมด (Main, Settings, Pause, GameOver)
├── background/      # ไฟล์รูปภาพพื้นหลังฉาก (bg-1.jpg ถึง bg-4.jpg)
│   └── back_g.py    # คลาส background สำหรับวาดพื้นหลัง
├── assets/
│   ├── player/      # Sprite Sheet ของ Player (Knight)
│   └── sound/       # ไฟล์เสียง BGM และ SFX ต่างๆ
├── requirements.txt # รายการ Library ที่ใช้ (pip)
└── pyproject.toml   # การตั้งค่าโปรเจกต์ (uv / PEP 517)
```