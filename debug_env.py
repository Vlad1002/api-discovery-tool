import sys
import firecrawl

print("--- Informații de Depanare ---")

# 1. Afișează calea către executabilul Python folosit
print(f"Executabil Python: {sys.executable}")

# 2. Afișează versiunea bibliotecii firecrawl
print(f"Versiune Firecrawl: {firecrawl.__version__}")

# 3. Listează toate atributele și metodele disponibile în obiectul FirecrawlApp
from firecrawl import FirecrawlApp
# Folosim o cheie falsă doar pentru a putea inspecta obiectul
app = FirecrawlApp(api_key="test-key") 

print("\nAtribute/Metode disponibile în FirecrawlApp:")
for attr in dir(app):
    if not attr.startswith('_'):
        print(f"- {attr}")

print("\n--- Sfârșit Depanare ---")