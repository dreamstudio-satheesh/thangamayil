# Workflow Schema - தங்கமயில் சில்க்ஸ் Billing Software

## System Workflow Overview

This document outlines the operational workflows and process flows for the offline billing software.

## 1. Application Startup Workflow

```
Start Application
    ↓
Display Login Screen
    ↓
Enter Staff Name & Password
    ↓
Validate Credentials
    ├── Success → Continue
    └── Failure → Show Error & Retry
    ↓
Initialize Database Connection
    ↓
Load Master Data (Items, Customers, Staff)
    ↓
Initialize Hardware (Barcode Scanner, Printer)
    ↓
Display Main Dashboard (with logged-in staff name)
```

## 2. Master Data Management Workflows

### 2.1 Items Master Workflow

```
Items Management
    ├── Add New Item
    │   ├── Enter Item Details (Name, Category, Price, GST%)
    │   ├── Generate/Assign Barcode
    │   ├── Set Initial Stock Quantity
    │   └── Save to Database
    │
    ├── Edit Existing Item
    │   ├── Search Item (by Barcode/Name)
    │   ├── Modify Details
    │   └── Update Database
    │
    └── Delete Item
        ├── Search Item
        ├── Check for Active Transactions
        └── Soft Delete (Mark Inactive)
```

### 2.2 Customer Master Workflow

```
Customer Management
    ├── Add Customer
    │   ├── Enter Name & Phone
    │   ├── Generate Customer ID
    │   └── Save to Database
    │
    └── Edit Customer
        ├── Search by Phone/Name
        ├── Update Details
        └── Save Changes
```

### 2.3 Staff Management Workflow

```
Staff Management
    ├── Add New Staff
    │   ├── Enter Staff Name (Display Name)
    │   ├── Set Password (Hashed Storage)
    │   ├── Set Active Status
    │   └── Save to Database
    │
    ├── Edit Staff Details
    │   ├── Select Staff from List
    │   ├── Update Name/Status
    │   ├── Change Password (Optional)
    │   └── Save Changes
    │
    └── Deactivate Staff
        ├── Select Staff
        ├── Mark as Inactive (Soft Delete)
        └── Retain Historical Data
```

## 3. Authentication & Session Management

### 3.1 Login Process

```
Login Workflow
    ↓
Display Login Form (Staff Name + Password)
    ↓
User Enters Credentials
    ↓
Validate Against Staff Database
    ├── Hash Password & Compare
    ├── Check Active Status
    └── Authenticate User
    ↓
Success:
    ├── Create Session
    ├── Store Staff ID & Name
    └── Proceed to Main Dashboard
    ↓
Failure:
    ├── Show Error Message
    ├── Clear Password Field
    └── Return to Login
```

### 3.2 Session Management

```
Session Handling
    ├── Store Current Staff Info
    │   ├── Staff ID
    │   ├── Staff Name (for display)
    │   └── Login Timestamp
    │
    ├── Bill Association
    │   ├── Associate each bill with Staff ID
    │   ├── Display staff name on invoices
    │   └── Track staff performance
    │
    └── Logout Process
        ├── Clear Session Data
        ├── Return to Login Screen
        └── Optional: Auto-logout after inactivity
```

## 4. Billing (POS) Workflow

### 4.1 Main Billing Process

```
Start New Bill (with logged-in staff session)
    ↓
Generate Invoice Number
    ↓
Associate Bill with Staff ID
    ↓
┌─────────────────────────┐
│     Add Items Loop      │
│                         │
│  Scan Barcode           │
│      OR                 │
│  Manual Item Search     │
│      ↓                  │
│  Validate Item          │
│      ↓                  │
│  Enter/Edit Quantity    │
│      ↓                  │
│  Apply Item Discount    │
│      ↓                  │
│  Calculate GST          │
│      ↓                  │
│  Add to Bill            │
│      ↓                  │
│  Update Stock           │
└─────────────────────────┘
    ↓
Review Bill Items
    ↓
Apply Bill-Level Discount (if any)
    ↓
Calculate Final Totals
    ├── Subtotal
    ├── Total Discount
    ├── CGST/SGST Amounts
    ├── Round Off
    └── Grand Total
    ↓
Select Payment Mode
    ↓
Generate & Print Invoice (with Staff Name)
    ↓
Save Transaction to Database (with Staff ID & Timestamp)
    ↓
End Bill / Start New Bill
```

### 3.2 Item Addition Sub-workflow

```
Item Entry
    ├── Barcode Scan
    │   ├── Auto-populate Item Details
    │   ├── Default Quantity = 1
    │   └── Calculate Line Total
    │
    ├── Manual Search
    │   ├── Search by Name/Code
    │   ├── Select from Results
    │   ├── Enter Quantity
    │   └── Calculate Line Total
    │
    └── Item Not Found
        ├── Add New Item Option
        │   ├── Quick Add Form
        │   └── Continue with Billing
        └── Skip Item Option
```

