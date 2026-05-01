import os
try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not installed. Checking file existence and sizes only.")
    PyPDF2 = None

raw_dir = r'c:\Users\nisar\OneDrive\Documents\SEM 2\AI for engineers\EV_project\data\raw'
files = os.listdir(raw_dir)
pdfs = [f for f in files if f.lower().endswith('.pdf')]

print(f"Total PDFs found: {len(pdfs)}")
for f in pdfs:
    path = os.path.join(raw_dir, f)
    size = os.path.getsize(path)
    print(f"\n--- {f} ---")
    print(f"Size: {size / 1024 / 1024:.2f} MB")
    
    if PyPDF2:
        try:
            with open(path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                pages = len(reader.pages)
                print(f"Pages: {pages}")
                # Try to extract first 100 chars
                first_page = reader.pages[0].extract_text()
                print(f"Preview (100 chars): {first_page[:100].strip()}...")
        except Exception as e:
            print(f"Error reading PDF: {e}")
    else:
        print("Cannot verify internal content (PyPDF2 missing)")
