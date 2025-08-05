"""
Asynchronous Processing Module for PyMBO
Provides non-blocking computation capabilities for UI responsiveness
"""

import asyncio
import concurrent.futures
import os
import threading
import time
import logging
from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
import numpy as np
import torch
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ProgressUpdate:
    """Progress update information"""
    current: int
    total: int
    stage: str
    message: str
    percentage: float
    elapsed_time: float

class AsyncOptimizer:
    """Asynchronous optimization wrapper for non-blocking operations"""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize async optimizer
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers or min(4, (os.cpu_count() or 1) + 1)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.current_tasks = {}
        self.progress_callbacks = []
        self._task_counter = 0
        self._lock = threading.Lock()
        
        logger.info(f"AsyncOptimizer initialized with {self.max_workers} workers")
    
    def add_progress_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Add a progress callback function"""
        with self._lock:
            self.progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Remove a progress callback function"""
        with self._lock:
            if callback in self.progress_callbacks:
                self.progress_callbacks.remove(callback)
    
    def _notify_progress(self, progress: ProgressUpdate):
        """Notify all progress callbacks"""
        with self._lock:
            for callback in self.progress_callbacks:
                try:
                    callback(progress)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")
    
    async def run_optimization_async(
        self, 
        optimizer_func: Callable,
        *args,
        task_name: str = "optimization",
        **kwargs
    ) -> Any:
        """
        Run optimization function asynchronously
        
        Args:
            optimizer_func: Function to run asynchronously
            task_name: Name for the task
            *args, **kwargs: Arguments for the function
            
        Returns:
            Future result of the optimization
        """
        with self._lock:
            task_id = self._task_counter
            self._task_counter += 1
        
        logger.info(f"Starting async task '{task_name}' (ID: {task_id})")
        
        start_time = time.time()
        
        def progress_wrapper():
            """Wrapper that provides progress updates"""
            try:
                # Create progress tracking
                progress = ProgressUpdate(
                    current=0,
                    total=100,
                    stage="initializing",
                    message=f"Starting {task_name}",
                    percentage=0.0,
                    elapsed_time=0.0
                )
                self._notify_progress(progress)
                
                # Run the actual function
                result = optimizer_func(*args, **kwargs)
                
                # Final progress update
                elapsed = time.time() - start_time
                progress = ProgressUpdate(
                    current=100,
                    total=100,
                    stage="completed",
                    message=f"{task_name} completed",
                    percentage=100.0,
                    elapsed_time=elapsed
                )
                self._notify_progress(progress)
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                progress = ProgressUpdate(
                    current=0,
                    total=100,
                    stage="error",
                    message=f"Error in {task_name}: {str(e)}",
                    percentage=0.0,
                    elapsed_time=elapsed
                )
                self._notify_progress(progress)
                raise
        
        # Submit to thread pool
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(self.executor, progress_wrapper)
        
        self.current_tasks[task_id] = {
            'future': future,
            'task_name': task_name,
            'start_time': start_time
        }
        
        try:
            result = await future
            logger.info(f"Async task '{task_name}' (ID: {task_id}) completed successfully")
            return result
        except Exception as e:
            logger.error(f"Async task '{task_name}' (ID: {task_id}) failed: {e}")
            raise
        finally:
            with self._lock:
                self.current_tasks.pop(task_id, None)
    
    def cancel_task(self, task_id: int) -> bool:
        """Cancel a running task"""
        with self._lock:
            if task_id in self.current_tasks:
                future = self.current_tasks[task_id]['future']
                return future.cancel()
        return False
    
    def get_active_tasks(self) -> Dict[int, Dict[str, Any]]:
        """Get information about active tasks"""
        with self._lock:
            return {
                task_id: {
                    'task_name': info['task_name'],
                    'elapsed_time': time.time() - info['start_time']
                }
                for task_id, info in self.current_tasks.items()
            }
    
    def shutdown(self):
        """Shutdown the async optimizer"""
        self.executor.shutdown(wait=True)
        logger.info("AsyncOptimizer shutdown complete")

