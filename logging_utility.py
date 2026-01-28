# -*- coding: utf-8 -*-
"""Logging utility for experiment runs."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from io import StringIO


class TeeStream:
    """Stream that writes to multiple outputs."""
    
    def __init__(self, *streams):
        self.streams = streams
    
    def write(self, data):
        for stream in self.streams:
            stream.write(data)
            stream.flush()
    
    def flush(self):
        for stream in self.streams:
            stream.flush()


class ExperimentLogger:
    """Logger for experiment runs with per-loop log files."""
    
    def __init__(self, dag_yaml_path: str, model_name: str, num_loops: int, loop_retry_max: int, label: str = None):
        """Initialize experiment logger with metadata.
        
        Args:
            dag_yaml_path: Path to the DAG YAML file
            model_name: Name of the LLM model
            num_loops: Number of loops to run
            loop_retry_max: Maximum retries per loop
            label: Optional custom label for the experiment
        """
        self.dag_yaml_path = dag_yaml_path
        self.model_name = model_name
        self.num_loops = num_loops
        self.loop_retry_max = loop_retry_max
        
        # Create experiment ID from timestamp and label (or dag name if no label)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if label:
            # Normalize label: lowercase and replace spaces with underscores
            identifier = label.lower().replace(" ", "_")
        else:
            identifier = Path(dag_yaml_path).stem
        self.experiment_id = f"{timestamp}_{identifier}"
        
        # Create output directory if it doesn't exist
        self.log_dir = Path("output") / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_loop_logger = None
    
    def create_loop_logger(self, loop_num: int) -> logging.Logger:
        """Create a logger for a specific loop.
        
        Args:
            loop_num: The loop number
            
        Returns:
            A configured logger for the loop
        """
        log_filename = f"{self.experiment_id}_loop_{loop_num}.log"
        log_filepath = self.log_dir / log_filename
        
        # Create logger
        logger = logging.getLogger(f"exp_{self.experiment_id}_loop_{loop_num}")
        logger.setLevel(logging.DEBUG)
        logger.handlers = []  # Clear any existing handlers
        
        # File handler - writes to file
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter (no timestamp, just like console output)
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.propagate = False
        
        self.current_loop_logger = logger
        self.current_log_filepath = log_filepath
        return logger
    
    @contextmanager
    def redirect_output(self):
        """Context manager to redirect stdout and stderr to both console and log file."""
        if self.current_loop_logger is None:
            raise RuntimeError("No logger created. Call create_loop_logger first.")
        
        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Open log file in append mode for direct writing
        with open(self.current_log_filepath, 'a') as log_file:
            # Create tee streams that write to both console and file
            tee_stdout = TeeStream(original_stdout, log_file)
            tee_stderr = TeeStream(original_stderr, log_file)
            
            try:
                sys.stdout = tee_stdout
                sys.stderr = tee_stderr
                yield
            finally:
                # Restore original stdout/stderr
                sys.stdout = original_stdout
                sys.stderr = original_stderr
    
    def log_experiment_metadata(self, logger: logging.Logger):
        """Log experiment metadata at the start of a log file.
        
        Args:
            logger: The logger to write metadata to
        """
        logger.info(f"[Loading DAG from YAML] {self.dag_yaml_path}")
        logger.info(f"[LLM Model] {self.model_name}")
        logger.info(f"[Number of Loops] {self.num_loops}")
        logger.info(f"[Retry Budget per Loop] {self.loop_retry_max}")
        logger.info(f"[Experiment ID] {self.experiment_id}")
        logger.info("")
    
    def get_log_filepath(self, loop_num: int) -> str:
        """Get the log file path for a specific loop.
        
        Args:
            loop_num: The loop number
            
        Returns:
            Path to the log file
        """
        log_filename = f"{self.experiment_id}_loop_{loop_num}.log"
        return str(self.log_dir / log_filename)
