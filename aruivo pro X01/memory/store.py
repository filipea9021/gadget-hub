import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from store import *
from store import DB_PATH, init_db, save_content, get_history, get_last_content_id, get_scraping_stats, get_best_dnas_v2, has_real_dna