class ChunkedProcessor:
    """Process large operations in chunks to maintain responsiveness"""
    
    def __init__(self, chunk_size: int = 100, delay_between_chunks: float = 0.001):
        """
        Initialize chunked processor
        
        Args:
            chunk_size: Size of each processing chunk
            delay_between_chunks: Delay between chunks in seconds
        """
        self.chunk_size = chunk_size
        self.delay = delay_between_chunks
    
    async def process_in_chunks(
        self,
        data: Union[List, np.ndarray, torch.Tensor],
        process_func: Callable,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
        stage_name: str = "processing"
    ) -> List[Any]:
        """
        Process data in chunks asynchronously
        
        Args:
            data: Data to process
            process_func: Function to apply to each chunk
            progress_callback: Optional progress callback
            stage_name: Name of the processing stage
            
        Returns:
            List of processed results
        """
        total_items = len(data)
        results = []
        start_time = time.time()
        
        for i in range(0, total_items, self.chunk_size):
            chunk_end = min(i + self.chunk_size, total_items)
            chunk = data[i:chunk_end]
            
            # Process chunk
            chunk_result = process_func(chunk)
            results.extend(chunk_result if isinstance(chunk_result, list) else [chunk_result])
            
            # Update progress
            if progress_callback:
                elapsed = time.time() - start_time
                progress = ProgressUpdate(
                    current=chunk_end,
                    total=total_items,
                    stage=stage_name,
                    message=f"Processed {chunk_end}/{total_items} items",
                    percentage=(chunk_end / total_items) * 100,
                    elapsed_time=elapsed
                )
                progress_callback(progress)
            
            # Small delay to allow other operations
            if self.delay > 0 and chunk_end < total_items:
                await asyncio.sleep(self.delay)
        
        return results

class BackgroundTaskManager:
    """Manage background tasks for long-running operations"""
    
    def __init__(self):
        self.tasks = {}
        self.task_counter = 0
        self._lock = threading.Lock()
    
    def submit_background_task(
        self,
        func: Callable,
        *args,
        task_name: str = "background_task",
        callback: Optional[Callable] = None,
        **kwargs
    ) -> int:
        """
        Submit a task to run in the background
        
        Args:
            func: Function to run
            task_name: Name for the task
            callback: Optional callback when task completes
            *args, **kwargs: Arguments for the function
            
        Returns:
            Task ID
        """
        with self._lock:
            task_id = self.task_counter
            self.task_counter += 1
        
        def task_wrapper():
            try:
                result = func(*args, **kwargs)
                if callback:
                    callback(result)
                return result
            except Exception as e:
                logger.error(f"Background task '{task_name}' failed: {e}")
                if callback:
                    callback(None)
                raise
            finally:
                with self._lock:
                    self.tasks.pop(task_id, None)
        
        thread = threading.Thread(target=task_wrapper, name=f"bg_task_{task_id}")
        thread.daemon = True
        thread.start()
        
        with self._lock:
            self.tasks[task_id] = {
                'thread': thread,
                'task_name': task_name,
                'start_time': time.time()
            }
        
        logger.info(f"Started background task '{task_name}' (ID: {task_id})")
        return task_id
    
    def is_task_running(self, task_id: int) -> bool:
        """Check if a task is still running"""
        with self._lock:
            if task_id in self.tasks:
                return self.tasks[task_id]['thread'].is_alive()
        return False
    
    def get_running_tasks(self) -> Dict[int, Dict[str, Any]]:
        """Get information about running tasks"""
        with self._lock:
            running_tasks = {}
            for task_id, info in self.tasks.items():
                if info['thread'].is_alive():
                    running_tasks[task_id] = {
                        'task_name': info['task_name'],
                        'elapsed_time': time.time() - info['start_time']
                    }
            return running_tasks