## 4. GST Calculation Workflow

```
GST Calculation Process
    ↓
For Each Item:
    ├── Item Price × Quantity = Line Amount
    ├── Apply Item Discount = Discounted Amount
    ├── Calculate Taxable Value
    ├── Apply GST Rate
    │   ├── If Intra-State: CGST + SGST
    │   └── If Inter-State: IGST
    └── Line Total = Taxable Value + GST Amount
    ↓
Bill Level:
    ├── Sum All Taxable Values = Subtotal
    ├── Sum All GST Amounts = Total GST
    ├── Apply Bill Discount (on Subtotal)
    ├── Recalculate GST on Discounted Amount
    ├── Apply Round Off (±0.50)
    └── Grand Total
```

## 5. Report Generation Workflows

### 5.1 Daily Sales Report

```
Daily Sales Report
    ↓
Select Date Range
    ↓
Optional: Select Staff Filter
    ↓
Query Transactions
    ├── Filter by Date (and Staff if selected)
    ├── Group by Bill Number
    └── Calculate Totals
    ↓
Generate Report
    ├── Total Sales Amount
    ├── Total GST Collected
    ├── Number of Bills
    ├── Payment Mode Breakdown
    ├── Staff-wise Sales Summary
    └── Item-wise Sales Summary
    ↓
Display/Print/Export Report
```

### 5.2 Stock Report

```
Stock Report
    ↓
Query Current Stock Levels
    ├── Item-wise Current Stock
    ├── Stock Value Calculation
    └── Low Stock Alerts
    ↓
Generate Report
    ├── Items with Stock
    ├── Out of Stock Items
    ├── Low Stock Items (<threshold)
    └── Total Stock Value
    ↓
Display/Export Report
```

### 5.3 Staff Performance Report

```
Staff Performance Report
    ↓
Select Date Range
    ↓
Query Staff Transaction Data
    ├── Group by Staff ID
    ├── Calculate Staff Totals
    └── Include Transaction Counts
    ↓
Generate Report
    ├── Staff Name & ID
    ├── Total Sales Amount
    ├── Number of Bills Handled
    ├── Average Bill Value
    ├── Performance Ranking
    └── Time-wise Activity
    ↓
Display/Export Report
```

## 6. Backup & Restore Workflow

### 6.1 Database Backup

```
Backup Process
    ↓
Select Backup Location
    ↓
Generate Backup Filename (with timestamp)
    ↓
Copy Database File
    ↓
Verify Backup Integrity
    ↓
Show Success Message
```

### 6.2 Database Restore

```
Restore Process
    ↓
Select Backup File
    ↓
Validate Backup File
    ↓
Create Current Database Backup
    ↓
Replace Current Database
    ↓
Restart Application
    ↓
Verify Data Integrity
```

## 7. Error Handling Workflows

### 7.1 Hardware Error Handling

```
Hardware Error Detection
    ├── Barcode Scanner Not Responding
    │   ├── Show Manual Entry Option
    │   └── Display Scanner Troubleshooting
    │
    ├── Printer Not Available
    │   ├── Save Bill to Reprint Queue
    │   ├── Show Manual Print Option
    │   └── Continue with Next Bill
    │
    └── Database Connection Lost
        ├── Attempt Reconnection
        ├── Save Pending Data to Temp File
        └── Show Recovery Options
```

### 7.2 Data Validation Workflows

```
Data Validation
    ├── Item Validation
    │   ├── Check Barcode Uniqueness
    │   ├── Validate Price > 0
    │   └── Validate GST Rate (0-28%)
    │
    ├── Bill Validation
    │   ├── Minimum 1 Item Required
    │   ├── Quantities > 0
    │   └── Valid Payment Mode
    │
    └── Stock Validation
        ├── Check Available Stock
        ├── Warn on Low Stock
        └── Prevent Negative Stock
```

## 8. System States

### Application States
- **IDLE**: Ready for new transaction
- **BILLING**: Active billing session
- **PAYMENT**: Payment processing
- **PRINTING**: Invoice generation
- **REPORTS**: Report generation mode
- **MAINTENANCE**: Master data management

### Transaction States
- **DRAFT**: Bill being created
- **COMPLETED**: Bill finalized and saved
- **PRINTED**: Invoice printed
- **CANCELLED**: Bill cancelled/voided

## 9. User Interface Flow

```
Main Dashboard
    ├── New Bill → POS Interface
    ├── Items Master → Item Management
    ├── Reports → Report Selection
    ├── Settings → Configuration
    └── Exit → Close Application

POS Interface
    ├── Item Entry Panel
    ├── Bill Preview Panel
    ├── Payment Panel
    └── Action Buttons (Save/Print/Cancel)
```

This workflow schema provides a comprehensive view of all operational processes in the billing software system.