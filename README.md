# 🎮 The Echo of the Abyss: Reversed Fate

**The Echo of the Abyss: Reversed Fate** เป็นเกมแนว 2D Action Side-Scroller ที่พัฒนาด้วยภาษา Python และ `pygame-ce` ผู้เล่นจะรับบทเป็นอัศวินผู้กล้าที่ต้องบุกตะลุยผ่านดินแดนที่ถูกความมืดกลืนกิน

---

## 👥 ข้อมูลทีมพัฒนา

**ชื่อทีม:** Game2D Dev Team

| ลำดับ | ชื่อ-นามสกุล | บทบาท |
|-------|--------------|-------|
| 1 | นาย วุฒิภัทร วิริยเสนกุล รหัสนักศึกษา 68114540605 | Game Developer |
| 2 | นาย ภัทรพงษ์ จรรยากรณ์ รหัสนักศึกษา 68114540434 | Game Developer |

---

## 🚀 วิธีการติดตั้งและรันเกม (Installation & Usage)

### 📦 วิธีที่ 1: ใช้ `uv` (แนะนำ - เสถียรที่สุด)
หากคุณมี [uv](https://github.com/astral-sh/uv) ติดตั้งอยู่ในเครื่องแล้ว สามารถรันเกมได้ทันที:
```bash
# 1. ติดตั้ง dependencies ทั้งหมด
uv sync

# 2. เริ่มรันเกม
uv run main.py
```

### 🐍 วิธีที่ 2: ใช้ `pip` แบบปกติ
```bash
# 1. ติดตั้ง Library ที่จำเป็น
pip install -r requirements.txt

# 2. เริ่มรันเกม
python main.py
```

---

## 🕹️ วิธีการเล่น (Controls)

| ปุ่ม | การกระทำ |
|------|----------|
| `←` / `→` หรือ `A` / `D` | เดินซ้าย / ขวา |
| `L-Shift` + ทิศทาง | วิ่ง (ใช้ Stamina) |
| `Space` / `W` / `↑` | กระโดด |
| `Z` หรือ `คลิกซ้าย` | โจมตีหนัก (ดาเมจ x2 / ใช้ Stamina 50%) |
| `C` หรือ `Shift + คลิกซ้าย` | โจมตีปกติ (รวดเร็ว / ใช้ Stamina 25%) |
| `X` หรือ `คลิกขวา` | ป้องกัน (ลดดาเมจ 50% / หากกดถูกจังหวะจะเป็น Parry 100%) |
| `ESC` / `P` | หยุดเกม (Pause) |

---

## ✨ รายละเอียดและคุณสมบัติของเกม

*   **Combat System**: ระบบการต่อสู้ที่ต้องบริหาร Stamina และการทำ Perfect Parry เพื่อป้องกันการโจมตี
*   **Progressive Scenes**: ดำเนินเรื่องผ่าน 4 ฉากหลัก (Night Forest, Mystic Ruins, Throne Room, Abyss Core)
*   **Boss Fights**: เผชิญหน้ากับศัตรูที่หลากหลายและบอสใหญ่ที่มี AI รูปแบบเฉพาะตัว
*   **Visual Juice**: เอฟเฟกต์ Screen Shake, Particles, และระบบแสงสี (Vignette) เพื่อบรรยากาศที่สมจริง

---

## 📁 โครงสร้างไฟล์ในโปรเจกต์

```
Game2d/
├── main.py          # ไฟล์หลักสำหรับรันเกมและจัดการฉาก (Scene Management)
├── player.py        # ระบบตัวละครผู้เล่น (Movement, Combat, Status)
├── monster.py       # ระบบศัตรูและ AI (NightBorne, Evil Wizard)
├── boss.py          # ระบบบอส (Demon Slime) และ Boss UI
├── puzzle.py        # ระบบปริศนาภายในเกม
├── story.py         # ระบบบทสนทนาและเนื้อเรื่อง
├── effects.py       # ระบบเอฟเฟกต์ภาพและอนุภาค (Particles)
├── background/      # ระบบ Parallax Background
└── assets/          # ทรัพยากรเกม (Sprites, Sounds, Fonts)
```

---

## ⚙️ ความต้องการของระบบ
*   **Python**: Version 3.14 ขึ้นไป
*   **Library**: `pygame-ce` (จะถูกติดตั้งอัตโนมัติผ่าน `uv sync` หรือ `pip install`)

---

*หมายเหตุ: เกมนี้เป็นส่วนหนึ่งของการศึกษาและพัฒนาเกมด้วย Python (pygame-ce)*