def async_wrapper(chunk_size: int = 100):
    """
    Decorator to make functions asynchronous with chunked processing
    
    Args:
        chunk_size: Size of processing chunks
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if we need chunked processing
            if 'progress_callback' in kwargs:
                progress_callback = kwargs.pop('progress_callback')
                
                # Simple async execution with progress
                loop = asyncio.get_event_loop()
                
                def progress_func():
                    # Simulate progress updates
                    start_time = time.time()
                    
                    # Initial progress
                    progress = ProgressUpdate(
                        current=0,
                        total=100,
                        stage="running",
                        message=f"Executing {func.__name__}",
                        percentage=0.0,
                        elapsed_time=0.0
                    )
                    progress_callback(progress)
                    
                    # Run function
                    result = func(*args, **kwargs)
                    
                    # Final progress
                    elapsed = time.time() - start_time
                    progress = ProgressUpdate(
                        current=100,
                        total=100,
                        stage="completed",
                        message=f"{func.__name__} completed",
                        percentage=100.0,
                        elapsed_time=elapsed
                    )
                    progress_callback(progress)
                    
                    return result
                
                return await loop.run_in_executor(None, progress_func)
            else:
                # Simple async execution
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, func, *args, **kwargs)
        
        return wrapper
    return decorator

class ProgressiveComputation:
    """Handle progressive computations that can be interrupted and resumed"""
    
    def __init__(self):
        self.checkpoints = {}
        self.interrupt_flags = {}
    
    def create_checkpoint(self, computation_id: str, state: Dict[str, Any]):
        """Create a checkpoint for a computation"""
        self.checkpoints[computation_id] = {
            'state': state,
            'timestamp': time.time()
        }
        logger.debug(f"Created checkpoint for computation: {computation_id}")
    
    def load_checkpoint(self, computation_id: str) -> Optional[Dict[str, Any]]:
        """Load a checkpoint for a computation"""
        if computation_id in self.checkpoints:
            return self.checkpoints[computation_id]['state']
        return None
    
    def set_interrupt_flag(self, computation_id: str):
        """Set interrupt flag for a computation"""
        self.interrupt_flags[computation_id] = True
        logger.info(f"Interrupt flag set for computation: {computation_id}")
    
    def check_interrupt(self, computation_id: str) -> bool:
        """Check if computation should be interrupted"""
        return self.interrupt_flags.get(computation_id, False)
    
    def clear_interrupt_flag(self, computation_id: str):
        """Clear interrupt flag for a computation"""
        self.interrupt_flags.pop(computation_id, None)
    
    def progressive_gp_fitting(
        self,
        models: List[Any],
        computation_id: str,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ) -> List[Any]:
        """
        Fit GP models progressively with interruption support
        
        Args:
            models: List of models to fit
            computation_id: Unique ID for this computation
            progress_callback: Optional progress callback
            
        Returns:
            List of fitted models
        """
        fitted_models = []
        start_time = time.time()
        total_models = len(models)
        
        for i, model in enumerate(models):
            # Check for interruption
            if self.check_interrupt(computation_id):
                logger.info(f"Computation {computation_id} interrupted at model {i}")
                break
            
            # Fit model
            try:
                from botorch.fit import fit_gpytorch_mll
                from gpytorch.mlls import ExactMarginalLogLikelihood
                
                mll = ExactMarginalLogLikelihood(model.likelihood, model)
                fit_gpytorch_mll(mll)
                fitted_models.append(model)
                
                # Create checkpoint
                self.create_checkpoint(computation_id, {
                    'fitted_models': fitted_models,
                    'current_index': i + 1
                })
                
                # Update progress
                if progress_callback:
                    elapsed = time.time() - start_time
                    progress = ProgressUpdate(
                        current=i + 1,
                        total=total_models,
                        stage="fitting_models",
                        message=f"Fitted model {i + 1}/{total_models}",
                        percentage=((i + 1) / total_models) * 100,
                        elapsed_time=elapsed
                    )
                    progress_callback(progress)
                
            except Exception as e:
                logger.error(f"Error fitting model {i}: {e}")
                continue
        
        # Clear interrupt flag and checkpoint
        self.clear_interrupt_flag(computation_id)
        self.checkpoints.pop(computation_id, None)
        
        return fitted_models

# Global instances
async_optimizer = AsyncOptimizer()
background_manager = BackgroundTaskManager()
progressive_computer = ProgressiveComputation()
chunked_processor = ChunkedProcessor()

# Utility functions for easy integration
def make_async(func: Callable, *args, **kwargs) -> asyncio.Future:
    """Make any function asynchronous"""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, func, *args, **kwargs)

def run_with_progress(
    func: Callable,
    progress_callback: Callable[[ProgressUpdate], None],
    *args,
    **kwargs
) -> Any:
    """Run function with progress updates"""
    start_time = time.time()
    
    # Initial progress
    progress = ProgressUpdate(
        current=0,
        total=100,
        stage="starting",
        message="Initializing...",
        percentage=0.0,
        elapsed_time=0.0
    )
    progress_callback(progress)
    
    try:
        result = func(*args, **kwargs)
        
        # Final progress
        elapsed = time.time() - start_time
        progress = ProgressUpdate(
            current=100,
            total=100,
            stage="completed",
            message="Operation completed",
            percentage=100.0,
            elapsed_time=elapsed
        )
        progress_callback(progress)
        
        return result
        
    except Exception as e:
        elapsed = time.time() - start_time
        progress = ProgressUpdate(
            current=0,
            total=100,
            stage="error",
            message=f"Error: {str(e)}",
            percentage=0.0,
            elapsed_time=elapsed
        )
        progress_callback(progress)
        raise

import os  # Add missing import

__all__ = [
    'AsyncOptimizer', 'ChunkedProcessor', 'BackgroundTaskManager',
    'ProgressiveComputation', 'ProgressUpdate', 'async_wrapper',
    'async_optimizer', 'background_manager', 'progressive_computer',
    'chunked_processor', 'make_async', 'run_with_progress'
]