import customtkinter as ctk
from pypdf import PdfReader
import json
from CTkMessagebox import CTkMessagebox
import threading

class PDFConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PDF to JSON Converter")
        self.geometry("700x600")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Frame for file inputs
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # PDF File selection
        self.pdf_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Select PDF file...")
        self.pdf_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.pdf_button = ctk.CTkButton(self.file_frame, text="Browse PDF", command=self.browse_pdf)
        self.pdf_button.grid(row=0, column=1, padx=10, pady=10)
        
        # JSON File selection
        self.json_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Select output JSON file...")
        self.json_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.json_button = ctk.CTkButton(self.file_frame, text="Save JSON As", command=self.browse_json)
        self.json_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Configure frame grid
        self.file_frame.grid_columnconfigure(0, weight=1)
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0,1), weight=1)
        
        # Convert button
        self.convert_button = ctk.CTkButton(self.button_frame, text="Convert PDF to JSON", 
                                          command=self.start_conversion,
                                          fg_color="green")
        self.convert_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Clear button
        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear All", 
                                        command=self.clear_all,
                                        fg_color="red")
        self.clear_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Text output
        self.text_output = ctk.CTkTextbox(self, wrap="word")
        self.text_output.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress.set(0)
    
    def clear_all(self):
        # Clear file entries
        self.pdf_entry.delete(0, "end")
        self.json_entry.delete(0, "end")
        # Clear text output
        self.text_output.delete("1.0", "end")
        # Reset progress bar
        self.progress.stop()
        self.progress.set(0)
    
    def browse_pdf(self):
        filename = ctk.filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        self.pdf_entry.delete(0, "end")
        self.pdf_entry.insert(0, filename)
    
    def browse_json(self):
        filename = ctk.filedialog.asksaveasfilename(defaultextension=".json",
                                                   filetypes=[("JSON Files", "*.json")])
        self.json_entry.delete(0, "end")
        self.json_entry.insert(0, filename)
    
    def start_conversion(self):
        thread = threading.Thread(target=self.convert_pdf_to_json)
        thread.start()
    
    def convert_pdf_to_json(self):
        pdf_path = self.pdf_entry.get()
        json_path = self.json_entry.get()
        
        if not pdf_path or not json_path:
            CTkMessagebox(title="Error", message="Please select both files", icon="warning")
            return
        
        try:
            self.progress.start()
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            records = self.parse_text(text)
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=4, ensure_ascii=False)
            
            self.text_output.delete("1.0", "end")
            self.text_output.insert("1.0", text)
            self.progress.stop()
            self.progress.set(1)
            
            CTkMessagebox(title="Success", message="Conversion completed!", icon="check")
            
        except Exception as e:
            CTkMessagebox(title="Error", message=str(e), icon="cancel")
            self.progress.stop()
            self.progress.set(0)
    
    def parse_text(self, text):
        lines = [line for line in text.split('\n') if line.strip()]
        records = []
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 3:
                records.append({
                    "CP": parts[0],
                    "Provincia": ' '.join(parts[1:-1]),
                    "Localidad": parts[-1]
                })
        
        return records

if __name__ == "__main__":
    app = PDFConverter()
    app.mainloop()