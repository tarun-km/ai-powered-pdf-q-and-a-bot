import customtkinter as ctk
import fitz  # PyMuPDF
import ollama
import os
from tkinter import filedialog, messagebox

# Load Poppins Font
FONT_PATH = "fonts/Poppins-Regular.ttf"
CUSTOM_FONT = ("Poppins", 14)

class PDFAnalyzerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window setup
        self.title("AI-Powered PDF Analyzer")
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=10, padx=20, fill="x")

        self.label = ctk.CTkLabel(self.header_frame, text="📄 AI-Powered PDF Analyzer", font=("Poppins", 20, "bold"))
        self.label.pack(side="left", padx=10)

        self.upload_btn = ctk.CTkButton(self.header_frame, text="📂 Upload PDF", command=self.open_file_dialog, fg_color="#0084ff", hover_color="#005bb5", width=120, font=CUSTOM_FONT)
        self.upload_btn.pack(side="right", padx=10)

        # PDF Display Frame
        self.pdf_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        self.pdf_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.text_display = ctk.CTkTextbox(self.pdf_frame, height=10, wrap="word", fg_color="#262626", text_color="white", font=CUSTOM_FONT)
        self.text_display.pack(pady=10, padx=10, fill="both", expand=True)

        # Question Input
        self.question_entry = ctk.CTkEntry(self, placeholder_text="Ask a question about the PDF...", fg_color="#262626", text_color="white", font=CUSTOM_FONT, height=40)
        self.question_entry.pack(pady=10, padx=20, fill="x")

        # Action Buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=5, padx=20, fill="x")

        self.ask_btn = ctk.CTkButton(self.button_frame, text="🔎 Ask AI", command=self.ask_ai, fg_color="#00cc44", hover_color="#009933", width=120, font=CUSTOM_FONT)
        self.ask_btn.pack(side="left", padx=5)

        self.clear_btn = ctk.CTkButton(self.button_frame, text="🗑 Clear", command=self.clear_fields, fg_color="#cc0000", hover_color="#990000", width=100, font=CUSTOM_FONT)
        self.clear_btn.pack(side="right", padx=5)

        # AI Response Display
        self.response_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        self.response_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.response_display = ctk.CTkTextbox(self.response_frame, height=10, wrap="word", fg_color="#262626", text_color="white", font=CUSTOM_FONT)
        self.response_display.pack(pady=10, padx=10, fill="both", expand=True)

    def open_file_dialog(self):
        """Opens file dialog to select a PDF file."""
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, file_path):
        """Loads the selected PDF and extracts text."""
        try:
            print("[INFO] Uploading PDF...")
            print("[INFO] Extracting text from PDF...")
            self.pdf_text = self.extract_text_from_pdf(file_path)

            if self.pdf_text:
                print("[INFO] PDF Loaded Successfully!")
                self.text_display.delete("1.0", "end")
                self.text_display.insert("1.0", self.pdf_text[:2000])  # Show first 2000 chars
            else:
                print("[ERROR] Could not extract text. The PDF may be empty.")
                self.show_error("Could not extract text. The PDF may be empty.")

        except Exception as e:
            print(f"[ERROR] Error loading PDF: {str(e)}")
            self.show_error(f"Error loading PDF: {str(e)}")

    def extract_text_from_pdf(self, file_path):
        """Extracts text from a PDF file."""
        try:
            doc = fitz.open(file_path)
            text = "\n".join(page.get_text("text") for page in doc)
            return text.strip() if text else "No readable text found in PDF."
        except Exception as e:
            raise RuntimeError(f"Failed to extract text: {str(e)}")

    def ask_ai(self):
        """Queries the AI model with the extracted text and user question."""
        question = self.question_entry.get().strip()
        if not question:
            print("[ERROR] No question entered.")
            self.show_error("Please enter a question.")
            return

        if not self.pdf_text:
            print("[ERROR] No PDF loaded.")
            self.show_error("Please upload and load a PDF first.")
            return

        print(f"[INFO] User asked: \"{question}\"")
        print("[INFO] AI is analyzing...")

        response = self.query_llm(question, self.pdf_text)

        print("[INFO] AI Response Generated!")
        self.response_display.delete("1.0", "end")
        self.response_display.insert("1.0", response)

    def query_llm(self, question, context):
        """Sends the extracted text and question to the local Ollama AI model."""
        try:
            prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
            response = ollama.chat(model="phi", messages=[{"role": "user", "content": prompt}])
            return response['message']['content'] if 'message' in response else "No response received."
        except Exception as e:
            print(f"[ERROR] AI Query Error: {str(e)}")
            return f"Error querying AI: {str(e)}. Make sure Ollama is running."

    def clear_fields(self):
        """Clears input fields and responses."""
        print("[INFO] Clearing input fields.")
        self.question_entry.delete(0, "end")
        self.response_display.delete("1.0", "end")

    def show_error(self, message):
        """Displays an error message box."""
        messagebox.showerror("Error", message)

# Run the application
if __name__ == "__main__":
    print("[INFO] Starting AI-Powered PDF Analyzer...")
    app = PDFAnalyzerApp()
    app.mainloop()
