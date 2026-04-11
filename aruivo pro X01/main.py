"""CIS — Ponto de entrada."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.store import init_db

def main():
    init_db()
    print("🧠 CIS iniciado.")
    print("Modo: bot telegram")
    from bot.telegram_bot import run_bot
    run_bot()

if __name__ == "__main__":
    main()
