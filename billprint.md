
**recommended GST bill format structure**:

---

## **தங்கமயில் சில்க்ஸ் – GST Invoice Format**

### **Header Section**

- Shop Name & Logo (தங்கமயில் சில்க்ஸ்)
    
- Address & Phone
    
- GSTIN, CIN (if applicable)
    
- Invoice Type: **CASH BILL / TAX INVOICE**
    
- Bill No, Date, Time
    
- Place of Supply
    
- Cashier Name (optional)
    

---

### **Item Table**

|SN|Product Code / Barcode|Item Name|Qty|Price|Disc%|GST%|GST Amt|Total|
|---|---|---|---|---|---|---|---|---|

👉 Example row:  
1 | 5407 | Silk Saree | 1 | 2000.00 | 5% | 5% | 95.24 | 2000.00

---

### **Summary Section**

- **Subtotal**: ₹ xxxx.xx
    
- **Discount**: ₹ xxxx.xx
    
- **CGST @ x%**: ₹ xxxx.xx
    
- **SGST @ x%**: ₹ xxxx.xx
    
- **IGST @ x% (if interstate)**: ₹ xxxx.xx
    
- **Round Off**: ± ₹ 0.xx
    
- **TOTAL**: ₹ xxxx.xx
    

---

### **Footer Section**

- Mode of Payment: Cash / Card / UPI
    
- Parcel No (if needed)
    
- Terms: _No Exchange / Delivery Slip_
    
- Thank You Message
    
- Website / Online Shop Link (optional)


```
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_invoice(bill_no, items, customer_name="Walk-in"):
    """
    bill_no : str
    items   : list of dicts → [{"name":"Silk Saree","code":"5407","qty":1,"price":2000,"disc":0,"gst":5}]
    """

    file_name = f"invoice_{bill_no}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height-50, "தங்கமயில் சில்க்ஸ்")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height-65, "No.1 Main Road, Tamil Nadu, IN")
    c.drawCentredString(width/2, height-80, "Phone: +91-9876543210 | GSTIN: 33AAACT9454F1ZB")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, height-110, f"Invoice No: {bill_no}")
    c.drawString(350, height-110, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}")

    # Table Headers
    c.setFont("Helvetica-Bold", 10)
    headers = ["SN", "Code", "Item", "Qty", "Price", "Disc%", "GST%", "GST Amt", "Total"]
    x_positions = [30, 70, 120, 280, 320, 370, 420, 470, 520]
    for i, h in enumerate(headers):
        c.drawString(x_positions[i], height-140, h)

    # Table Content
    c.setFont("Helvetica", 10)
    y = height-160
    sn = 1
    subtotal, total_gst, grand_total = 0, 0, 0

    for item in items:
        price = item["price"] * item["qty"]
        discount_amt = (price * item["disc"]) / 100
        taxable = price - discount_amt
        gst_amt = (taxable * item["gst"]) / 100
        total = taxable + gst_amt

        subtotal += taxable
        total_gst += gst_amt
        grand_total += total

        row = [str(sn), item["code"], item["name"], str(item["qty"]),
               f"{item['price']:.2f}", f"{item['disc']}%", f"{item['gst']}%",
               f"{gst_amt:.2f}", f"{total:.2f}"]

        for i, val in enumerate(row):
            c.drawString(x_positions[i], y, val)

        y -= 20
        sn += 1

    # Summary
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(400, y, f"Subtotal: {subtotal:.2f}")
    y -= 15
    c.drawString(400, y, f"GST Total: {total_gst:.2f}")
    y -= 15
    c.drawString(400, y, f"Grand Total: {grand_total:.2f}")

    # Footer
    y -= 40
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, y, "Thank you for shopping with தங்கமயில் சில்க்ஸ்")
    y -= 15
    c.drawCentredString(width/2, y, "No Exchange | No Refund")

    c.save()
    print(f"Invoice saved: {file_name}")


# Example usage
items = [
    {"name":"Silk Saree", "code":"5407", "qty":1, "price":2000, "disc":0, "gst":5},
    {"name":"Cotton Saree", "code":"5410", "qty":2, "price":800, "disc":5, "gst":5},
]

generate_invoice("INV-1001", items)

```

