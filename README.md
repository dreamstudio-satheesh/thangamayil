# Software Requirements Specification (SRS)

## Project Title

**தங்கமயில் சில்க்ஸ் – Offline Billing Software**

## 1. Introduction

* Purpose: To develop a lightweight offline billing software tailored for silk shops.
* Technology: **Python (Tkinter/PyQt)** for UI and **SQLite** for database.
* Scope: Enable barcode-based billing, GST calculation, discounts, and daily sales reports.
* User: Cashiers/Shop staff.

## 2. Functional Requirements

### 2.1 Master Data Management

* **Items Master**

  * Fields: Barcode, Item Name, Category, Price, GST%, Stock Quantity.
  * Add/Edit/Delete items.
* **Customer Master (Optional)**

  * Fields: Customer Name, Phone Number.

### 2.2 Billing (POS)

* Scan item via barcode (auto entry).
* Manual search & entry (if barcode not available).
* Edit quantity, apply discount (flat/percentage).
* Auto GST calculation (CGST + SGST).
* Generate bill (with unique invoice number).
* Print bill (thermal printer support).

### 2.3 Reports

* Daily sales report.
* GST summary report.
* Item-wise sales report.
* Stock report (current stock levels).

### 2.4 Discounts & Offers

* Per-item discount.
* Bill-level discount.

### 2.5 Backup/Restore

* Local database backup option.
* Export reports as CSV/Excel.

## 3. Non-Functional Requirements

* **Performance**: Billing entry should be completed in < 2 seconds per item.
* **Reliability**: Should work offline without internet.
* **Usability**: Simple interface, touch-friendly buttons.
* **Portability**: Single executable file for Windows systems.

## 4. Hardware/Software Requirements

* **Hardware**: Windows PC, Barcode Scanner, Thermal Printer.
* **Software**:

  * Python 3.x
  * Tkinter/PyQt
  * SQLite

## 5. Future Enhancements

* Multi-user login with roles.
* Cloud sync for multi-branch usage.
* Mobile app integration.
* Loyalty program for customers.

---

**Prepared for: தங்கமயில் சில்க்ஸ்**
Licensed to: Satheesh (Dream Studio)