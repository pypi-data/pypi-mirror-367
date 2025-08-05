"""
Progressive UI Module for PyMBO
Provides responsive user interfaces with progress feedback and interruption capabilities
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
from typing import Any, Callable, Dict, List, Optional, Union
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class OperationStatus(Enum):
    """Status of a progressive operation"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"

@dataclass
class ProgressInfo:
    """Information about operation progress"""
    current: int
    total: int
    percentage: float
    stage: str
    message: str
    elapsed_time: float
    estimated_remaining: float
    status: OperationStatus

class ProgressDialog:
    """Modal progress dialog with cancellation support"""
    
    def __init__(self, parent, title: str = "Processing", cancellable: bool = True):
        """
        Initialize progress dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            cancellable: Whether operation can be cancelled
        """
        self.parent = parent
        self.cancelled = False
        self.paused = False
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self._center_dialog()
        
        # Create UI elements
        self._create_widgets(cancellable)
        
        # Progress tracking
        self.start_time = time.time()
        self.last_update_time = time.time()
        
        logger.debug(f"ProgressDialog created: {title}")
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent window position and size
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Calculate center position
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_widgets(self, cancellable: bool):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Stage label
        self.stage_label = ttk.Label(main_frame, text="Initializing...", font=("Arial", 10, "bold"))
        self.stage_label.pack(pady=(0, 5))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100, 
            length=350,
            mode='determinate'
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Percentage label
        self.percentage_label = ttk.Label(main_frame, text="0%")
        self.percentage_label.pack()
        
        # Status message
        self.message_label = ttk.Label(main_frame, text="", wraplength=350)
        self.message_label.pack(pady=(5, 0))
        
        # Time information frame
        time_frame = ttk.Frame(main_frame)
        time_frame.pack(pady=(10, 0), fill=tk.X)
        
        self.elapsed_label = ttk.Label(time_frame, text="Elapsed: 0s")
        self.elapsed_label.pack(side=tk.LEFT)
        
        self.remaining_label = ttk.Label(time_frame, text="Remaining: --")
        self.remaining_label.pack(side=tk.RIGHT)
        
        # Button frame
        if cancellable:
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=(15, 0))
            
            self.pause_button = ttk.Button(
                button_frame, 
                text="Pause", 
                command=self._toggle_pause,
                width=10
            )
            self.pause_button.pack(side=tk.LEFT, padx=(0, 5))
            
            self.cancel_button = ttk.Button(
                button_frame, 
                text="Cancel", 
                command=self._cancel_operation,
                width=10
            )
            self.cancel_button.pack(side=tk.LEFT)
    
    def update_progress(self, progress_info: ProgressInfo):
        """Update progress dialog with new information"""
        if self.dialog.winfo_exists():
            # Update progress bar and percentage
            self.progress_var.set(progress_info.percentage)
            self.percentage_label.config(text=f"{progress_info.percentage:.1f}%")
            
            # Update stage and message
            self.stage_label.config(text=progress_info.stage)
            self.message_label.config(text=progress_info.message)
            
            # Update time information
            elapsed_str = self._format_time(progress_info.elapsed_time)
            self.elapsed_label.config(text=f"Elapsed: {elapsed_str}")
            
            if progress_info.estimated_remaining > 0:
                remaining_str = self._format_time(progress_info.estimated_remaining)
                self.remaining_label.config(text=f"Remaining: {remaining_str}")
            else:
                self.remaining_label.config(text="Remaining: --")
            
            # Update button states based on status
            if hasattr(self, 'pause_button'):
                if progress_info.status == OperationStatus.PAUSED:
                    self.pause_button.config(text="Resume")
                elif progress_info.status == OperationStatus.RUNNING:
                    self.pause_button.config(text="Pause")
                else:
                    self.pause_button.config(state=tk.DISABLED)
            
            # Auto-close on completion or error
            if progress_info.status in [OperationStatus.COMPLETED, OperationStatus.ERROR]:
                self.dialog.after(1500, self.close)  # Close after 1.5 seconds
            
            # Force update
            self.dialog.update()
    
    def _format_time(self, seconds: float) -> str:
        """Format time in human-readable format"""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _toggle_pause(self):
        """Toggle pause state"""
        self.paused = not self.paused
        logger.info(f"Operation {'paused' if self.paused else 'resumed'}")
    
    def _cancel_operation(self):
        """Cancel the operation"""
        self.cancelled = True
        if hasattr(self, 'cancel_button'):
            self.cancel_button.config(text="Cancelling...", state=tk.DISABLED)
        logger.info("Operation cancellation requested")
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        return self.cancelled
    
    def is_paused(self) -> bool:
        """Check if operation is paused"""
        return self.paused
    
    def close(self):
        """Close the progress dialog"""
        if self.dialog.winfo_exists():
            self.dialog.destroy()

