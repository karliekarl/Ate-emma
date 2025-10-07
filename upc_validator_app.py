"""
UPC Validator: A Real-Time System for Validating and Decoding Product Barcodes
Complete Windows Desktop Application in Pure Python using Tkinter

Features:
- Real-time UPC-A (12-digit) validation
- Missing digit solver
- Barcode generator with preview
- Webcam barcode scanner
- Batch validation from CSV files
- Export results to CSV/PDF
- Validation history with SQLite storage
- Dark/Light mode toggle
- Keyboard shortcuts
- Sound notifications
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import re
import csv
import sqlite3
import os
import io
from datetime import datetime
from pathlib import Path
import threading
import time

# Optional imports with error handling
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import barcode
    from barcode.writer import ImageWriter
    BARCODE_AVAILABLE = True
except ImportError:
    BARCODE_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Import core UPC validation logic
from upc_core import UPCValidator


class BarcodeGenerator:
    """
    Generate barcode images for valid UPC codes.
    Uses python-barcode library to create UPC-A barcode images.
    """
    
    def __init__(self):
        self.last_image = None
    
    def generate(self, upc_code, output_path=None):
        """
        Generate barcode image for UPC code.
        Returns PIL Image object or None if generation fails.
        """
        if not BARCODE_AVAILABLE or not PIL_AVAILABLE:
            return None
        
        try:
            # Create UPC-A barcode
            upc_class = barcode.get_barcode_class('upca')
            
            # UPC-A expects 11 digits (adds check digit automatically)
            # But our UPC already has check digit, so we use it as-is
            upc_instance = upc_class(upc_code[:-1], writer=ImageWriter())
            
            # Generate to buffer
            buffer = io.BytesIO()
            upc_instance.write(buffer, options={
                'module_width': 0.3,
                'module_height': 10.0,
                'quiet_zone': 6.5,
                'font_size': 8,
                'text_distance': 3
            })
            
            # Load image from buffer
            buffer.seek(0)
            image = Image.open(buffer)
            self.last_image = image
            
            # Save to file if path provided
            if output_path:
                image.save(output_path)
            
            return image
            
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None


class BarcodeScanner:
    """
    Scan barcodes using webcam with OpenCV and pyzbar.
    Runs in separate thread to avoid blocking UI.
    """
    
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.thread = None
        self.cap = None
    
    def start(self):
        """Start webcam scanning in separate thread."""
        if not CV2_AVAILABLE or not PYZBAR_AVAILABLE:
            messagebox.showerror("Error", "OpenCV and pyzbar are required for scanning.\n"
                               "Install with: pip install opencv-python pyzbar")
            return False
        
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """Stop webcam scanning."""
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()
    
    def _scan_loop(self):
        """Main scanning loop running in separate thread."""
        try:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                if self.callback:
                    self.callback(None, "Could not open webcam")
                return
            
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Decode barcodes in frame
                barcodes = pyzbar.decode(frame)
                
                for barcode_obj in barcodes:
                    # Extract barcode data
                    barcode_data = barcode_obj.data.decode('utf-8')
                    barcode_type = barcode_obj.type
                    
                    # Check if it's a UPC
                    if barcode_type in ['UPCA', 'EAN13'] and len(barcode_data) >= 12:
                        # Get 12-digit UPC
                        upc = barcode_data[:12]
                        if self.callback:
                            self.callback(upc, None)
                        self.stop()
                        return
                    
                    # Draw rectangle around barcode
                    points = barcode_obj.polygon
                    if len(points) == 4:
                        pts = [(p.x, p.y) for p in points]
                        cv2.polylines(frame, [cv2.convexHull(cv2.UMat(pts))], True, (0, 255, 0), 2)
                
                # Display frame
                cv2.imshow('UPC Scanner - Position barcode in view', frame)
                
                # Check for ESC key to exit
                if cv2.waitKey(1) & 0xFF == 27:
                    break
            
        except Exception as e:
            if self.callback:
                self.callback(None, f"Scanner error: {e}")
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()


class UPCValidatorApp:
    """
    Main application class for UPC Validator.
    Handles UI creation, event handling, and feature integration.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("UPC Validator: Real-Time Barcode Checker & Decoder")
        
        # Set window size and position (centered)
        window_width = 1000
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Initialize variables
        self.dark_mode = False
        self.scanner = None
        self.history = []
        self.barcode_generator = BarcodeGenerator()
        
        # Color schemes
        self.light_colors = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'header_bg': '#2c3e50',
            'header_fg': '#ffffff',
            'entry_bg': '#ffffff',
            'button_bg': '#3498db',
            'button_fg': '#ffffff',
            'valid_fg': '#27ae60',
            'invalid_fg': '#e74c3c',
            'frame_bg': '#ffffff'
        }
        
        self.dark_colors = {
            'bg': '#2c3e50',
            'fg': '#ecf0f1',
            'header_bg': '#1a252f',
            'header_fg': '#ffffff',
            'entry_bg': '#34495e',
            'button_bg': '#3498db',
            'button_fg': '#ffffff',
            'valid_fg': '#2ecc71',
            'invalid_fg': '#e74c3c',
            'frame_bg': '#34495e'
        }
        
        self.colors = self.light_colors
        
        # Initialize database
        self.init_database()
        
        # Create UI
        self.create_widgets()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Apply initial theme
        self.apply_theme()
        
        # Load history
        self.load_history()
    
    def init_database(self):
        """Initialize SQLite database for history storage."""
        self.db_path = 'upc_history.db'
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upc_code TEXT NOT NULL,
                is_valid INTEGER NOT NULL,
                product_type TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_widgets(self):
        """Create all UI widgets."""
        
        # ===== HEADER SECTION =====
        header_frame = tk.Frame(self.root, bg=self.colors['header_bg'], height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🔍 UPC Validator",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colors['header_bg'],
            fg=self.colors['header_fg']
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Real-Time Barcode Checker & Decoder",
            font=('Segoe UI', 10),
            bg=self.colors['header_bg'],
            fg=self.colors['header_fg']
        )
        subtitle_label.pack()
        
        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel (Input and Results)
        left_panel = tk.Frame(main_container, bg=self.colors['bg'])
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # ===== INPUT SECTION =====
        input_frame = tk.LabelFrame(
            left_panel,
            text="📋 UPC Input",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            padx=15,
            pady=15
        )
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="Enter 12-digit UPC code (use ? for missing digit):",
            font=('Segoe UI', 10),
            bg=self.colors['frame_bg'],
            fg=self.colors['fg']
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.upc_entry = tk.Entry(
            input_frame,
            font=('Segoe UI', 14),
            bg=self.colors['entry_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            borderwidth=2
        )
        self.upc_entry.pack(fill=tk.X, pady=(0, 10), ipady=5)
        self.upc_entry.bind('<KeyRelease>', self.on_upc_change)
        
        # Buttons row
        button_frame = tk.Frame(input_frame, bg=self.colors['frame_bg'])
        button_frame.pack(fill=tk.X)
        
        self.validate_btn = tk.Button(
            button_frame,
            text="✓ Validate",
            font=('Segoe UI', 10, 'bold'),
            bg='#27ae60',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.validate_upc
        )
        self.validate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            button_frame,
            text="🗑 Clear",
            font=('Segoe UI', 10),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.clear_input
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📷 Scan",
            font=('Segoe UI', 10),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.start_scanner
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="📁 Batch",
            font=('Segoe UI', 10),
            bg='#9b59b6',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.batch_validate
        ).pack(side=tk.LEFT, padx=5)
        
        # ===== RESULTS SECTION =====
        results_frame = tk.LabelFrame(
            left_panel,
            text="📊 Validation Results",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            padx=15,
            pady=15
        )
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status label
        self.status_label = tk.Label(
            results_frame,
            text="Enter a UPC code to validate",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['frame_bg'],
            fg=self.colors['fg']
        )
        self.status_label.pack(pady=(0, 10))
        
        # Details text
        self.details_text = scrolledtext.ScrolledText(
            results_frame,
            height=10,
            font=('Consolas', 10),
            bg=self.colors['entry_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            borderwidth=2,
            wrap=tk.WORD
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Barcode preview label
        self.barcode_label = tk.Label(
            results_frame,
            text="Barcode preview will appear here",
            bg=self.colors['frame_bg'],
            fg=self.colors['fg']
        )
        self.barcode_label.pack(pady=5)
        
        # Generate barcode button
        tk.Button(
            results_frame,
            text="🖼 Generate Barcode Image",
            font=('Segoe UI', 9),
            bg='#16a085',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.generate_barcode
        ).pack(pady=5)
        
        # ===== RIGHT PANEL (History & Settings) =====
        right_panel = tk.Frame(main_container, bg=self.colors['bg'], width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # Settings frame
        settings_frame = tk.LabelFrame(
            right_panel,
            text="⚙ Settings",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            padx=10,
            pady=10
        )
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            settings_frame,
            text="🌓 Toggle Dark Mode",
            font=('Segoe UI', 9),
            bg='#34495e',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.toggle_dark_mode
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            settings_frame,
            text="💾 Export History (CSV)",
            font=('Segoe UI', 9),
            bg='#16a085',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.export_csv
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            settings_frame,
            text="📄 Export History (PDF)",
            font=('Segoe UI', 9),
            bg='#d35400',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.export_pdf
        ).pack(fill=tk.X, pady=2)
        
        tk.Button(
            settings_frame,
            text="ℹ About",
            font=('Segoe UI', 9),
            bg='#7f8c8d',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.show_about
        ).pack(fill=tk.X, pady=2)
        
        # History frame
        history_frame = tk.LabelFrame(
            right_panel,
            text="📜 Validation History",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['frame_bg'],
            fg=self.colors['fg'],
            padx=10,
            pady=10
        )
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # History listbox
        self.history_listbox = tk.Listbox(
            history_frame,
            font=('Consolas', 9),
            bg=self.colors['entry_bg'],
            fg=self.colors['fg'],
            relief=tk.FLAT,
            borderwidth=2
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(
            history_frame,
            text="🗑 Clear History",
            font=('Segoe UI', 8),
            bg='#c0392b',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.clear_history
        ).pack(fill=tk.X, pady=(5, 0))
        
        # ===== FOOTER =====
        footer_frame = tk.Frame(self.root, bg=self.colors['bg'], height=30)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        tk.Button(
            footer_frame,
            text="❌ Exit",
            font=('Segoe UI', 9),
            bg='#c0392b',
            fg='white',
            relief=tk.FLAT,
            padx=30,
            pady=5,
            cursor='hand2',
            command=self.exit_app
        ).pack(side=tk.RIGHT, padx=10, pady=5)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<Return>', lambda e: self.validate_upc())
        self.root.bind('<Escape>', lambda e: self.exit_app())
        self.root.bind('<Control-c>', lambda e: self.copy_result())
        self.root.bind('<Control-v>', lambda e: self.paste_input())
    
    def on_upc_change(self, event=None):
        """Real-time feedback as user types."""
        upc = self.upc_entry.get().strip()
        
        if not upc:
            self.status_label.config(text="Enter a UPC code to validate", fg=self.colors['fg'])
            return
        
        # Show length feedback
        if len(upc) < 12:
            self.status_label.config(
                text=f"⚠ Incomplete ({len(upc)}/12 digits)",
                fg='#f39c12'
            )
        elif len(upc) == 12:
            self.status_label.config(
                text="✓ Ready to validate",
                fg=self.colors['valid_fg']
            )
        else:
            self.status_label.config(
                text=f"⚠ Too long ({len(upc)}/12 digits)",
                fg=self.colors['invalid_fg']
            )
    
    def validate_upc(self):
        """Validate the entered UPC code."""
        upc = self.upc_entry.get().strip()
        
        if not upc:
            messagebox.showwarning("Warning", "Please enter a UPC code")
            return
        
        # Check for missing digit
        if '?' in upc or '_' in upc:
            self.solve_missing()
            return
        
        # Validate
        validator = UPCValidator(upc)
        is_valid = validator.validate()
        
        # Update UI
        if is_valid:
            self.status_label.config(
                text="✓ VALID UPC CODE",
                fg=self.colors['valid_fg']
            )
            
            details = f"""
╔═══════════════════════════════════════════╗
║         UPC CODE DETAILS                  ║
╚═══════════════════════════════════════════╝

UPC Code:          {validator.upc_code}
Status:            ✓ VALID
Product Type:      {validator.product_type}
Manufacturer Code: {validator.manufacturer_code}
Product Code:      {validator.product_code}
Check Digit:       {validator.check_digit}

═══════════════════════════════════════════
Validation Formula:
3×{validator.upc_code[0]} + {validator.upc_code[1]} + 3×{validator.upc_code[2]} + {validator.upc_code[3]} + 3×{validator.upc_code[4]} + {validator.upc_code[5]} + 
3×{validator.upc_code[6]} + {validator.upc_code[7]} + 3×{validator.upc_code[8]} + {validator.upc_code[9]} + 3×{validator.upc_code[10]} + {validator.upc_code[11]} 
≡ 0 (mod 10) ✓

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════
            """
            
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)
            
            # Play success sound (simple beep)
            try:
                self.root.bell()
            except:
                pass
            
        else:
            self.status_label.config(
                text="✗ INVALID UPC CODE",
                fg=self.colors['invalid_fg']
            )
            
            details = f"""
╔═══════════════════════════════════════════╗
║         VALIDATION FAILED                 ║
╚═══════════════════════════════════════════╝

UPC Code:  {validator.upc_code}
Status:    ✗ INVALID
Error:     {validator.error_message}

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════

Please check:
• Code must be exactly 12 digits
• All characters must be numeric
• Check digit must be correct
            """
            
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, details)
        
        # Save to history
        self.save_to_history(validator.upc_code, is_valid, validator.product_type)
    
    def solve_missing(self):
        """Solve for missing digit in UPC."""
        upc = self.upc_entry.get().strip()
        
        if len(upc) != 12:
            messagebox.showerror("Error", "UPC must be exactly 12 characters with one '?' or '_'")
            return
        
        validator = UPCValidator(upc)
        solved_upc = validator.solve_missing_digit()
        
        if solved_upc:
            self.upc_entry.delete(0, tk.END)
            self.upc_entry.insert(0, solved_upc)
            messagebox.showinfo("Success", f"Missing digit solved!\nComplete UPC: {solved_upc}")
            self.validate_upc()
        else:
            messagebox.showerror("Error", "Could not solve for missing digit.\nNo valid solution found.")
    
    def clear_input(self):
        """Clear input and results."""
        self.upc_entry.delete(0, tk.END)
        self.details_text.delete(1.0, tk.END)
        self.status_label.config(text="Enter a UPC code to validate", fg=self.colors['fg'])
        self.barcode_label.config(image='', text="Barcode preview will appear here")
    
    def start_scanner(self):
        """Start barcode scanner."""
        if not CV2_AVAILABLE or not PYZBAR_AVAILABLE:
            messagebox.showerror(
                "Missing Dependencies",
                "Barcode scanner requires OpenCV and pyzbar.\n\n"
                "Install with:\n"
                "pip install opencv-python pyzbar"
            )
            return
        
        self.scanner = BarcodeScanner(callback=self.on_barcode_scanned)
        if self.scanner.start():
            messagebox.showinfo(
                "Scanner Started",
                "Position a UPC barcode in front of your webcam.\n"
                "Press ESC to cancel scanning."
            )
    
    def on_barcode_scanned(self, upc, error):
        """Callback when barcode is scanned."""
        if error:
            messagebox.showerror("Scanner Error", error)
        elif upc:
            self.upc_entry.delete(0, tk.END)
            self.upc_entry.insert(0, upc)
            self.validate_upc()
            messagebox.showinfo("Success", f"Barcode scanned: {upc}")
    
    def generate_barcode(self):
        """Generate barcode image for current UPC."""
        upc = self.upc_entry.get().strip()
        
        if not upc or len(upc) != 12 or not upc.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid 12-digit UPC first")
            return
        
        if not BARCODE_AVAILABLE or not PIL_AVAILABLE:
            messagebox.showerror(
                "Missing Dependencies",
                "Barcode generation requires python-barcode and Pillow.\n\n"
                "Install with:\n"
                "pip install python-barcode pillow"
            )
            return
        
        # Ask where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Generate barcode
        image = self.barcode_generator.generate(upc, file_path)
        
        if image:
            # Display preview
            image_resized = image.copy()
            image_resized.thumbnail((400, 150))
            photo = ImageTk.PhotoImage(image_resized)
            self.barcode_label.config(image=photo, text="")
            self.barcode_label.image = photo  # Keep reference
            
            messagebox.showinfo("Success", f"Barcode saved to:\n{file_path}")
        else:
            messagebox.showerror("Error", "Failed to generate barcode image")
    
    def batch_validate(self):
        """Batch validate UPCs from CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV file with UPC codes",
            filetypes=[("CSV Files", "*.csv"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            results = []
            
            with open(file_path, 'r') as f:
                # Try to detect if it's CSV or plain text
                first_line = f.readline().strip()
                f.seek(0)
                
                if ',' in first_line:
                    reader = csv.reader(f)
                    upcs = [row[0].strip() for row in reader if row]
                else:
                    upcs = [line.strip() for line in f if line.strip()]
            
            # Validate each UPC
            for upc in upcs:
                validator = UPCValidator(upc)
                is_valid = validator.validate()
                results.append({
                    'upc': upc,
                    'valid': is_valid,
                    'error': validator.error_message if not is_valid else '',
                    'product_type': validator.product_type if is_valid else ''
                })
            
            # Show results dialog
            self.show_batch_results(results)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file:\n{e}")
    
    def show_batch_results(self, results):
        """Show batch validation results in a dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Batch Validation Results")
        dialog.geometry("700x500")
        
        # Summary
        valid_count = sum(1 for r in results if r['valid'])
        invalid_count = len(results) - valid_count
        
        tk.Label(
            dialog,
            text=f"Validated {len(results)} UPCs: {valid_count} valid, {invalid_count} invalid",
            font=('Segoe UI', 11, 'bold'),
            bg='#ecf0f1',
            fg='#2c3e50',
            pady=10
        ).pack(fill=tk.X)
        
        # Results text
        results_text = scrolledtext.ScrolledText(
            dialog,
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for i, r in enumerate(results, 1):
            status = "✓ VALID" if r['valid'] else "✗ INVALID"
            line = f"{i}. {r['upc']:12s} - {status:10s}"
            if r['valid']:
                line += f" - {r['product_type']}"
            else:
                line += f" - {r['error']}"
            results_text.insert(tk.END, line + "\n")
        
        results_text.config(state=tk.DISABLED)
        
        # Close button
        tk.Button(
            dialog,
            text="Close",
            command=dialog.destroy,
            bg='#3498db',
            fg='white',
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def save_to_history(self, upc, is_valid, product_type):
        """Save validation to history database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO validation_history (upc_code, is_valid, product_type, timestamp) VALUES (?, ?, ?, ?)',
                (upc, 1 if is_valid else 0, product_type, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            
            # Refresh history display
            self.load_history()
        except Exception as e:
            print(f"Error saving to history: {e}")
    
    def load_history(self):
        """Load validation history from database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT upc_code, is_valid, timestamp FROM validation_history ORDER BY id DESC LIMIT 50'
            )
            rows = cursor.fetchall()
            conn.close()
            
            # Clear listbox
            self.history_listbox.delete(0, tk.END)
            
            # Add history items
            for upc, is_valid, timestamp in rows:
                status = "✓" if is_valid else "✗"
                time_str = datetime.fromisoformat(timestamp).strftime('%m/%d %H:%M')
                self.history_listbox.insert(tk.END, f"{status} {upc} - {time_str}")
        except Exception as e:
            print(f"Error loading history: {e}")
    
    def clear_history(self):
        """Clear all validation history."""
        result = messagebox.askyesno(
            "Confirm",
            "Are you sure you want to clear all validation history?"
        )
        
        if result:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('DELETE FROM validation_history')
                conn.commit()
                conn.close()
                
                self.history_listbox.delete(0, tk.END)
                messagebox.showinfo("Success", "History cleared")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history:\n{e}")
    
    def export_csv(self):
        """Export history to CSV file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT upc_code, is_valid, product_type, timestamp FROM validation_history ORDER BY id DESC')
            rows = cursor.fetchall()
            conn.close()
            
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['UPC Code', 'Valid', 'Product Type', 'Timestamp'])
                for row in rows:
                    writer.writerow([row[0], 'Yes' if row[1] else 'No', row[2] or '', row[3]])
            
            messagebox.showinfo("Success", f"History exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{e}")
    
    def export_pdf(self):
        """Export history to PDF file."""
        if not PDF_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "PDF export requires reportlab.\n\n"
                "Install with:\n"
                "pip install reportlab"
            )
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT upc_code, is_valid, product_type, timestamp FROM validation_history ORDER BY id DESC')
            rows = cursor.fetchall()
            conn.close()
            
            # Create PDF
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(1*inch, height - 1*inch, "UPC Validation History Report")
            
            # Metadata
            c.setFont("Helvetica", 10)
            c.drawString(1*inch, height - 1.3*inch, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(1*inch, height - 1.5*inch, f"Total Records: {len(rows)}")
            
            # Table header
            y = height - 2*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "UPC Code")
            c.drawString(2.5*inch, y, "Valid")
            c.drawString(3.5*inch, y, "Product Type")
            c.drawString(5*inch, y, "Timestamp")
            
            # Table rows
            c.setFont("Helvetica", 9)
            y -= 0.2*inch
            
            for row in rows:
                if y < 1*inch:  # New page if needed
                    c.showPage()
                    y = height - 1*inch
                
                c.drawString(1*inch, y, row[0])
                c.drawString(2.5*inch, y, "Yes" if row[1] else "No")
                c.drawString(3.5*inch, y, row[2] or "N/A")
                c.drawString(5*inch, y, row[3][:16])
                y -= 0.2*inch
            
            c.save()
            messagebox.showinfo("Success", f"History exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF:\n{e}")
    
    def toggle_dark_mode(self):
        """Toggle between dark and light mode."""
        self.dark_mode = not self.dark_mode
        self.colors = self.dark_colors if self.dark_mode else self.light_colors
        self.apply_theme()
    
    def apply_theme(self):
        """Apply current color theme to all widgets."""
        self.root.config(bg=self.colors['bg'])
        
        # Recursively update all widgets
        def update_widget_colors(widget):
            try:
                widget_type = widget.winfo_class()
                
                if widget_type in ['Frame', 'Labelframe']:
                    widget.config(bg=self.colors['bg'])
                elif widget_type == 'Label':
                    if 'header' not in str(widget):
                        widget.config(bg=self.colors['bg'], fg=self.colors['fg'])
                elif widget_type == 'Entry':
                    widget.config(bg=self.colors['entry_bg'], fg=self.colors['fg'])
                elif widget_type == 'Text':
                    widget.config(bg=self.colors['entry_bg'], fg=self.colors['fg'])
                elif widget_type == 'Listbox':
                    widget.config(bg=self.colors['entry_bg'], fg=self.colors['fg'])
                
                for child in widget.winfo_children():
                    update_widget_colors(child)
            except:
                pass
        
        update_widget_colors(self.root)
    
    def copy_result(self):
        """Copy UPC to clipboard."""
        upc = self.upc_entry.get().strip()
        if upc:
            self.root.clipboard_clear()
            self.root.clipboard_append(upc)
            self.status_label.config(text="Copied to clipboard!", fg=self.colors['fg'])
    
    def paste_input(self):
        """Paste from clipboard to input."""
        try:
            clipboard = self.root.clipboard_get()
            self.upc_entry.delete(0, tk.END)
            self.upc_entry.insert(0, clipboard.strip())
        except:
            pass
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
UPC Validator v1.0
Real-Time Barcode Checker & Decoder

A comprehensive desktop application for validating
and decoding UPC-A barcodes.

Features:
• Real-time validation
• Missing digit solver
• Barcode generator
• Webcam scanner
• Batch processing
• History tracking
• Export to CSV/PDF
• Dark/Light mode

Developed in Python with Tkinter
        """
        
        messagebox.showinfo("About UPC Validator", about_text.strip())
    
    def exit_app(self):
        """Exit the application."""
        if self.scanner:
            self.scanner.stop()
        
        result = messagebox.askyesno("Exit", "Are you sure you want to exit?")
        if result:
            self.root.quit()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = UPCValidatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()