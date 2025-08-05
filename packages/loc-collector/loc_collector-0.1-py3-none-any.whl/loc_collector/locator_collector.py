#!/usr/bin/env python3

"""
Advanced Chrome Visual Element Picker Tool with Multiple Selection - FIXED VERSION
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
import json
import logging
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ElementPicker:
    """Advanced Chrome-only element picker with multiple selection"""

    def __init__(self):
        self.driver = None
        self.is_picking = False
        self.collected_elements = []

        # Enhanced JavaScript for multiple element picking
        self.picker_js = """
        // Ensure we don't create duplicates
        if (typeof window.elementPicker !== 'undefined') {
            window.elementPicker.stop();
        }

        window.elementPicker = {
            isActive: false,
            currentElement: null,
            selectedElements: [],
            selectedCount: 0,

            start: function() {
                console.log('ElementPicker: Starting selection mode');
                this.isActive = true;
                this.selectedElements = [];
                this.selectedCount = 0;
                document.body.style.cursor = 'crosshair';
                document.addEventListener('mouseover', this.onMouseOver.bind(this), true);
                document.addEventListener('click', this.onClick.bind(this), true);
                document.addEventListener('keydown', this.onKeyDown.bind(this), true);
                this.showMessage('Click elements to select (green border = selected). Press ENTER to finish, ESC to cancel.');
                return true;
            },

            stop: function() {
                console.log('ElementPicker: Stopping selection mode');
                this.isActive = false;
                document.body.style.cursor = '';
                document.removeEventListener('mouseover', this.onMouseOver, true);
                document.removeEventListener('click', this.onClick, true);
                document.removeEventListener('keydown', this.onKeyDown, true);
                this.clearHighlight();
                this.hideMessage();
                return true;
            },

            onMouseOver: function(event) {
                if (!this.isActive) return;
                event.stopPropagation();
                this.highlightElement(event.target);
            },

            onClick: function(event) {
                if (!this.isActive) return;
                event.preventDefault();
                event.stopPropagation();

                var element = event.target;
                var elementId = this.getElementId(element);

                // Check if element is already selected
                var existingIndex = this.selectedElements.findIndex(e => e.elementId === elementId);

                if (existingIndex >= 0) {
                    // Deselect element
                    this.selectedElements.splice(existingIndex, 1);
                    element.style.border = '';
                    element.style.backgroundColor = '';
                    this.selectedCount--;
                } else {
                    // Select element
                    var info = this.getElementInfo(element);
                    info.elementId = elementId;
                    this.selectedElements.push(info);
                    element.style.border = '3px solid #00ff00';
                    element.style.backgroundColor = 'rgba(0, 255, 0, 0.2)';
                    this.selectedCount++;
                }

                this.updateMessage();
                return false;
            },

            onKeyDown: function(event) {
                if (!this.isActive) return;

                if (event.keyCode === 27) { // ESC key
                    event.preventDefault();
                    this.cancelSelection();
                } else if (event.keyCode === 13) { // ENTER key
                    event.preventDefault();
                    this.finishSelection();
                }
            },

            cancelSelection: function() {
                console.log('ElementPicker: Cancelling selection');
                this.selectedElements.forEach(info => {
                    var element = document.querySelector('[data-picker-id="' + info.elementId + '"]');
                    if (element) {
                        element.style.border = '';
                        element.style.backgroundColor = '';
                        element.removeAttribute('data-picker-id');
                    }
                });
                this.selectedElements = [];
                this.stop();
                window.selectedElementsInfo = null;
            },

            finishSelection: function() {
                console.log('ElementPicker: Finishing selection with ' + this.selectedElements.length + ' elements');
                // Clean up selection indicators
                this.selectedElements.forEach(info => {
                    var element = document.querySelector('[data-picker-id="' + info.elementId + '"]');
                    if (element) {
                        element.style.border = '';
                        element.style.backgroundColor = '';
                        element.removeAttribute('data-picker-id');
                    }
                });

                window.selectedElementsInfo = this.selectedElements.slice(); // Create a copy
                this.stop();
            },

            highlightElement: function(element) {
                this.clearHighlight();
                if (!element || element === document.body) return;

                this.currentElement = element;
                var elementId = this.getElementId(element);
                var isSelected = this.selectedElements.some(e => e.elementId === elementId);

                if (!isSelected) {
                    element.style.outline = '3px solid #ff0000';
                    element.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
                }

                try {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } catch (e) {
                    // Fallback if smooth scrolling fails
                    element.scrollIntoView();
                }
            },

            clearHighlight: function() {
                if (this.currentElement) {
                    var elementId = this.getElementId(this.currentElement);
                    var isSelected = this.selectedElements.some(e => e.elementId === elementId);

                    if (!isSelected) {
                        this.currentElement.style.outline = '';
                        this.currentElement.style.backgroundColor = '';
                    }
                    this.currentElement = null;
                }
            },

            getElementId: function(element) {
                if (!element.hasAttribute('data-picker-id')) {
                    element.setAttribute('data-picker-id', 'picker-' + Date.now() + '-' + Math.random());
                }
                return element.getAttribute('data-picker-id');
            },

            getElementInfo: function(element) {
                var rect = element.getBoundingClientRect();

                // Get element type
                var elementType = this.getElementType(element);

                // Get text content (simplified)
                var text = '';
                if (element.tagName.toLowerCase() === 'input') {
                    text = element.value || element.placeholder || '';
                } else if (element.tagName.toLowerCase() === 'img') {
                    text = element.alt || element.title || '';
                } else {
                    text = (element.textContent || '').trim();
                    // Limit text length
                    if (text.length > 100) {
                        text = text.substring(0, 100) + '...';
                    }
                }

                return {
                    tagName: element.tagName.toLowerCase(),
                    elementType: elementType,
                    text: text,
                    id: element.id || '',
                    className: element.className || '',
                    timestamp: new Date().toISOString()
                };
            },

            getElementType: function(element) {
                var tag = element.tagName.toLowerCase();

                if (tag === 'input') {
                    return element.type || 'text';
                } else if (tag === 'button') {
                    return 'button';
                } else if (tag === 'a') {
                    return 'link';
                } else if (tag === 'img') {
                    return 'image';
                } else if (tag === 'select') {
                    return 'dropdown';
                } else if (tag === 'textarea') {
                    return 'textarea';
                } else if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag)) {
                    return 'heading';
                } else if (['p', 'span', 'div'].includes(tag)) {
                    return 'text';
                } else if (['ul', 'ol', 'li'].includes(tag)) {
                    return 'list';
                } else {
                    return tag;
                }
            },

            updateMessage: function() {
                var message = 'Selected: ' + this.selectedCount + ' elements. Click more elements, ENTER to finish, ESC to cancel.';
                this.showMessage(message);
            },

            showMessage: function(text) {
                var msg = document.getElementById('picker-message');
                if (!msg) {
                    msg = document.createElement('div');
                    msg.id = 'picker-message';
                    msg.style.cssText = 
                        'position: fixed; top: 10px; left: 50%; transform: translateX(-50%);' +
                        'background: #333; color: white; padding: 10px 20px;' +
                        'border-radius: 5px; z-index: 999999; font-size: 14px;' +
                        'font-family: Arial, sans-serif; max-width: 80%;';
                    document.body.appendChild(msg);
                }
                msg.textContent = text;
            },

            hideMessage: function() {
                var msg = document.getElementById('picker-message');
                if (msg) msg.remove();
            },

            // Test function to verify injection
            test: function() {
                console.log('ElementPicker is working correctly');
                return 'ElementPicker loaded successfully';
            }
        };

        // Initialize and test
        console.log('ElementPicker script injected successfully');
        window.selectedElementsInfo = null;
        """

    def inject_javascript(self):
        """Inject JavaScript with error handling"""
        try:
            # First, inject the script
            self.driver.execute_script(self.picker_js)

            # Test if injection was successful
            test_result = self.driver.execute_script(
                "return window.elementPicker ? window.elementPicker.test() : 'FAILED'")

            if test_result == "ElementPicker loaded successfully":
                logger.info("JavaScript injection successful")
                return True
            else:
                logger.error(f"JavaScript injection test failed: {test_result}")
                return False

        except Exception as e:
            logger.error(f"Failed to inject JavaScript: {e}")
            return False

    def setup_chrome_driver(self):
        """Setup Chrome driver with appropriate options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info("Chrome driver setup successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False

    def open_url(self, url):
        """Open URL in Chrome browser"""
        try:
            if not self.driver:
                if not self.setup_chrome_driver():
                    return False

            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            self.driver.get(url)
            time.sleep(3)  # Increased wait time

            # Inject JavaScript after page load
            if not self.inject_javascript():
                return False

            logger.info(f"Opened URL: {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            return False

    def start_picking(self):
        """Start multiple element picking mode"""
        try:
            if not self.driver:
                raise Exception("Browser not opened")

            # Re-inject JavaScript to ensure it's available
            if not self.inject_javascript():
                raise Exception("Failed to inject JavaScript")

            # Verify elementPicker exists before calling start
            exists = self.driver.execute_script("return typeof window.elementPicker !== 'undefined'")
            if not exists:
                raise Exception("ElementPicker object not found")

            self.is_picking = True
            result = self.driver.execute_script("return window.elementPicker.start();")

            if result:
                logger.info("Started multiple element picking mode")
                return True
            else:
                raise Exception("Failed to start picking mode")

        except Exception as e:
            logger.error(f"Failed to start picking: {e}")
            return False

    def get_selected_elements(self):
        """Get all selected elements information"""
        try:
            if not self.driver:
                return None

            # Wait for element selection completion
            for i in range(300):  # 30 seconds timeout
                try:
                    result = self.driver.execute_script("return window.selectedElementsInfo;")
                    if result is not None:
                        self.driver.execute_script("window.selectedElementsInfo = null;")
                        self.is_picking = False
                        logger.info(f"Retrieved {len(result)} selected elements")
                        return result
                except Exception as e:
                    logger.warning(f"Error checking for selected elements: {e}")
                    break

                time.sleep(0.1)

            self.is_picking = False
            logger.info("Selection timeout or cancelled")
            return None

        except Exception as e:
            logger.error(f"Failed to get selected elements: {e}")
            return None

    def close_browser(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")


# Keep the rest of the ElementPickerGUI class unchanged
class ElementPickerGUI:
    """Enhanced GUI for the element picker tool"""

    def __init__(self):
        self.picker = ElementPicker()
        self.collected_elements = []
        self.root = tk.Tk()
        self.root.title("Advanced Chrome Element Picker")
        self.root.geometry("1000x700")
        self.setup_ui()

    # ... (rest of the GUI code remains the same)

    def setup_ui(self):
        """Setup the enhanced user interface"""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)

        # Left frame for controls
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Right frame for collected elements
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        # Setup left side controls
        self.setup_left_panel(left_frame)

        # Setup right side element list
        self.setup_right_panel(right_frame)

    def setup_left_panel(self, parent):
        """Setup the control panel"""
        # URL frame
        url_frame = ttk.LabelFrame(parent, text="Browser Control", padding="5")
        url_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky='w')
        self.url_var = tk.StringVar(value="https://example.com")
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=40)
        url_entry.grid(row=0, column=1, padx=(5, 10), sticky='ew')

        ttk.Button(url_frame, text="Open Browser", command=self.open_browser).grid(row=0, column=2)
        ttk.Button(url_frame, text="Close Browser", command=self.close_browser).grid(row=0, column=3, padx=(5, 0))

        url_frame.columnconfigure(1, weight=1)

        # Control frame
        control_frame = ttk.LabelFrame(parent, text="Element Picker", padding="5")
        control_frame.pack(fill='x', pady=(0, 10))

        self.pick_button = ttk.Button(control_frame, text="Start Picking Elements", command=self.start_picking)
        self.pick_button.pack(side='left')

        self.clear_button = ttk.Button(control_frame, text="Clear All", command=self.clear_all_elements)
        self.clear_button.pack(side='left', padx=(10, 0))

        self.export_button = ttk.Button(control_frame, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(side='left', padx=(10, 0))

        # Status frame
        status_frame = ttk.Frame(control_frame)
        status_frame.pack(side='right')

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack()

        self.count_var = tk.StringVar(value="Elements collected: 0")
        ttk.Label(status_frame, textvariable=self.count_var, font=('Arial', 9)).pack()

        # Results frame (simplified view)
        results_frame = ttk.LabelFrame(parent, text="Last Selection Details", padding="5")
        results_frame.pack(fill='both', expand=True)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.results_text.pack(fill='both', expand=True)

    def setup_right_panel(self, parent):
        """Setup the collected elements panel"""
        elements_frame = ttk.LabelFrame(parent, text="Collected Elements", padding="5")
        elements_frame.pack(fill='both', expand=True)

        # Treeview for elements list
        columns = ('ID', 'Type', 'Tag', 'Text Preview')
        self.elements_tree = ttk.Treeview(elements_frame, columns=columns, show='tree headings', height=20)

        # Configure columns
        self.elements_tree.heading('#0', text='#')
        self.elements_tree.column('#0', width=50, minwidth=30)

        for col in columns:
            self.elements_tree.heading(col, text=col)
            if col == 'Text Preview':
                self.elements_tree.column(col, width=200, minwidth=100)
            else:
                self.elements_tree.column(col, width=100, minwidth=60)

        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(elements_frame, orient='vertical', command=self.elements_tree.yview)
        self.elements_tree.configure(yscrollcommand=tree_scrollbar.set)

        self.elements_tree.pack(side='left', fill='both', expand=True)
        tree_scrollbar.pack(side='right', fill='y')

        # Bind double-click to view details
        self.elements_tree.bind('<Double-1>', self.view_element_details)

    def open_browser(self):
        """Open browser with the specified URL"""

        def open_thread():
            self.status_var.set("Opening browser...")
            self.pick_button.config(state='disabled')

            url = self.url_var.get().strip()
            if not url:
                messagebox.showerror("Error", "Please enter a URL")
                self.status_var.set("Ready")
                self.pick_button.config(state='normal')
                return

            success = self.picker.open_url(url)
            if success:
                self.status_var.set("Browser opened - Ready to pick elements")
                self.pick_button.config(state='normal')
            else:
                messagebox.showerror("Error", "Failed to open browser")
                self.status_var.set("Error opening browser")
                self.pick_button.config(state='disabled')

        threading.Thread(target=open_thread, daemon=True).start()

    def close_browser(self):
        """Close the browser"""
        self.picker.close_browser()
        self.status_var.set("Browser closed")
        self.pick_button.config(state='disabled')
        self.results_text.delete(1.0, tk.END)

    def start_picking(self):
        """Start the element picking process"""

        def picking_thread():
            self.status_var.set("Select elements in browser (ENTER to finish, ESC to cancel)")
            self.pick_button.config(state='disabled')

            # Start picking mode
            if not self.picker.start_picking():
                messagebox.showerror("Error", "Failed to start picking mode")
                self.status_var.set("Error")
                self.pick_button.config(state='normal')
                return

            # Wait for elements selection
            elements_info = self.picker.get_selected_elements()

            if elements_info and len(elements_info) > 0:
                # Add to collected elements
                for element in elements_info:
                    element['collection_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.collected_elements.append(element)

                self.update_elements_list()
                self.display_last_selection(elements_info)
                self.status_var.set(f"Added {len(elements_info)} elements successfully")
            else:
                self.status_var.set("No elements selected or cancelled")

            self.pick_button.config(state='normal')
            self.count_var.set(f"Elements collected: {len(self.collected_elements)}")

        threading.Thread(target=picking_thread, daemon=True).start()

    # ... (rest of the methods remain unchanged)
    def update_elements_list(self):
        """Update the elements treeview"""
        # Clear existing items
        for item in self.elements_tree.get_children():
            self.elements_tree.delete(item)

        # Add collected elements
        for i, element in enumerate(self.collected_elements, 1):
            text_preview = element.get('text', '')[:50] + ('...' if len(element.get('text', '')) > 50 else '')

            self.elements_tree.insert('', 'end',
                                      text=str(i),
                                      values=(
                                          element.get('id', 'N/A'),
                                          element.get('elementType', 'N/A'),
                                          element.get('tagName', 'N/A'),
                                          text_preview
                                      ))

    def view_element_details(self, event):
        """View details of selected element"""
        selection = self.elements_tree.selection()
        if selection:
            item = self.elements_tree.item(selection[0])
            element_index = int(item['text']) - 1

            if 0 <= element_index < len(self.collected_elements):
                element = self.collected_elements[element_index]
                self.display_element_details(element)

    def display_last_selection(self, elements_list):
        """Display the last selection in the results area"""
        self.results_text.delete(1.0, tk.END)

        output = []
        output.append("=" * 50)
        output.append(f"LAST SELECTION - {len(elements_list)} ELEMENTS")
        output.append("=" * 50)

        for i, element in enumerate(elements_list, 1):
            output.append(f"\nElement #{i}:")
            output.append(f"  Type: {element.get('elementType', 'N/A')}")
            output.append(f"  Tag: {element.get('tagName', 'N/A')}")
            output.append(f"  ID: {element.get('id', 'None')}")
            output.append(f"  Class: {element.get('className', 'None')}")
            output.append(f"  Text: {element.get('text', 'None')}")

        self.results_text.insert(tk.END, "\n".join(output))

    def display_element_details(self, element):
        """Display detailed information for a single element"""
        self.results_text.delete(1.0, tk.END)

        output = []
        output.append("=" * 50)
        output.append("ELEMENT DETAILS")
        output.append("=" * 50)
        output.append(f"Element Type: {element.get('elementType', 'N/A')}")
        output.append(f"Tag Name: {element.get('tagName', 'N/A')}")
        output.append(f"ID: {element.get('id', 'None')}")
        output.append(f"Class: {element.get('className', 'None')}")
        output.append(f"Text Content: {element.get('text', 'None')}")
        output.append(f"Collection Time: {element.get('collection_time', 'N/A')}")

        self.results_text.insert(tk.END, "\n".join(output))

    def clear_all_elements(self):
        """Clear all collected elements"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all collected elements?"):
            self.collected_elements.clear()
            self.update_elements_list()
            self.results_text.delete(1.0, tk.END)
            self.count_var.set("Elements collected: 0")
            self.status_var.set("All elements cleared")

    def export_to_csv(self):
        """Export collected elements to CSV"""
        if not self.collected_elements:
            messagebox.showwarning("Warning", "No elements to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Elements as CSV"
        )

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['element_type', 'tag_name', 'id', 'class_name', 'text_content', 'collection_time']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for element in self.collected_elements:
                        writer.writerow({
                            'element_type': element.get('elementType', ''),
                            'tag_name': element.get('tagName', ''),
                            'id': element.get('id', ''),
                            'class_name': element.get('className', ''),
                            'text_content': element.get('text', ''),
                            'collection_time': element.get('collection_time', '')
                        })

                messagebox.showinfo("Success", f"Elements exported successfully to:\n{filename}")
                self.status_var.set(f"Exported {len(self.collected_elements)} elements to CSV")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV:\n{e}")

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = ElementPickerGUI()
        app.run()
    except KeyboardInterrupt:
        print("Application terminated by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start: {e}")
