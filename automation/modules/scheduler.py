"""
modules/scheduler.py — Agendamento automático
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self):
        import schedule
        self.schedule = schedule
        self._tarefas = []

    def agendar(self, hora, funcao, *args, **kwargs):
        self.schedule.every().day.at(hora).do(funcao, *args, **kwargs)
        self._tarefas.append({"hora": hora, "funcao": funcao.__name__})

    def executar(self):
        import time
        print(f"[{datetime.now()}] Scheduler ativo. Ctrl+C para parar.")
        try:
            while True:
                self.schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            print("Scheduler parado.")
