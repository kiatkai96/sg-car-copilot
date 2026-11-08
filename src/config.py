"""Settings in one place. If you want to tweak behaviour, start here."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Where your knowledge files live
DOCS_DIR = ROOT / "data" / "docs"      # text you paste from official pages
RAW_DIR = ROOT / "data" / "raw"        # raw downloads (e.g. COE csv)
CARS_CSV = ROOT / "data" / "cars.csv"  # your small list of car models

# Where the "search index" gets saved on your computer
DB_DIR = ROOT / "chroma_db"
COLLECTION = "sg_car_copilot"

# The small free model that turns text into numbers (runs on your laptop)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# How big each "piece" of text is (in characters). ~800 is a good start.
CHUNK_CHARS = 800

# How many pieces we fetch for each question
TOP_K = 5

# If even the BEST piece is further away than this, we say "I don't know".
# Lower = stricter (more "I don't know"), higher = more willing to answer.
# You will tune this number in Step 7 of the guide.
MAX_DISTANCE = 0.65

# Shown in the app so people know how fresh your data is. EDIT THIS.
DATA_AS_OF = "EDIT ME (e.g. Nov 2026)"
