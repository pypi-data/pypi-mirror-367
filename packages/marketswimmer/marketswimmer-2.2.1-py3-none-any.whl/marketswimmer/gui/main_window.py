import sys
import os
import subprocess
import threading
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLabel, QInputDialog, QTextEdit, 
                             QMessageBox, QProgressBar, QFrame, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor

# Optional logging - only import if available
try:
    from logger_config import setup_logger, log_function_entry, log_gui_event, log_subprocess_call, log_function_exit
    LOGGING_ENABLED = True
    logger = setup_logger()
except ImportError:
    # Fallback dummy functions if logging not available
    def log_function_entry(*args, **kwargs): pass
    def log_gui_event(*args, **kwargs): pass
    def log_subprocess_call(*args, **kwargs): pass
    def log_function_exit(*args, **kwargs): pass
    
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def debug(self, msg): pass
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
    
    LOGGING_ENABLED = False
    logger = DummyLogger()

class WorkerThread(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, command, timeout=10):
        super().__init__()
        self.command = command
        self.timeout = timeout

    def run(self):
        log_function_entry(f"WorkerThread.run() args=[{self.command}]")
        logger.info(f"Starting subprocess: {self.command}")
        
        if LOGGING_ENABLED:
            log_subprocess_call()
        
        try:
            # Keep the original working directory instead of changing to GUI directory
            # This ensures files are created where the user expects them
            original_cwd = os.getcwd()
            logger.debug(f"Using working directory: {original_cwd}")
            
            # Create the subprocess with unbuffered output
            logger.debug(f"Creating subprocess: {self.command}")
            import os
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Force unbuffered output
            
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,  # Unbuffered
                universal_newlines=True,
                cwd=original_cwd,
                env=env  # Use environment with unbuffered Python
            )
            
            logger.info(f"Subprocess PID: {process.pid}")
            
            # Read output with timeout using threading for Windows compatibility
            import time
            import threading
            import queue
            
            def read_output(proc, q):
                """Read output in a separate thread to avoid blocking"""
                try:
                    for line in iter(proc.stdout.readline, ''):
                        if line:
                            q.put(line.rstrip())
                        if proc.poll() is not None:
                            break
                except Exception as e:
                    q.put(f"Error reading output: {e}")
                finally:
                    q.put(None)  # Signal end of output
            
            output_queue = queue.Queue()
            reader_thread = threading.Thread(target=read_output, args=(process, output_queue))
            reader_thread.daemon = True
            reader_thread.start()
            
            start_time = time.time()
            last_output_time = start_time
            
            while True:
                # Check if process has finished
                if process.poll() is not None:
                    break
                    
                # Check for timeout
                current_time = time.time()
                if current_time - start_time > self.timeout:
                    if self.timeout > 60:  # If using the longer timeout for downloads
                        self.output_signal.emit("⏱️ Download timeout reached")
                        self.output_signal.emit("📁 Browser should be open - please download XLSX file manually")
                        self.output_signal.emit("🔄 Click 'Calculate Owner Earnings' once download completes")
                    else:
                        self.output_signal.emit("⚠️ Process timeout - this command requires manual interaction")
                        self.output_signal.emit("📁 Opening browser for manual download...")
                    process.terminate()
                    process.wait()
                    self.error_signal.emit(f"Process timed out after {self.timeout} seconds - download manually and use Calculate Owner Earnings")
                    return
                
                # Try to get output from queue with short timeout
                try:
                    line = output_queue.get(timeout=0.5)
                    if line is None:  # End of output signal
                        break
                    self.output_signal.emit(line)
                    last_output_time = current_time
                except queue.Empty:
                    # No output available, continue checking
                    time.sleep(0.1)
            
            # Wait for process to complete and get final output
            process.wait()
            
            # Get any remaining output from queue
            while True:
                try:
                    line = output_queue.get_nowait()
                    if line is None:
                        break
                    self.output_signal.emit(line)
                except queue.Empty:
                    break
            
            if process.returncode == 0:
                logger.info(f"Subprocess completed successfully with return code: {process.returncode}")
                self.finished_signal.emit()
            else:
                error_msg = f"Process failed with return code: {process.returncode}"
                logger.error(error_msg)
                self.error_signal.emit(error_msg)
                
        except Exception as e:
            error_msg = f"Error running subprocess: {str(e)}"
            logger.error(error_msg)
            self.error_signal.emit(error_msg)

class MarketSwimmerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        log_function_entry("MarketSwimmerGUI.__init__()")
        log_gui_event("GUI_INIT_START")
        
        self.setWindowTitle("MarketSwimmer - Financial Analysis Tool")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: #fafafa;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: #fafafa;
            }
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #3498db;
                color: #3498db;
                padding: 10px 20px;
                text-align: center;
                font-size: 14px;
                border-radius: 6px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #3498db;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #2980b9;
                border-color: #2980b9;
                color: #ffffff;
            }
            QPushButton:disabled {
                background-color: #f5f5f5;
                border-color: #cccccc;
                color: #999999;
            }
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                background-color: #ffffff;
                color: #333333;
                line-height: 1.4;
            }
            QLabel {
                font-size: 13px;
                color: #2c3e50;
            }
            QInputDialog {
                background-color: #ffffff;
            }
        """)

        # Initialize UI
        self.init_ui()
        
        # Current ticker
        self.current_ticker = ""
        
        logger.info("GUI window created successfully")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("MarketSwimmer Financial Analysis")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Ticker input section
        ticker_group = QGroupBox("Stock Ticker Selection")
        ticker_layout = QHBoxLayout(ticker_group)
        
        self.ticker_label = QLabel("Selected Ticker: None")
        self.ticker_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #2980b9; padding: 5px;")
        
        self.select_ticker_button = QPushButton("Select Ticker")
        self.select_ticker_button.clicked.connect(self.select_ticker)
        
        ticker_layout.addWidget(self.ticker_label)
        ticker_layout.addStretch()
        ticker_layout.addWidget(self.select_ticker_button)
        
        main_layout.addWidget(ticker_group)
        
        # Analysis buttons section
        analysis_group = QGroupBox("Analysis Options")
        analysis_layout = QGridLayout(analysis_group)
        
        # Individual analysis buttons
        self.download_button = QPushButton("Download Financial Data")
        self.download_button.clicked.connect(self.download_data)
        self.download_button.setEnabled(False)
        
        self.earnings_button = QPushButton("Calculate Owner Earnings")
        self.earnings_button.clicked.connect(self.calculate_earnings)
        self.earnings_button.setEnabled(False)
        
        self.visualize_button = QPushButton("Create Visualizations")
        self.visualize_button.clicked.connect(self.create_visualizations)
        self.visualize_button.setEnabled(False)
        
        self.complete_button = QPushButton("Complete Analysis")
        self.complete_button.clicked.connect(self.run_full_analysis)
        self.complete_button.setEnabled(False)
        self.complete_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #e74c3c;
                color: #e74c3c;
                font-size: 16px;
                padding: 15px 30px;
                font-weight: 600;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #c0392b;
                border-color: #c0392b;
                color: #ffffff;
            }
        """)
        
        # Arrange buttons in grid
        analysis_layout.addWidget(self.download_button, 0, 0)
        analysis_layout.addWidget(self.earnings_button, 0, 1)
        analysis_layout.addWidget(self.visualize_button, 1, 0)
        analysis_layout.addWidget(self.complete_button, 1, 1)
        
        # Add Open Charts Folder button
        self.open_charts_button = QPushButton("Open Charts Folder")
        self.open_charts_button.clicked.connect(self.open_charts_folder)
        self.open_charts_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #27ae60;
                color: #27ae60;
                font-size: 14px;
                padding: 12px 20px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #27ae60;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #229954;
                border-color: #229954;
                color: #ffffff;
            }
        """)
        analysis_layout.addWidget(self.open_charts_button, 2, 0, 1, 2)  # Span 2 columns
        
        main_layout.addWidget(analysis_group)
        
        # Console output section
        console_group = QGroupBox("Console Output")
        console_layout = QVBoxLayout(console_group)
        
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(300)
        console_layout.addWidget(self.console_output)
        
        # Clear console button
        clear_button = QPushButton("Clear Console")
        clear_button.clicked.connect(self.clear_console)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #95a5a6;
                color: #95a5a6;
                max-width: 150px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #95a5a6;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #7f8c8d;
                border-color: #7f8c8d;
                color: #ffffff;
            }
        """)
        console_layout.addWidget(clear_button)
        
        main_layout.addWidget(console_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select a ticker to begin analysis")

    def select_ticker(self):
        log_gui_event("BUTTON_CLICK", "Select Ticker button clicked")
        
        ticker, ok = QInputDialog.getText(self, 'Select Ticker', 'Enter stock ticker symbol:')
        
        if ok and ticker:
            ticker = ticker.upper().strip()
            self.current_ticker = ticker
            self.ticker_label.setText(f"Selected Ticker: {ticker}")
            
            # Enable analysis buttons
            self.download_button.setEnabled(True)
            self.earnings_button.setEnabled(True)
            self.visualize_button.setEnabled(True)
            self.complete_button.setEnabled(True)
            
            self.console_output.append(f">> Ticker selected: {ticker}")
            self.statusBar().showMessage(f"Ticker selected: {ticker} - Ready for analysis")
            
            logger.info(f"Ticker selected: {ticker}")

    def download_data(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Download Data button clicked")
        logger.info(f"Starting data download for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Starting data download for {self.current_ticker}...")
        self.console_output.append("🌐 Opening browser for download...")
        self.console_output.append("📥 Will monitor Downloads folder for new XLSX files...")
        self.console_output.append("⏱️ Timeout: 5 minutes (plenty of time for manual download)")
        self.disable_buttons()
        self.show_progress()
        
        # Use the modern CLI for data analysis with proper timeout (5 minutes)
        command = f'python -m marketswimmer analyze {self.current_ticker} --force'
        self.worker_thread = WorkerThread(command, timeout=300)  # 5 minutes like the original
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_download_finished)
        self.worker_thread.error_signal.connect(self.on_download_timeout)
        self.worker_thread.start()

    def calculate_earnings(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Calculate Earnings button clicked")
        logger.info(f"Starting earnings calculation for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Processing downloaded data for {self.current_ticker}...")
        self.console_output.append(">> Converting XLSX files to analysis format...")
        self.disable_buttons()
        self.show_progress()
        
        # First process the downloaded XLSX files
        command = f'python process_financial_data.py {self.current_ticker}'
        self.worker_thread = WorkerThread(command, timeout=30)
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_data_processed)
        self.worker_thread.error_signal.connect(self.on_process_error)
        self.worker_thread.start()

    def create_visualizations(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Create Visualizations button clicked")
        logger.info(f"Starting visualization creation for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Creating visualizations for {self.current_ticker}...")
        self.disable_buttons()
        self.show_progress()
        
        # Use the MarketSwimmer visualization command instead of a standalone script
        # Use python command which is available in PATH
        command = f'python -m marketswimmer visualize --ticker {self.current_ticker}'
        self.run_command(command)

    def run_full_analysis(self):
        if not self.current_ticker:
            QMessageBox.warning(self, "Warning", "Please select a ticker first.")
            return
            
        log_gui_event("BUTTON_CLICK", "Complete Analysis button clicked")
        logger.info(f"Starting complete analysis for ticker: {self.current_ticker}")
        
        self.console_output.append(f"\n>> Starting complete analysis for {self.current_ticker}...")
        self.console_output.append("This will run the full analysis pipeline:")
        self.console_output.append("  1. Download financial data")
        self.console_output.append("  2. Calculate owner earnings")  
        self.console_output.append("  3. Create visualizations")
        self.console_output.append("🌐 Opening browser for download...")
        self.console_output.append("📥 Will monitor Downloads folder for new XLSX files...")
        self.console_output.append("⏱️ Timeout: 5 minutes (plenty of time for manual download)")
        self.console_output.append("Please wait...\n")
        
        self.disable_buttons()
        self.show_progress()
        
        # Use the new MarketSwimmer CLI automation with proper timeout
        command = f'python -m marketswimmer analyze {self.current_ticker}'
        logger.info(f"Full analysis command: {command}")
        
        self.worker_thread = WorkerThread(command, timeout=300)
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_process_finished)
        self.worker_thread.error_signal.connect(self.on_process_error)
        self.worker_thread.start()

    def run_command(self, command):
        """Run a command in a separate thread"""
        self.worker_thread = WorkerThread(command)
        self.worker_thread.output_signal.connect(self.update_console)
        self.worker_thread.finished_signal.connect(self.on_process_finished)
        self.worker_thread.error_signal.connect(self.on_process_error)
        self.worker_thread.start()

    def update_console(self, text):
        """Update console output with new text"""
        self.console_output.append(text)
        
        # Auto-scroll to bottom
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.console_output.setTextCursor(cursor)

    def on_process_finished(self):
        """Handle process completion"""
        self.console_output.append("\n>> Process completed successfully!")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage(f"Analysis completed for {self.current_ticker}")
        
        logger.info("Process completed successfully")

    def on_process_error(self, error_msg):
        """Handle process error"""
        self.console_output.append(f"\nERROR: {error_msg}")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Error occurred during analysis")
        
        logger.error(f"Process error: {error_msg}")

    def on_download_finished(self):
        """Handle download process completion (shouldn't happen due to manual nature)"""
        self.console_output.append("\n>> Download process completed!")
        self.console_output.append(">> Please manually download the XLSX file if it hasn't started automatically")
        self.console_output.append(">> Then click 'Calculate Owner Earnings' to process the data")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Download completed - ready to process data")
        
        logger.info("Download process completed")

    def on_download_timeout(self, error_msg):
        """Handle download timeout (expected behavior)"""
        self.console_output.append(f"\n>> {error_msg}")
        self.console_output.append(">> This is normal - the browser should have opened for manual download")
        self.console_output.append(">> Download the XLSX file manually, then click 'Calculate Owner Earnings'")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage("Ready to process downloaded data")
        
        logger.info("Download timeout - normal behavior")

    def on_data_processed(self):
        """Handle data processing completion"""
        self.console_output.append("\n>> Data processing completed successfully!")
        self.console_output.append(">> Financial data has been converted to analysis format")
        self.console_output.append(">> You can now run owner earnings calculations and visualizations")
        self.hide_progress()
        self.enable_buttons()
        self.statusBar().showMessage(f"Data processed for {self.current_ticker} - ready for analysis")
        
        logger.info("Data processing completed successfully")

    def disable_buttons(self):
        """Disable all analysis buttons during processing"""
        self.download_button.setEnabled(False)
        self.earnings_button.setEnabled(False)
        self.visualize_button.setEnabled(False)
        self.complete_button.setEnabled(False)

    def enable_buttons(self):
        """Enable all analysis buttons after processing"""
        if self.current_ticker:
            self.download_button.setEnabled(True)
            self.earnings_button.setEnabled(True)
            self.visualize_button.setEnabled(True)
            self.complete_button.setEnabled(True)

    def show_progress(self):
        """Show indeterminate progress bar"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)

    def clear_console(self):
        """Clear the console output"""
        self.console_output.clear()
        self.console_output.append("Console cleared.")
        
        logger.info("Console cleared by user")

    def open_charts_folder(self):
        """Open the charts folder in Windows Explorer"""
        log_gui_event("BUTTON_CLICK", "Open Charts Folder button clicked")
        
        charts_folder = Path("charts")
        if not charts_folder.exists():
            charts_folder.mkdir(parents=True, exist_ok=True)
            self.console_output.append(">> Created charts folder")
        
        # Open the folder in Windows Explorer
        try:
            os.startfile(str(charts_folder.absolute()))
            self.console_output.append(f">> Opened charts folder: {charts_folder.absolute()}")
            logger.info(f"Opened charts folder: {charts_folder.absolute()}")
        except Exception as e:
            error_msg = f"Could not open charts folder: {str(e)}"
            self.console_output.append(f"ERROR: {error_msg}")
            logger.error(error_msg)

def main():
    log_function_entry("main()")
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("MarketSwimmer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("MarketSwimmer Analytics")
    
    # Create and show the main window
    window = MarketSwimmerGUI()
    window.show()
    
    logger.info("MarketSwimmer GUI started successfully")
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
