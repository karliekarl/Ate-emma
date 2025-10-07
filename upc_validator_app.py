#!/usr/bin/env python3
"""
UPC Validator: A Real-Time System for Validating and Decoding Product Barcodes

Pure Python Tkinter application (no external frameworks).
Works on Windows (and cross-platform) using the standard library only.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Tuple


class UPCValidatorApp:
    """Tkinter GUI application for real-time UPC-A validation and decoding."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("UPC Validator: Real-Time Barcode Checker")
        self.root.resizable(False, False)

        # Theme colors
        self.colors = {
            "bg": "#f3f4f6",          # Light gray window background
            "panel": "#eef2f7",       # Slightly darker frame background
            "title": "#1d4ed8",       # Blue title text
            "text": "#111827",        # Primary text (near-black)
            "muted": "#4b5563",       # Muted label text (gray)
            "input_bg": "#ffffff",    # White input
            "valid": "#16a34a",       # Green
            "invalid": "#dc2626",     # Red
            "button_bg": "#e5e7eb",   # Light gray button
            "button_fg": "#111827",
        }

        self.root.configure(bg=self.colors["bg"])

        # Top-level variables bound to UI
        self.upc_var = tk.StringVar()
        self.status_var = tk.StringVar(value="")
        self.product_type_digit_var = tk.StringVar(value="—")
        self.product_type_meaning_var = tk.StringVar(value="—")
        self.manufacturer_code_var = tk.StringVar(value="—")
        self.product_code_var = tk.StringVar(value="—")
        self.check_digit_var = tk.StringVar(value="—")

        # Build UI
        self._build_ui()

        # Real-time updates on change
        self.upc_var.trace_add("write", lambda *_: self._on_upc_change())

        # Center window after layout is computed
        self.root.after(0, self._center_window)

    # -----------------------------
    # UI Construction
    # -----------------------------
    def _build_ui(self) -> None:
        # Title
        title = tk.Label(
            self.root,
            text="UPC Validator: Real-Time Barcode Checker",
            font=("Segoe UI", 16, "bold"),
            fg=self.colors["title"],
            bg=self.colors["bg"],
            pady=10,
        )
        title.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        # Input panel
        input_frame = tk.Frame(self.root, bg=self.colors["panel"], bd=0, highlightthickness=0)
        input_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=8)
        for i in range(4):
            input_frame.grid_columnconfigure(i, weight=1)

        input_label = tk.Label(
            input_frame,
            text="Enter 12-digit UPC:",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["text"],
            bg=self.colors["panel"],
            anchor="w",
        )
        input_label.grid(row=0, column=0, padx=12, pady=(12, 4), sticky="w")

        # Entry with validation (only digits, max length 12)
        vcmd = (self.root.register(self._validate_entry_on_key), "%P")
        self.upc_entry = tk.Entry(
            input_frame,
            textvariable=self.upc_var,
            font=("Segoe UI", 12),
            bg=self.colors["input_bg"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="solid",
            bd=1,
            width=24,
            validate="key",
            validatecommand=vcmd,
        )
        self.upc_entry.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew", columnspan=2)
        self.upc_entry.bind("<Return>", self._on_validate_click)
        self.upc_entry.focus_set()

        # Buttons
        btn_validate = tk.Button(
            input_frame,
            text="Validate",
            command=self._on_validate_click,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief="raised",
            bd=1,
            padx=10,
            pady=4,
        )
        btn_validate.grid(row=1, column=2, padx=(4, 4), pady=(0, 12), sticky="e")

        btn_clear = tk.Button(
            input_frame,
            text="Clear",
            command=self._on_clear_click,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief="raised",
            bd=1,
            padx=10,
            pady=4,
        )
        btn_clear.grid(row=1, column=3, padx=(4, 4), pady=(0, 12), sticky="e")

        btn_exit = tk.Button(
            input_frame,
            text="Exit",
            command=self.root.destroy,
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            relief="raised",
            bd=1,
            padx=10,
            pady=4,
        )
        btn_exit.grid(row=1, column=4, padx=(4, 12), pady=(0, 12), sticky="e")

        # Status
        status_frame = tk.Frame(self.root, bg=self.colors["bg"])  # transparent frame for spacing
        status_frame.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 4))

        status_label_prefix = tk.Label(
            status_frame,
            text="Status:",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"],
        )
        status_label_prefix.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 12, "bold"),
            fg=self.colors["invalid"],
            bg=self.colors["bg"],
        )
        self.status_label.grid(row=0, column=1, sticky="w")

        # Breakdown panel
        breakdown = tk.LabelFrame(
            self.root,
            text="Breakdown",
            font=("Segoe UI", 10, "bold"),
            fg=self.colors["muted"],
            bg=self.colors["panel"],
            bd=1,
            relief="groove",
            labelanchor="nw",
            padx=12,
            pady=8,
        )
        breakdown.grid(row=3, column=0, sticky="ew", padx=16, pady=(4, 16))
        for i in range(2):
            breakdown.grid_columnconfigure(i, weight=1)

        # Product type digit
        tk.Label(
            breakdown, text="Product Type (Digit):", font=("Segoe UI", 10), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=0, column=0, sticky="w", pady=2)
        tk.Label(
            breakdown, textvariable=self.product_type_digit_var, font=("Segoe UI", 10, "bold"), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=0, column=1, sticky="w", pady=2)

        # Product type meaning
        tk.Label(
            breakdown, text="Product Type Meaning:", font=("Segoe UI", 10), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=1, column=0, sticky="w", pady=2)
        tk.Label(
            breakdown, textvariable=self.product_type_meaning_var, font=("Segoe UI", 10), fg=self.colors["muted"], bg=self.colors["panel"]
        ).grid(row=1, column=1, sticky="w", pady=2)

        # Manufacturer code (digits 2–6)
        tk.Label(
            breakdown, text="Manufacturer Code (2–6):", font=("Segoe UI", 10), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=2, column=0, sticky="w", pady=2)
        tk.Label(
            breakdown, textvariable=self.manufacturer_code_var, font=("Segoe UI", 10, "bold"), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=2, column=1, sticky="w", pady=2)

        # Product code (digits 7–11)
        tk.Label(
            breakdown, text="Product Code (7–11):", font=("Segoe UI", 10), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=3, column=0, sticky="w", pady=2)
        tk.Label(
            breakdown, textvariable=self.product_code_var, font=("Segoe UI", 10, "bold"), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=3, column=1, sticky="w", pady=2)

        # Check digit (digit 12)
        tk.Label(
            breakdown, text="Check Digit (12):", font=("Segoe UI", 10), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=4, column=0, sticky="w", pady=2)
        tk.Label(
            breakdown, textvariable=self.check_digit_var, font=("Segoe UI", 10, "bold"), fg=self.colors["text"], bg=self.colors["panel"]
        ).grid(row=4, column=1, sticky="w", pady=2)

    # -----------------------------
    # Event Handlers
    # -----------------------------
    def _on_upc_change(self) -> None:
        """Handle real-time updates when the UPC input changes."""
        upc = self.upc_var.get()
        self._update_breakdown(upc)
        self._update_status(upc)

    def _on_validate_click(self, *_evt) -> None:
        """Handle Validate button or Enter key: confirm validation status."""
        upc = self.upc_var.get()
        # If incomplete, give a gentle nudge
        if not upc.isdigit() or len(upc) != 12:
            self.status_var.set("INVALID")
            self.status_label.config(fg=self.colors["invalid"]) 
            messagebox.showinfo(
                "Validation",
                "Please enter exactly 12 numeric digits to validate the UPC.",
            )
            return

        is_valid = self._is_valid_upc(upc)
        self.status_var.set("VALID" if is_valid else "INVALID")
        self.status_label.config(fg=self.colors["valid"] if is_valid else self.colors["invalid"]) 

    def _on_clear_click(self) -> None:
        """Clear the input and reset UI."""
        self.upc_var.set("")
        self.status_var.set("")
        self.status_label.config(fg=self.colors["invalid"])  # will be hidden when empty
        self._update_breakdown("")
        self.upc_entry.focus_set()

    # -----------------------------
    # Validation and Decoding Logic
    # -----------------------------
    def _validate_entry_on_key(self, proposed_value: str) -> bool:
        """Return True to accept the edit; restrict to digits and max length 12.

        This is used by the Entry's validatecommand to enforce constraints as the
        user types or pastes text.
        """
        if proposed_value == "":
            return True
        if not proposed_value.isdigit():
            return False
        return len(proposed_value) <= 12

    def _update_breakdown(self, upc: str) -> None:
        """Update the breakdown fields based on the current input."""
        # Product type digit (first digit)
        if len(upc) >= 1 and upc[0].isdigit():
            first_digit = upc[0]
            self.product_type_digit_var.set(first_digit)
            self.product_type_meaning_var.set(self._product_type_meaning(first_digit))
        else:
            self.product_type_digit_var.set("—")
            self.product_type_meaning_var.set("—")

        # Manufacturer code (digits 2–6)
        if len(upc) >= 6 and upc[1:6].isdigit():
            self.manufacturer_code_var.set(upc[1:6])
        else:
            self.manufacturer_code_var.set("—")

        # Product code (digits 7–11)
        if len(upc) >= 11 and upc[6:11].isdigit():
            self.product_code_var.set(upc[6:11])
        else:
            self.product_code_var.set("—")

        # Check digit (digit 12)
        if len(upc) == 12 and upc[-1].isdigit():
            self.check_digit_var.set(upc[-1])
        else:
            self.check_digit_var.set("—")

    def _update_status(self, upc: str) -> None:
        """Update the VALID/INVALID status label in real-time."""
        if len(upc) == 0:
            self.status_var.set("")
            return

        if not upc.isdigit() or len(upc) != 12:
            self.status_var.set("INVALID")
            self.status_label.config(fg=self.colors["invalid"]) 
            return

        is_valid = self._is_valid_upc(upc)
        self.status_var.set("VALID" if is_valid else "INVALID")
        self.status_label.config(fg=self.colors["valid"] if is_valid else self.colors["invalid"]) 

    def _is_valid_upc(self, upc: str) -> bool:
        """Return True if a 12-digit UPC-A code passes the check digit rule.

        Rule: 3a1 + a2 + 3a3 + a4 + 3a5 + a6 + 3a7 + a8 + 3a9 + a10 + 3a11 + a12 ≡ 0 (mod 10)
        Equivalently, expected check digit is (10 - (sum % 10)) % 10 where sum includes
        weighted digits a1..a11.
        """
        if len(upc) != 12 or not upc.isdigit():
            return False
        digits = [int(ch) for ch in upc]
        body = digits[:11]
        check = digits[11]
        expected = self._compute_expected_check_digit(body)
        return check == expected

    def _compute_expected_check_digit(self, first_eleven: list) -> int:
        """Compute expected UPC-A check digit from the first 11 digits.

        Weights: 3 on odd positions (1-based), 1 on even positions.
        """
        total = 0
        for index, value in enumerate(first_eleven, start=1):
            weight = 3 if index % 2 == 1 else 1
            total += weight * value
        expected_check = (10 - (total % 10)) % 10
        return expected_check

    def _product_type_meaning(self, first_digit: str) -> str:
        """Return the human-readable meaning for the product type digit."""
        mapping = {
            "0": "General groceries",
            "2": "Meat and produce",
            "3": "Drugs and health products",
            "4": "Non-food items",
            "5": "Coupons",
            "6": "Other items",
            "7": "Other items",
            "1": "Reserved for future use",
            "8": "Reserved for future use",
            "9": "Reserved for future use",
        }
        return mapping.get(first_digit, "Unknown")

    # -----------------------------
    # Window Utilities
    # -----------------------------
    def _center_window(self) -> None:
        """Center the window on the current screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 3)
        self.root.geometry(f"{width}x{height}+{x}+{y}")


def main() -> None:
    root = tk.Tk()
    app = UPCValidatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
