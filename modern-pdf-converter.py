import customtkinter as ctk
from pypdf import PdfReader
import json
import re
import threading
from pathlib import Path
from CTkMessagebox import CTkMessagebox
import tkinter as tk

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PDFConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PDF to JSON Converter Pro")
        self.geometry("800x700")
        self.minsize(700, 600)
        
        # Variables de control
        self.conversion_running = False
        self.show_text_preview = tk.BooleanVar(value=True)
        
        self._setup_ui()
        self._configure_grid()
    
    def _setup_ui(self):
        # Frame principal de archivos
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        
        # Sección PDF
        ctk.CTkLabel(self.file_frame, text="PDF File:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.pdf_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Select PDF file...")
        self.pdf_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.pdf_button = ctk.CTkButton(self.file_frame, text="Browse...", width=90, command=self.browse_pdf)
        self.pdf_button.grid(row=1, column=1, padx=5, pady=5)
        
        # Sección JSON
        ctk.CTkLabel(self.file_frame, text="JSON Output:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.json_entry = ctk.CTkEntry(self.file_frame, placeholder_text="Select output JSON file...")
        self.json_entry.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        self.json_button = ctk.CTkButton(self.file_frame, text="Save As...", width=90, command=self.browse_json)
        self.json_button.grid(row=3, column=1, padx=5, pady=5)
        
        # Botones de acción
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.convert_button = ctk.CTkButton(
            self.button_frame, 
            text="Convert PDF to JSON", 
            command=self.start_conversion,
            fg_color="#2AAA8A",
            hover_color="#228B22"
        )
        self.convert_button.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear All",
            command=self.clear_all,
            fg_color="#FF6347",
            hover_color="#CD5C5C"
        )
        self.clear_button.pack(side="right", padx=10, pady=5, fill="x", expand=True)
        
        # Opciones adicionales
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        self.preview_check = ctk.CTkCheckBox(
            self.options_frame,
            text="Show text preview",
            variable=self.show_text_preview,
            onvalue=True,
            offvalue=False
        )
        self.preview_check.pack(side="left", padx=10, pady=5)
        
        # Área de texto con scroll
        self.text_output = ctk.CTkTextbox(self, wrap="word", activate_scrollbars=True)
        self.text_output.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # Barra de progreso
        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress.set(0)
    
    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.file_frame.grid_columnconfigure(0, weight=1)
    
    def clear_all(self):
        self.pdf_entry.delete(0, "end")
        self.json_entry.delete(0, "end")
        self.text_output.delete("1.0", "end")
        self.progress.stop()
        self.progress.set(0)
        self.conversion_running = False
    
    def browse_pdf(self):
        filename = ctk.filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filename:
            self.pdf_entry.delete(0, "end")
            self.pdf_entry.insert(0, filename)
    
    def browse_json(self):
        filename = ctk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if filename:
            self.json_entry.delete(0, "end")
            self.json_entry.insert(0, filename)
    
    def start_conversion(self):
        if not self.conversion_running:
            self.conversion_running = True
            self.convert_button.configure(state="disabled")
            thread = threading.Thread(target=self.convert_pdf_to_json)
            thread.start()
    
    def _update_progress(self, value):
        self.progress.set(value)
    
    def _show_error(self, message):
        CTkMessagebox(title="Error", message=message, icon="cancel")
    
    def convert_pdf_to_json(self):
        try:
            pdf_path = self.pdf_entry.get()
            json_path = self.json_entry.get()
            
            # Validación de archivos
            if not pdf_path or not json_path:
                self.after(0, lambda: self._show_error("Please select both files"))
                return
            
            if not Path(pdf_path).exists():
                self.after(0, lambda: self._show_error("PDF file does not exist"))
                return
            
            try:
                reader = PdfReader(pdf_path)
                total_pages = len(reader.pages)
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Invalid PDF file: {str(e)}"))
                return
            
            try:
                text = ""
                for i, page in enumerate(reader.pages):
                    text += page.extract_text()
                    progress = (i + 1) / total_pages
                    self.after(0, self._update_progress, progress)
                
                records = self._parse_text(text)
                
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(records, f, indent=4, ensure_ascii=False)
                
                if self.show_text_preview.get():
                    self.after(0, self._update_text_output, text)
                
                self.after(0, lambda: CTkMessagebox(
                    title="Success", 
                    message="Conversion completed successfully!", 
                    icon="check"
                ))
                
            except Exception as e:
                self.after(0, lambda: self._show_error(str(e)))
            
        finally:
            self.after(0, lambda: self.convert_button.configure(state="normal"))
            self.conversion_running = False
            self.after(0, lambda: self.progress.set(0))
    
    def _update_text_output(self, text):
        self.text_output.delete("1.0", "end")
        self.text_output.insert("1.0", text[:50000])  # Limitar a 50,000 caracteres
    
    def _parse_text(self, text):
        pattern = re.compile(
            r'^(\d{5})\s+'          # Código postal (5 dígitos)
            r'(.+?)\s+'             # Provincia (todo hasta el último espacio)
            r'([^\d]+)$',           # Localidad (resto del texto)
            flags=re.MULTILINE
        )
        
        records = []
        for match in pattern.finditer(text):
            records.append({
                "CP": match.group(1),
                "Provincia": match.group(2).strip(),
                "Localidad": match.group(3).strip()
            })
        
        return records

if __name__ == "__main__":
    app = PDFConverter()
    app.mainloop()