class ProgressiveOperationManager:
    """Manage progressive operations with UI feedback"""
    
    def __init__(self, parent_window=None):
        """
        Initialize progressive operation manager
        
        Args:
            parent_window: Parent window for dialogs
        """
        self.parent_window = parent_window
        self.active_operations = {}
        self.operation_counter = 0
        self._lock = threading.Lock()
        
        logger.info("ProgressiveOperationManager initialized")
    
    def run_progressive_operation(
        self,
        operation_func: Callable,
        *args,
        title: str = "Processing",
        cancellable: bool = True,
        show_dialog: bool = True,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Run an operation with progressive UI feedback
        
        Args:
            operation_func: Function to execute
            title: Dialog title
            cancellable: Whether operation can be cancelled
            show_dialog: Whether to show progress dialog
            callback: Optional callback for completion
            *args, **kwargs: Arguments for operation_func
            
        Returns:
            Operation result or None if cancelled
        """
        with self._lock:
            operation_id = self.operation_counter
            self.operation_counter += 1
        
        progress_dialog = None
        if show_dialog and self.parent_window:
            progress_dialog = ProgressDialog(self.parent_window, title, cancellable)
        
        # Create progress tracking
        progress_tracker = ProgressTracker(operation_id, progress_dialog)
        
        def operation_wrapper():
            """Wrapper that handles progress tracking"""
            try:
                # Add progress tracker to kwargs
                kwargs['progress_tracker'] = progress_tracker
                
                # Execute operation
                result = operation_func(*args, **kwargs)
                
                # Mark as completed
                progress_tracker.complete("Operation completed successfully")
                
                if callback:
                    callback(result)
                
                return result
                
            except Exception as e:
                progress_tracker.error(f"Operation failed: {str(e)}")
                logger.error(f"Progressive operation failed: {e}", exc_info=True)
                
                if callback:
                    callback(None)
                
                raise
            finally:
                with self._lock:
                    self.active_operations.pop(operation_id, None)
                
                if progress_dialog:
                    progress_dialog.close()
        
        # Store operation info
        with self._lock:
            self.active_operations[operation_id] = {
                'progress_tracker': progress_tracker,
                'progress_dialog': progress_dialog,
                'title': title
            }
        
        # Run operation in thread
        if show_dialog:
            # Run in background thread
            thread = threading.Thread(target=operation_wrapper, daemon=True)
            thread.start()
            
            # Keep dialog responsive
            while thread.is_alive():
                if progress_dialog and progress_dialog.dialog.winfo_exists():
                    progress_dialog.dialog.update()
                time.sleep(0.1)
            
            thread.join()
        else:
            # Run directly
            return operation_wrapper()
    
    def get_active_operations(self) -> Dict[int, Dict[str, Any]]:
        """Get information about active operations"""
        with self._lock:
            return {
                op_id: {
                    'title': info['title'],
                    'progress': info['progress_tracker'].get_current_progress()
                }
                for op_id, info in self.active_operations.items()
            }
    
    def cancel_operation(self, operation_id: int) -> bool:
        """Cancel a specific operation"""
        with self._lock:
            if operation_id in self.active_operations:
                progress_tracker = self.active_operations[operation_id]['progress_tracker']
                progress_tracker.cancel()
                return True
        return False
    
    def cancel_all_operations(self):
        """Cancel all active operations"""
        with self._lock:
            for operation_info in self.active_operations.values():
                progress_tracker = operation_info['progress_tracker']
                progress_tracker.cancel()

class ProgressTracker:
    """Track progress of a long-running operation"""
    
    def __init__(self, operation_id: int, progress_dialog: Optional[ProgressDialog] = None):
        """
        Initialize progress tracker
        
        Args:
            operation_id: Unique operation identifier
            progress_dialog: Optional progress dialog to update
        """
        self.operation_id = operation_id
        self.progress_dialog = progress_dialog
        self.start_time = time.time()
        self.last_update_time = time.time()
        
        self.current_progress = ProgressInfo(
            current=0,
            total=100,
            percentage=0.0,
            stage="initializing",
            message="Starting operation...",
            elapsed_time=0.0,
            estimated_remaining=0.0,
            status=OperationStatus.PENDING
        )
        
        self._cancelled = False
        self._paused = False
    
    def update(
        self,
        current: int,
        total: int,
        stage: str = "",
        message: str = ""
    ):
        """Update progress information"""
        if self._cancelled:
            raise InterruptedError("Operation was cancelled")
        
        # Wait if paused
        while self._paused and not self._cancelled:
            time.sleep(0.1)
        
        if self._cancelled:
            raise InterruptedError("Operation was cancelled")
        
        # Calculate progress
        percentage = (current / total * 100) if total > 0 else 0
        elapsed_time = time.time() - self.start_time
        
        # Estimate remaining time
        if current > 0 and percentage > 0:
            estimated_total_time = elapsed_time / (percentage / 100)
            estimated_remaining = max(0, estimated_total_time - elapsed_time)
        else:
            estimated_remaining = 0.0
        
        # Update progress info
        self.current_progress = ProgressInfo(
            current=current,
            total=total,
            percentage=percentage,
            stage=stage or self.current_progress.stage,
            message=message or self.current_progress.message,
            elapsed_time=elapsed_time,
            estimated_remaining=estimated_remaining,
            status=OperationStatus.PAUSED if self._paused else OperationStatus.RUNNING
        )
        
        # Update dialog if present
        if self.progress_dialog:
            self.progress_dialog.update_progress(self.current_progress)
            
            # Check for user cancellation
            if self.progress_dialog.is_cancelled():
                self._cancelled = True
                raise InterruptedError("Operation was cancelled by user")
            
            # Update pause state
            self._paused = self.progress_dialog.is_paused()
        
        self.last_update_time = time.time()
        logger.debug(f"Progress updated: {percentage:.1f}% - {stage}")
    
    def set_stage(self, stage: str, message: str = ""):
        """Set current operation stage"""
        self.current_progress.stage = stage
        if message:
            self.current_progress.message = message
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(self.current_progress)
    
    def complete(self, message: str = "Operation completed"):
        """Mark operation as completed"""
        self.current_progress.status = OperationStatus.COMPLETED
        self.current_progress.message = message
        self.current_progress.percentage = 100.0
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(self.current_progress)
        
        logger.info(f"Operation {self.operation_id} completed: {message}")
    
    def error(self, message: str):
        """Mark operation as failed"""
        self.current_progress.status = OperationStatus.ERROR
        self.current_progress.message = message
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(self.current_progress)
        
        logger.error(f"Operation {self.operation_id} failed: {message}")
    
    def cancel(self):
        """Cancel the operation"""
        self._cancelled = True
        self.current_progress.status = OperationStatus.CANCELLED
        self.current_progress.message = "Operation cancelled"
        
        if self.progress_dialog:
            self.progress_dialog.update_progress(self.current_progress)
        
        logger.info(f"Operation {self.operation_id} cancelled")
    
    def is_cancelled(self) -> bool:
        """Check if operation is cancelled"""
        return self._cancelled
    
    def is_paused(self) -> bool:
        """Check if operation is paused"""
        return self._paused
    
    def get_current_progress(self) -> ProgressInfo:
        """Get current progress information"""
        return self.current_progress

class ResponsiveUI:
    """Base class for responsive UI components"""
    
    def __init__(self, update_interval: float = 0.1):
        """
        Initialize responsive UI
        
        Args:
            update_interval: UI update interval in seconds
        """
        self.update_interval = update_interval
        self.update_queue = queue.Queue()
        self.running = False
        self.update_thread = None
    
    def start_updates(self):
        """Start the UI update loop"""
        if not self.running:
            self.running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            logger.debug("ResponsiveUI update loop started")
    
    def stop_updates(self):
        """Stop the UI update loop"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        logger.debug("ResponsiveUI update loop stopped")
    
    def _update_loop(self):
        """Main update loop"""
        while self.running:
            try:
                # Process queued updates
                while not self.update_queue.empty():
                    try:
                        update_func = self.update_queue.get_nowait()
                        update_func()
                        self.update_queue.task_done()
                    except queue.Empty:
                        break
                    except Exception as e:
                        logger.error(f"Error in UI update: {e}")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
    
    def queue_update(self, update_func: Callable):
        """Queue a UI update function"""
        try:
            self.update_queue.put_nowait(update_func)
        except queue.Full:
            logger.warning("UI update queue is full, skipping update")
    
    def force_update(self):
        """Force immediate processing of queued updates"""
        while not self.update_queue.empty():
            try:
                update_func = self.update_queue.get_nowait()
                update_func()
            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"Error in forced update: {e}")

