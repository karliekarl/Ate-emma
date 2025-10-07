#!/usr/bin/env python3
"""
UPC Validator: A Real-Time System for Validating and Decoding Product Barcodes

Pure Python + Tkinter desktop application.

Features:
- Real-time UPC-A validation and decoding
- Input field for 12-digit UPC code
- Validate button, Clear button, Exit button
- Check digit calculation and verification using the UPC formula
- Breakdown display: product type, manufacturer code, product code, check digit
- Product type meaning mapping
- Real-time feedback with color cues (green for valid, red for invalid)
- Simple, clean Tkinter layout with labels and frames
- Centered window, themed colors

This file is self-contained and requires only the Python standard library.
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional, Tuple

# -----------------------------
# Theme and styling constants
# -----------------------------
APP_TITLE = "UPC Validator: Real-Time Barcode Checker"
BACKGROUND_COLOR = "#f0f2f5"  # light gray
TITLE_TEXT_COLOR = "#1f5fbf"   # blue
INPUT_BACKGROUND = "#ffffff"   # white
TEXT_COLOR = "#222222"
VALID_COLOR = "#2e7d32"        # green
INVALID_COLOR = "#c62828"      # red
NEUTRAL_COLOR = "#333333"
BORDER_COLOR = "#d0d7de"

# -----------------------------
# UPC logic helpers
# -----------------------------
PRODUCT_TYPE_MAP = {
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


def calculate_expected_check_digit(upc_first_11: str) -> int:
    """Calculate the expected UPC check digit from the first 11 digits.

    Uses the standard UPC-A check digit algorithm:
    (3a1 + a2 + 3a3 + a4 + 3a5 + a6 + 3a7 + a8 + 3a9 + a10 + 3a11 + a12) ≡ 0 (mod 10)

    The check digit a12 is chosen so that the total sum is a multiple of 10.
    """
    if len(upc_first_11) != 11 or not upc_first_11.isdigit():
        raise ValueError("Input to calculate_expected_check_digit must be 11 digits.")

    digits = [int(ch) for ch in upc_first_11]

    # Sum of digits in odd positions (1-based indexing): positions 1,3,5,7,9,11
    sum_odd_positions = digits[0] + digits[2] + digits[4] + digits[6] + digits[8] + digits[10]
    # Sum of digits in even positions (1-based indexing): positions 2,4,6,8,10
    sum_even_positions = digits[1] + digits[3] + digits[5] + digits[7] + digits[9]

    total = (sum_odd_positions * 3) + sum_even_positions
    expected_check_digit = (10 - (total % 10)) % 10
    return expected_check_digit


def validate_upc(upc_code: str) -> Tuple[bool, Optional[int]]:
    """Validate a 12-digit UPC-A code and return (is_valid, expected_check_digit).

    - If the input is not exactly 12 digits, returns (False, None) or (False, expected)
      when 11 leading digits are present.
    - If 12 digits are present, compares the actual check digit against the expected one.
    """
    if not upc_code.isdigit():
        # Not all digits; if we can, still compute a candidate expected check digit
        if len(upc_code) >= 11 and upc_code[:11].isdigit():
            return False, calculate_expected_check_digit(upc_code[:11])
        return False, None

    if len(upc_code) == 12:
        expected = calculate_expected_check_digit(upc_code[:11])
        actual = int(upc_code[11])
        return actual == expected, expected

    if len(upc_code) >= 11:
        # Not 12 digits yet, but we can compute the expected from first 11
        return False, calculate_expected_check_digit(upc_code[:11])

    return False, None


def product_type_meaning(first_digit: str) -> str:
    """Map the first digit to a human-readable product type meaning."""
    if not first_digit or not first_digit.isdigit():
        return "—"
    return PRODUCT_TYPE_MAP.get(first_digit, "Unknown")


# -----------------------------
# Tkinter Application
# -----------------------------
class UPCValidatorApp(tk.Tk):
    """Tkinter GUI application for real-time UPC validation and decoding."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.configure(bg=BACKGROUND_COLOR)

        # Fonts (Windows-friendly defaults)
        self.font_title = ("Segoe UI", 16, "bold")
        self.font_label = ("Segoe UI", 10)
        self.font_value = ("Consolas", 12)
        self.font_status = ("Segoe UI", 12, "bold")

        # Tk variables
        self.upc_var = tk.StringVar(value="")

        # Build UI
        self._build_layout()
        self._bind_shortcuts()

        # Real-time updates when the UPC changes
        self.upc_var.trace_add("write", self._on_upc_change)

        # Size and center after layout is computed
        self.after(50, self._center_window)

    # ---------- UI construction ----------
    def _build_layout(self) -> None:
        # Title
        title_label = tk.Label(
            self,
            text=APP_TITLE,
            font=self.font_title,
            fg=TITLE_TEXT_COLOR,
            bg=BACKGROUND_COLOR,
            padx=10,
            pady=10,
        )
        title_label.pack(anchor="center")

        # Content frame (for padding and consistent background)
        content = tk.Frame(self, bg=BACKGROUND_COLOR, padx=16, pady=12)
        content.pack(fill="both", expand=True)

        # Input frame
        input_frame = tk.LabelFrame(
            content,
            text="Input",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=self.font_label,
            padx=12,
            pady=10,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            bd=0,
        )
        input_frame.pack(fill="x", pady=(0, 10))

        input_label = tk.Label(
            input_frame,
            text="Enter 12-digit UPC:",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=self.font_label,
        )
        input_label.grid(row=0, column=0, sticky="w", padx=(0, 8))

        # Validation: only digits, max length 12
        vcmd = (self.register(self._validate_entry), "%P")
        self.upc_entry = tk.Entry(
            input_frame,
            textvariable=self.upc_var,
            width=20,
            bg=INPUT_BACKGROUND,
            fg=TEXT_COLOR,
            font=self.font_value,
            relief="solid",
            bd=1,
            validate="key",
            validatecommand=vcmd,
            insertbackground=TEXT_COLOR,
        )
        self.upc_entry.grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.upc_entry.focus_set()

        self.validate_button = tk.Button(
            input_frame,
            text="Validate",
            command=self._on_validate_clicked,
            width=12,
        )
        self.validate_button.grid(row=0, column=2, sticky="w")

        # Status frame
        status_frame = tk.LabelFrame(
            content,
            text="Status",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=self.font_label,
            padx=12,
            pady=10,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            bd=0,
        )
        status_frame.pack(fill="x", pady=(0, 10))

        status_label = tk.Label(
            status_frame,
            text="Validation:",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=self.font_label,
        )
        status_label.grid(row=0, column=0, sticky="w")

        self.status_value = tk.Label(
            status_frame,
            text="—",
            bg=BACKGROUND_COLOR,
            fg=NEUTRAL_COLOR,
            font=self.font_status,
        )
        self.status_value.grid(row=0, column=1, sticky="w", padx=(8, 0))

        expected_label = tk.Label(
            status_frame,
            text="Expected check digit:",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=self.font_label,
        )
        expected_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.expected_check_digit_value = tk.Label(
            status_frame,
            text="—",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=self.font_value,
        )
        self.expected_check_digit_value.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        # Breakdown frame
        breakdown = tk.LabelFrame(
            content,
            text="Breakdown",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=self.font_label,
            padx=12,
            pady=10,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            bd=0,
        )
        breakdown.pack(fill="x", pady=(0, 10))

        # Product type
        pt_label = tk.Label(breakdown, text="Product type (digit 1):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_label)
        pt_label.grid(row=0, column=0, sticky="w")

        self.product_type_digit_value = tk.Label(breakdown, text="-", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_value)
        self.product_type_digit_value.grid(row=0, column=1, sticky="w", padx=(8, 20))

        self.product_type_desc_value = tk.Label(breakdown, text="—", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_label)
        self.product_type_desc_value.grid(row=0, column=2, sticky="w")

        # Manufacturer code
        man_label = tk.Label(breakdown, text="Manufacturer code (digits 2–6):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_label)
        man_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.manufacturer_value = tk.Label(breakdown, text="-", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_value)
        self.manufacturer_value.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        # Product code
        prod_label = tk.Label(breakdown, text="Product code (digits 7–11):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_label)
        prod_label.grid(row=2, column=0, sticky="w", pady=(6, 0))

        self.product_value = tk.Label(breakdown, text="-", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_value)
        self.product_value.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        # Check digit (digit 12)
        check_label = tk.Label(breakdown, text="Check digit (digit 12):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_label)
        check_label.grid(row=3, column=0, sticky="w", pady=(6, 0))

        self.check_digit_value = tk.Label(breakdown, text="-", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=self.font_value)
        self.check_digit_value.grid(row=3, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        # Buttons frame
        buttons = tk.Frame(content, bg=BACKGROUND_COLOR)
        buttons.pack(fill="x")

        self.clear_button = tk.Button(buttons, text="Clear", command=self._on_clear_clicked, width=12, state="disabled")
        self.clear_button.pack(side="left")

        exit_button = tk.Button(buttons, text="Exit", command=self.destroy, width=12)
        exit_button.pack(side="right")

        # Configure resizing weights for nicer layout
        for container in (input_frame, status_frame, breakdown):
            container.grid_columnconfigure(0, weight=0)
            container.grid_columnconfigure(1, weight=1)
            container.grid_columnconfigure(2, weight=1)

        # Initialize state
        self._update_breakdown()
        self._update_status()

    def _bind_shortcuts(self) -> None:
        # Enter to validate, Esc to exit, Ctrl+L to clear
        self.bind("<Return>", lambda e: self._on_validate_clicked())
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Control-l>", lambda e: self._on_clear_clicked())

    # ---------- Event handlers and helpers ----------
    def _validate_entry(self, proposed: str) -> bool:
        """Allow only digits and length up to 12."""
        if proposed == "":
            return True
        if not proposed.isdigit():
            return False
        return len(proposed) <= 12

    def _on_upc_change(self, *args) -> None:
        self._update_breakdown()
        self._update_status()

    def _on_validate_clicked(self) -> None:
        # Explicit validation action (real-time already validates as user types)
        self._update_status(explicit=True)

    def _on_clear_clicked(self) -> None:
        self.upc_var.set("")
        self.upc_entry.focus_set()

    def _update_breakdown(self) -> None:
        upc = self.upc_var.get()

        first_digit = upc[0] if len(upc) >= 1 else "-"
        manufacturer = upc[1:6] if len(upc) >= 6 else "-"
        product = upc[6:11] if len(upc) >= 11 else "-"
        check_digit = upc[11] if len(upc) >= 12 else "-"

        self.product_type_digit_value.config(text=first_digit)
        self.product_type_desc_value.config(text=product_type_meaning(first_digit) if first_digit != "-" else "—")
        self.manufacturer_value.config(text=manufacturer)
        self.product_value.config(text=product)
        self.check_digit_value.config(text=check_digit)

    def _update_status(self, explicit: bool = False) -> None:
        upc = self.upc_var.get()

        # Expected check digit display
        if len(upc) >= 11 and upc[:11].isdigit():
            expected = calculate_expected_check_digit(upc[:11])
            self.expected_check_digit_value.config(text=str(expected))
        else:
            self.expected_check_digit_value.config(text="—")

        # Compute validation state
        if len(upc) == 12 and upc.isdigit():
            is_valid, expected = validate_upc(upc)
            if is_valid:
                self.status_value.config(text="VALID", fg=VALID_COLOR)
            else:
                self.status_value.config(text="INVALID", fg=INVALID_COLOR)
        elif upc == "":
            self.status_value.config(text="—", fg=NEUTRAL_COLOR)
        else:
            # Partial input
            self.status_value.config(text="Awaiting 12 digits", fg=NEUTRAL_COLOR)

        # Enable/disable buttons based on state
        self.validate_button.config(state=("normal" if len(upc) == 12 and upc.isdigit() else "disabled"))
        self.clear_button.config(state=("normal" if len(upc) > 0 else "disabled"))

    def _center_window(self) -> None:
        """Center the window on screen after it has been drawn."""
        self.update_idletasks()
        # Provide a sensible minimum size for aesthetics
        min_width, min_height = 600, 420
        current_width = max(self.winfo_width(), min_width)
        current_height = max(self.winfo_height(), min_height)
        x = (self.winfo_screenwidth() - current_width) // 2
        y = (self.winfo_screenheight() - current_height) // 2
        self.geometry(f"{current_width}x{current_height}+{x}+{y}")


def main() -> None:
    app = UPCValidatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
