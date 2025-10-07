# 🔍 UPC Validator: Real-Time Barcode Checker & Decoder

A comprehensive Windows desktop application built in **pure Python** using **Tkinter** for validating and decoding UPC-A barcodes in real-time.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

### Core Functionality
- ✅ **Real-time UPC-A (12-digit) validation**
- 🔢 **Check-digit formula validation**: `3a₁ + a₂ + 3a₃ + a₄ + 3a₅ + a₆ + 3a₇ + a₈ + 3a₉ + a₁₀ + 3a₁₁ + a₁₂ ≡ 0 (mod 10)`
- 🔍 **Missing digit solver** - Use `?` to represent unknown digits
- 📊 **Comprehensive decoding** - Product type, manufacturer code, product code, check digit
- 🎨 **Color-coded validation** - Green for valid, red for invalid

### Advanced Features
- 📷 **Webcam barcode scanner** - Real-time scanning using your camera
- 🖼️ **Barcode generator** - Create PNG/JPG barcode images
- 📁 **Batch validation** - Import and validate multiple UPCs from CSV/TXT files
- 💾 **Export capabilities** - Save results to CSV or PDF
- 📜 **History tracking** - SQLite database stores all validations
- 🌓 **Dark/Light mode** - Toggle between themes
- ⌨️ **Keyboard shortcuts** - Quick access to common functions

### Product Type Detection
- **0** → General groceries
- **2** → Meat and produce (variable weight)
- **3** → Drugs & health products
- **4** → Non-food items
- **5** → Coupons
- **6, 7** → Other items
- **1, 8, 9** → Reserved for future use

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Windows OS (tested on Windows 10/11)

### Step 1: Clone or Download
```bash
git clone <repository-url>
cd upc-validator
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Required Dependencies:
- **Pillow** - Image processing
- **python-barcode** - Barcode generation

#### Optional Dependencies (for full functionality):
- **opencv-python** - Webcam scanning
- **pyzbar** - Barcode reading
- **reportlab** - PDF export

### Step 3: Run the Application
```bash
python upc_validator_app.py
```

## 📖 Usage Guide

### Basic Validation
1. Launch the application
2. Enter a 12-digit UPC code in the input field
3. Click **✓ Validate** or press **Enter**
4. View the results with detailed breakdown

### Missing Digit Solver
1. Enter a UPC with `?` representing the unknown digit (e.g., `03600029145?`)
2. Click **✓ Validate**
3. The application will solve for the missing digit automatically

### Webcam Barcode Scanner
1. Click **📷 Scan** button
2. Position a UPC barcode in front of your webcam
3. The barcode will be automatically detected and validated
4. Press **ESC** to cancel scanning

### Barcode Generator
1. Enter or validate a UPC code
2. Click **🖼 Generate Barcode Image**
3. Choose save location
4. Preview appears in the results section

### Batch Validation
1. Click **📁 Batch** button
2. Select a CSV or TXT file containing UPC codes (one per line)
3. View validation results for all codes
4. Export results if needed

### Export Options
- **CSV Export**: Click **💾 Export History (CSV)** to save all validation history
- **PDF Export**: Click **📄 Export History (PDF)** for a formatted report

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Enter** | Validate current UPC |
| **Ctrl+C** | Copy UPC to clipboard |
| **Ctrl+V** | Paste UPC from clipboard |
| **Esc** | Exit application |

## 📁 File Structure

```
upc-validator/
│
├── upc_validator_app.py    # Main application file
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── upc_history.db          # SQLite database (created on first run)
```

## 🎨 UI Overview

The application features a modern, user-friendly interface with:

- **Header Section**: Application title and subtitle
- **Input Section**: UPC entry field with action buttons
- **Results Section**: Detailed validation results and barcode preview
- **History Panel**: Recent validations with timestamps
- **Settings Panel**: Theme toggle, export options, and about dialog

## 🔧 Troubleshooting

### pyzbar Installation Issues (Windows)
If you encounter errors with pyzbar:
1. Download Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install zbar from: https://sourceforge.net/projects/zbar/files/zbar/
3. Alternatively, try: `pip install pyzbar-windows`

### Webcam Not Working
- Ensure no other application is using the webcam
- Check Windows privacy settings for camera access
- Verify OpenCV installation: `python -c "import cv2; print(cv2.__version__)"`

### Barcode Generation Issues
- Ensure Pillow and python-barcode are installed
- Check file permissions for save location

## 📝 UPC Validation Algorithm

The application validates UPC codes using the standard check-digit formula:

```
Sum = 3×d₁ + d₂ + 3×d₃ + d₄ + 3×d₅ + d₆ + 3×d₇ + d₈ + 3×d₉ + d₁₀ + 3×d₁₁ + d₁₂

Valid if: Sum ≡ 0 (mod 10)
```

Where:
- Odd positions (1, 3, 5, 7, 9, 11) are multiplied by 3
- Even positions (2, 4, 6, 8, 10, 12) are multiplied by 1
- The sum must be divisible by 10

## 🎯 Example UPC Codes for Testing

Try these valid UPC codes:

- `036000291452` - Tide Detergent
- `012000161155` - Coca-Cola
- `078000082487` - Lucky Charms
- `041196403091` - Skippy Peanut Butter
- `492750209310` - Test UPC

## 🤝 Contributing

This is a complete, standalone application. Feel free to:
- Report bugs or issues
- Suggest new features
- Submit pull requests
- Fork and customize for your needs

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- Built with Python's Tkinter for cross-platform GUI
- Barcode generation powered by python-barcode
- Barcode scanning using OpenCV and pyzbar
- PDF generation with reportlab

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Ensure all dependencies are installed correctly
3. Verify Python version (3.8+)

---

**Made with ❤️ using Pure Python and Tkinter**

Enjoy validating barcodes! 🎉