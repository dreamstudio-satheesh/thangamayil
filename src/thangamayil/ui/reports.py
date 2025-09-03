"""
Reports Window
Interface for generating and viewing various business reports
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime, timedelta
from ..models.billing import BillingManager


class ReportsWindow:
    """Reports interface"""
    
    def __init__(self):
        self.window = None
        self.reports_data = []
    
    def show(self, parent=None):
        """Display the reports window"""
        self.window = tk.Toplevel(parent)
        self.window.title("Reports - தங்கமயில் சில்க்ஸ்")
        self.window.geometry("1000x700")
        
        # Set up proper window cleanup
        self.window.protocol("WM_DELETE_WINDOW", self.close_window)
        
        try:
            if parent:
                self.window.transient(parent)
            self.window.grab_set()
        except tk.TclError:
            pass  # Skip if parent window is not available
        
        self.create_widgets()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
    
    def close_window(self):
        """Properly close the reports window"""
        if self.window:
            try:
                self.window.grab_release()
            except tk.TclError:
                pass
            self.window.destroy()
            self.window = None
    
    def create_widgets(self):
        """Create the UI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Report selection
        self.create_left_panel(main_frame)
        
        # Right panel - Report display
        self.create_right_panel(main_frame)
    
    def create_left_panel(self, parent):
        """Create left panel with report options"""
        left_panel = ttk.LabelFrame(parent, text="Reports", padding="10")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Date selection
        date_frame = ttk.LabelFrame(left_panel, text="Date Range", padding="10")
        date_frame.pack(fill=tk.X, pady=(0, 20))
        
        # From date
        ttk.Label(date_frame, text="From Date:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.from_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        from_date_entry = ttk.Entry(date_frame, textvariable=self.from_date, width=12)
        from_date_entry.grid(row=0, column=1, padx=(10, 0), pady=2)
        
        # To date
        ttk.Label(date_frame, text="To Date:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.to_date = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_date_entry = ttk.Entry(date_frame, textvariable=self.to_date, width=12)
        to_date_entry.grid(row=1, column=1, padx=(10, 0), pady=2)
        
        # Quick date buttons
        quick_dates_frame = ttk.Frame(date_frame)
        quick_dates_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(quick_dates_frame, text="Today", 
                  command=self.set_today, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="Yesterday", 
                  command=self.set_yesterday, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(quick_dates_frame, text="This Week", 
                  command=self.set_this_week, width=8).pack(side=tk.LEFT, padx=2)
        
        # Report types
        reports_frame = ttk.LabelFrame(left_panel, text="Available Reports", padding="10")
        reports_frame.pack(fill=tk.X, pady=(0, 20))
        
        report_buttons = [
            ("📈 Daily Sales Report", self.show_daily_sales_report),
            ("👥 Staff Performance", self.show_staff_performance),
            ("🧾 Bills Summary", self.show_bills_summary),
            ("💰 Payment Mode Report", self.show_payment_mode_report),
            ("📊 GST Summary", self.show_gst_summary),
        ]
        
        for text, command in report_buttons:
            ttk.Button(reports_frame, text=text, command=command, width=20).pack(fill=tk.X, pady=2)
        
        # Export options
        export_frame = ttk.LabelFrame(left_panel, text="Export", padding="10")
        export_frame.pack(fill=tk.X)
        
        ttk.Button(export_frame, text="Export to CSV", 
                  command=self.export_to_csv, width=20).pack(fill=tk.X, pady=2)
        ttk.Button(export_frame, text="Print Report", 
                  command=self.print_report, width=20).pack(fill=tk.X, pady=2)
    
    def create_right_panel(self, parent):
        """Create right panel for report display"""
        right_panel = ttk.LabelFrame(parent, text="Report Display", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Report title
        self.report_title = ttk.Label(right_panel, text="Select a report to view", 
                                     font=("Arial", 14, "bold"))
        self.report_title.grid(row=0, column=0, pady=(0, 10))
        
        # Report display area
        display_frame = ttk.Frame(right_panel)
        display_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Create treeview for report data
        self.report_tree = ttk.Treeview(display_frame, show='headings')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=self.report_tree.yview)
        h_scrollbar = ttk.Scrollbar(display_frame, orient="horizontal", command=self.report_tree.xview)
        self.report_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.report_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Summary frame (below treeview)
        self.summary_frame = ttk.LabelFrame(right_panel, text="Summary", padding="10")
        self.summary_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.summary_text = tk.Text(self.summary_frame, height=4, wrap=tk.WORD)
        summary_scrollbar = ttk.Scrollbar(self.summary_frame, orient="vertical", command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)
        
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        ttk.Button(right_panel, text="Close", command=self.window.destroy).grid(row=3, column=0, pady=(10, 0))
    
    def set_today(self):
        """Set date range to today"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.from_date.set(today)
        self.to_date.set(today)
    
    def set_yesterday(self):
        """Set date range to yesterday"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.from_date.set(yesterday)
        self.to_date.set(yesterday)
    
    def set_this_week(self):
        """Set date range to this week"""
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())
        self.from_date.set(start_of_week.strftime("%Y-%m-%d"))
        self.to_date.set(today.strftime("%Y-%m-%d"))
    
    def show_daily_sales_report(self):
        """Show daily sales report"""
        try:
            from_date = self.from_date.get()
            to_date = self.to_date.get()
            
            bills = BillingManager.get_bills_by_date(from_date, to_date)
            
            # Configure treeview columns
            columns = ('Date', 'Invoice', 'Staff', 'Items', 'Amount', 'Payment')
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'
            
            # Configure column headings
            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=100)
            
            # Clear existing data
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            # Add data
            total_amount = 0
            total_bills = len(bills)
            
            for bill in bills:
                values = (
                    bill['bill_date'][:10],  # Date only
                    bill['invoice_number'],
                    bill['staff_name'],
                    bill['item_count'],
                    f"₹{bill['grand_total']:.2f}",
                    bill['payment_mode']
                )
                self.report_tree.insert('', 'end', values=values)
                total_amount += bill['grand_total']
            
            # Update title and summary
            self.report_title.config(text=f"Daily Sales Report ({from_date} to {to_date})")
            
            summary = f"Total Bills: {total_bills}\n"
            summary += f"Total Amount: ₹{total_amount:.2f}\n"
            if total_bills > 0:
                summary += f"Average Bill Value: ₹{total_amount/total_bills:.2f}\n"
            
            self.update_summary(summary)
            self.reports_data = bills
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def show_staff_performance(self):
        """Show staff performance report"""
        try:
            from_date = self.from_date.get()
            to_date = self.to_date.get()
            
            bills = BillingManager.get_bills_by_date(from_date, to_date)
            
            # Group by staff
            staff_performance = {}
            for bill in bills:
                staff_name = bill['staff_name']
                if staff_name not in staff_performance:
                    staff_performance[staff_name] = {
                        'bills': 0,
                        'total_amount': 0,
                        'total_items': 0
                    }
                
                staff_performance[staff_name]['bills'] += 1
                staff_performance[staff_name]['total_amount'] += bill['grand_total']
                staff_performance[staff_name]['total_items'] += bill['item_count']
            
            # Configure treeview columns
            columns = ('Staff', 'Bills', 'Items', 'Total Sales', 'Avg Bill')
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'
            
            # Configure column headings
            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=120)
            
            # Clear existing data
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            # Add data
            for staff_name, perf in staff_performance.items():
                avg_bill = perf['total_amount'] / perf['bills'] if perf['bills'] > 0 else 0
                values = (
                    staff_name,
                    perf['bills'],
                    perf['total_items'],
                    f"₹{perf['total_amount']:.2f}",
                    f"₹{avg_bill:.2f}"
                )
                self.report_tree.insert('', 'end', values=values)
            
            # Update title and summary
            self.report_title.config(text=f"Staff Performance Report ({from_date} to {to_date})")
            
            total_bills = sum(p['bills'] for p in staff_performance.values())
            total_amount = sum(p['total_amount'] for p in staff_performance.values())
            
            summary = f"Total Staff: {len(staff_performance)}\n"
            summary += f"Total Bills: {total_bills}\n"
            summary += f"Total Sales: ₹{total_amount:.2f}\n"
            
            self.update_summary(summary)
            self.reports_data = list(staff_performance.items())
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def show_bills_summary(self):
        """Show bills summary report"""
        try:
            from_date = self.from_date.get()
            to_date = self.to_date.get()
            
            bills = BillingManager.get_bills_by_date(from_date, to_date)
            
            # Configure treeview columns
            columns = ('Invoice', 'Date', 'Time', 'Staff', 'Subtotal', 'GST', 'Total')
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'
            
            # Configure column headings
            for col in columns:
                self.report_tree.heading(col, text=col)
                if col in ['Subtotal', 'GST', 'Total']:
                    self.report_tree.column(col, width=80, anchor='e')
                else:
                    self.report_tree.column(col, width=100)
            
            # Clear existing data
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            # Add data
            total_subtotal = 0
            total_gst = 0
            total_amount = 0
            
            for bill in bills:
                gst_amount = bill.get('cgst_amount', 0) + bill.get('sgst_amount', 0) + bill.get('igst_amount', 0)
                
                values = (
                    bill['invoice_number'],
                    bill['bill_date'][:10],
                    bill['bill_date'][11:16] if len(bill['bill_date']) > 11 else '',
                    bill['staff_name'],
                    f"₹{bill['subtotal']:.2f}",
                    f"₹{gst_amount:.2f}",
                    f"₹{bill['grand_total']:.2f}"
                )
                self.report_tree.insert('', 'end', values=values)
                
                total_subtotal += bill['subtotal']
                total_gst += gst_amount
                total_amount += bill['grand_total']
            
            # Update title and summary
            self.report_title.config(text=f"Bills Summary Report ({from_date} to {to_date})")
            
            summary = f"Total Bills: {len(bills)}\n"
            summary += f"Total Subtotal: ₹{total_subtotal:.2f}\n"
            summary += f"Total GST: ₹{total_gst:.2f}\n"
            summary += f"Grand Total: ₹{total_amount:.2f}"
            
            self.update_summary(summary)
            self.reports_data = bills
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def show_payment_mode_report(self):
        """Show payment mode report"""
        try:
            from_date = self.from_date.get()
            to_date = self.to_date.get()
            
            bills = BillingManager.get_bills_by_date(from_date, to_date)
            
            # Group by payment mode
            payment_summary = {}
            for bill in bills:
                mode = bill['payment_mode']
                if mode not in payment_summary:
                    payment_summary[mode] = {
                        'count': 0,
                        'amount': 0
                    }
                
                payment_summary[mode]['count'] += 1
                payment_summary[mode]['amount'] += bill['grand_total']
            
            # Configure treeview columns
            columns = ('Payment Mode', 'Count', 'Amount', 'Percentage')
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'
            
            # Configure column headings
            for col in columns:
                self.report_tree.heading(col, text=col)
                self.report_tree.column(col, width=120)
            
            # Clear existing data
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            # Calculate total for percentage
            total_amount = sum(p['amount'] for p in payment_summary.values())
            
            # Add data
            for mode, data in payment_summary.items():
                percentage = (data['amount'] / total_amount * 100) if total_amount > 0 else 0
                values = (
                    mode,
                    data['count'],
                    f"₹{data['amount']:.2f}",
                    f"{percentage:.1f}%"
                )
                self.report_tree.insert('', 'end', values=values)
            
            # Update title and summary
            self.report_title.config(text=f"Payment Mode Report ({from_date} to {to_date})")
            
            total_bills = sum(p['count'] for p in payment_summary.values())
            summary = f"Total Bills: {total_bills}\n"
            summary += f"Total Amount: ₹{total_amount:.2f}\n"
            summary += f"Payment Methods: {len(payment_summary)}"
            
            self.update_summary(summary)
            self.reports_data = list(payment_summary.items())
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def show_gst_summary(self):
        """Show GST summary report"""
        try:
            from_date = self.from_date.get()
            to_date = self.to_date.get()
            
            bills = BillingManager.get_bills_by_date(from_date, to_date)
            
            # Configure treeview columns
            columns = ('Invoice', 'Date', 'Subtotal', 'CGST', 'SGST', 'IGST', 'Total GST')
            self.report_tree['columns'] = columns
            self.report_tree['show'] = 'headings'
            
            # Configure column headings
            for col in columns:
                self.report_tree.heading(col, text=col)
                if col != 'Invoice' and col != 'Date':
                    self.report_tree.column(col, width=80, anchor='e')
                else:
                    self.report_tree.column(col, width=100)
            
            # Clear existing data
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            # Add data
            total_subtotal = 0
            total_cgst = 0
            total_sgst = 0
            total_igst = 0
            
            for bill in bills:
                cgst = bill.get('cgst_amount', 0)
                sgst = bill.get('sgst_amount', 0)
                igst = bill.get('igst_amount', 0)
                total_gst = cgst + sgst + igst
                
                values = (
                    bill['invoice_number'],
                    bill['bill_date'][:10],
                    f"₹{bill['subtotal']:.2f}",
                    f"₹{cgst:.2f}",
                    f"₹{sgst:.2f}",
                    f"₹{igst:.2f}",
                    f"₹{total_gst:.2f}"
                )
                self.report_tree.insert('', 'end', values=values)
                
                total_subtotal += bill['subtotal']
                total_cgst += cgst
                total_sgst += sgst
                total_igst += igst
            
            # Update title and summary
            self.report_title.config(text=f"GST Summary Report ({from_date} to {to_date})")
            
            total_gst_collected = total_cgst + total_sgst + total_igst
            summary = f"Taxable Amount: ₹{total_subtotal:.2f}\n"
            summary += f"CGST Collected: ₹{total_cgst:.2f}\n"
            summary += f"SGST Collected: ₹{total_sgst:.2f}\n"
            summary += f"IGST Collected: ₹{total_igst:.2f}\n"
            summary += f"Total GST: ₹{total_gst_collected:.2f}"
            
            self.update_summary(summary)
            self.reports_data = bills
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def update_summary(self, summary_text):
        """Update the summary display"""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_text)
    
    def export_to_csv(self):
        """Export current report to CSV"""
        if not self.reports_data:
            messagebox.showwarning("No Data", "No report data to export")
            return
        
        try:
            # Get current report title to determine report type
            report_title = self.report_title.cget("text")
            
            # Generate default filename based on report type and date range
            from_date = self.from_date.get()
            to_date = self.to_date.get()
            date_str = f"{from_date}_to_{to_date}" if from_date != to_date else from_date
            
            if "Daily Sales" in report_title:
                filename = f"daily_sales_report_{date_str}.csv"
            elif "Staff Performance" in report_title:
                filename = f"staff_performance_report_{date_str}.csv"
            elif "Bills Summary" in report_title:
                filename = f"bills_summary_report_{date_str}.csv"
            elif "Payment Mode" in report_title:
                filename = f"payment_mode_report_{date_str}.csv"
            elif "GST Summary" in report_title:
                filename = f"gst_summary_report_{date_str}.csv"
            else:
                filename = f"report_{date_str}.csv"
            
            # Ask user for file location
            file_path = filedialog.asksaveasfilename(
                title="Save CSV Report",
                initialfile=filename,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export based on current treeview columns and data
            columns = self.report_tree['columns']
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(columns)
                
                # Write data from treeview
                for child in self.report_tree.get_children():
                    row_data = self.report_tree.item(child, 'values')
                    writer.writerow(row_data)
                
                # Add summary section if available
                summary_text = self.summary_text.get(1.0, tk.END).strip()
                if summary_text:
                    writer.writerow([])  # Empty row
                    writer.writerow(["=== SUMMARY ==="])
                    for line in summary_text.split('\n'):
                        if line.strip():
                            writer.writerow([line.strip()])
            
            messagebox.showinfo("Export Successful", f"Report exported to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")
    
    def print_report(self):
        """Print current report"""
        if not self.reports_data:
            messagebox.showwarning("No Data", "No report data to print")
            return
        
        # TODO: Implement printing
        messagebox.showinfo("Print", "Print functionality to be implemented")