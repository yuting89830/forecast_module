from threading import Thread, current_thread
from queue import Queue as _Queue
from analysis.DBhandler import DbHandler
from analysis.localization import analyze
from color_log import color
logging = color.setup(name=__name__, level=color.INFO)

class Analyzer:
    def __init__(self, queue: _Queue, cv, config,
                 db_persistence=False,
                 log_level: int=color.DEBUG):
        self.config = config
        self.queue = queue
        self.cv = cv
        self.db_persistence = db_persistence
        self.thread = Thread(target=self.run, args=(self.queue,))
        self.log_level_sub = log_level
        logging.setLevel(log_level)
        self.db_watchdog_rollback = 3

    def start(self):
        if not self.db_persistence:
            try:
                with DbHandler(self.config, persistence=self.db_persistence,
                               log_level=self.log_level_sub) as dh:
                    dh.createDatabase()
                    dh.createTable()
                    logging.info("Connected to database")
                    logging.info("Created Table and Database")
                    
            except Exception as e:
                logging.error(f"Unable to connect to database", exc_info=e)
        self.thread.start()

    def run(self, queue: _Queue):
        t = current_thread()
        entries = []
        while getattr(t, "do_run", True):
            # logging.verbose("Analyzer running")
            with self.cv:
                # logging.verbose("Analyzer go to sleep")
                self.cv.wait_for(
                    lambda: not queue.empty() or not getattr(t, "do_run", True), 
                    timeout=5)
            # logging.verbose("Analyzer woke up")
            logging.debug(f'{self.queue.qsize() = }')
            while not queue.empty():
                try:
                    time_frame_analysis = queue.get(timeout=2)
                except Exception as e:
                    logging.error(e)
                    continue
                queue.task_done()
                analyzed_entries = analyze(time_frame_analysis, self.config)
                entries += analyzed_entries
            # logging.debug("is there something to send to the database?")
            if len(entries) > 0:
                # logging.debug("YES, there is something to send to the database")
                try:
                    # logging.debug(f"{self.db_persistence=}")
                    with DbHandler(self.config, persistence=self.db_persistence,
                                   log_level=self.log_level_sub) as dh:
                        logging.debug("Connection is ok")
                        dh.insert(entries)
                        logging.info(color.bg_lightgrey("Data inserted to the database with success! Cleaning buffer..."))
                        entries = []
                except Exception as e:
                    self.db_watchdog_rollback -= 1
                    logging.error(f"Unable to send entries, retrying the next time (trial: {self.db_watchdog_rollback})", exc_info=e)
                    if self.db_watchdog_rollback == 0:
                        logging.fatal(f'Impossible to send entries! Abort these entries. (with {self.db_watchdog_rollback} retries)')
                        entries = []
                        

    def stop(self):
        logging.info("Stopping Analyzer!")
        self.thread.do_run = False
        with self.cv:
            self.cv.notify()
        self.thread.join()
