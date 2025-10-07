# 🚀 Quick Start Guide

## Installation (3 Easy Steps)

### 1️⃣ Install Python
Make sure you have Python 3.8 or higher installed:
```bash
python --version
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

**Minimal installation** (just validation and barcode generation):
```bash
pip install Pillow python-barcode
```

**Full installation** (all features including webcam scanning):
```bash
pip install Pillow python-barcode opencv-python pyzbar reportlab
```

### 3️⃣ Run the Application
```bash
python upc_validator_app.py
```

## 🎯 Quick Test

Want to test without the GUI first?
```bash
python test_upc_validator.py
```

## 📝 Sample UPC Codes to Try

Copy and paste these into the application:

| UPC Code | Product |
|----------|---------|
| `036000291452` | Tide Detergent |
| `012000161155` | Coca-Cola |
| `078000082487` | Lucky Charms |
| `041196403091` | Skippy Peanut Butter |

## 🔍 Try the Missing Digit Solver

Enter this in the app:
```
03600029145?
```

Click **Validate** and watch it solve for the `?`!

## 📷 Using the Webcam Scanner

1. Click **📷 Scan** button
2. Hold a product barcode up to your webcam
3. Watch it automatically fill in and validate!

**Note**: Requires `opencv-python` and `pyzbar` to be installed.

## 🎨 Features at a Glance

### Basic Features (Always Available)
- ✅ UPC validation
- 🔢 Check digit calculation
- 📊 Product type decoding
- 💾 History tracking
- 🌓 Dark/Light mode

### Advanced Features (Require Optional Dependencies)
- 📷 Webcam scanner → Needs: `opencv-python`, `pyzbar`
- 🖼️ Barcode generator → Needs: `python-barcode`, `Pillow`
- 📄 PDF export → Needs: `reportlab`

## ⚡ Keyboard Shortcuts

- **Enter** → Validate
- **Ctrl+C** → Copy UPC
- **Ctrl+V** → Paste UPC
- **Esc** → Exit

## 🐛 Troubleshooting

### "Module not found" errors?
```bash
pip install --upgrade -r requirements.txt
```

### Webcam not working?
1. Make sure no other app is using the camera
2. Check Windows privacy settings (Camera access)
3. Install Visual C++ Redistributable if needed

### pyzbar issues on Windows?
```bash
pip install pyzbar-windows
```

Or download zbar manually from:
https://sourceforge.net/projects/zbar/files/zbar/

## 📖 Learn More

See [README.md](README.md) for complete documentation.

---

**Ready to validate some barcodes?** 🎉

```bash
python upc_validator_app.py
```