# Example usage functions
def progressive_optimization_example(
    optimizer,
    n_iterations: int = 100,
    progress_tracker: Optional[ProgressTracker] = None
) -> Any:
    """Example of a progressive optimization function"""
    if not progress_tracker:
        return None
    
    results = []
    
    for i in range(n_iterations):
        # Check for cancellation
        if progress_tracker.is_cancelled():
            break
        
        # Simulate some work
        time.sleep(0.1)
        
        # Update progress
        progress_tracker.update(
            current=i + 1,
            total=n_iterations,
            stage=f"Iteration {i + 1}",
            message=f"Processing iteration {i + 1} of {n_iterations}"
        )
        
        # Simulate optimization step
        result = {"iteration": i + 1, "value": np.random.random()}
        results.append(result)
    
    return results

# Global instance
progressive_manager = None

def get_progressive_manager(parent_window=None) -> ProgressiveOperationManager:
    """Get global progressive operation manager"""
    global progressive_manager
    if progressive_manager is None:
        progressive_manager = ProgressiveOperationManager(parent_window)
    return progressive_manager

__all__ = [
    'ProgressDialog', 'ProgressiveOperationManager', 'ProgressTracker',
    'ResponsiveUI', 'ProgressInfo', 'OperationStatus',
    'progressive_optimization_example', 'get_progressive_manager'
]