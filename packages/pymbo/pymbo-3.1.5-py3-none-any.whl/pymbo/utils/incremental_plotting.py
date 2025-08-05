"""
Incremental and Differential Plotting System for PyMBO
Provides efficient updates for plots without full re-rendering
"""

import time
import logging
import threading
from typing import Any, Dict, List, Optional, Tuple, Callable, Union, Set
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.collections import LineCollection
from matplotlib.artist import Artist
import weakref
from dataclasses import dataclass, field
from collections import deque, defaultdict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class PlotUpdate:
    """Represents a plot update operation"""
    plot_id: str
    update_type: str  # 'add', 'remove', 'modify', 'style'
    data: Any
    timestamp: float = field(default_factory=time.time)
    priority: int = 1  # Lower numbers = higher priority
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PlotState:
    """Tracks the current state of a plot"""
    plot_id: str
    plot_type: str
    data_hash: str
    last_update: float
    artists: List[Artist] = field(default_factory=list)
    data_bounds: Optional[Tuple[float, float, float, float]] = None
    element_count: int = 0
    needs_full_redraw: bool = False

class DifferentialRenderer(ABC):
    """Abstract base class for differential rendering strategies"""
    
    @abstractmethod
    def can_handle(self, plot_type: str) -> bool:
        """Check if this renderer can handle the given plot type"""
        pass
    
    @abstractmethod
    def apply_update(self, ax, plot_state: PlotState, update: PlotUpdate) -> bool:
        """Apply an incremental update to the plot"""
        pass
    
    @abstractmethod
    def should_full_redraw(self, plot_state: PlotState, updates: List[PlotUpdate]) -> bool:
        """Determine if a full redraw is needed"""
        pass

class ScatterDifferentialRenderer(DifferentialRenderer):
    """Differential renderer for scatter plots"""
    
    def can_handle(self, plot_type: str) -> bool:
        return plot_type in ['scatter', 'scatter_plot', 'pareto_plot']
    
    def apply_update(self, ax, plot_state: PlotState, update: PlotUpdate) -> bool:
        """Apply incremental update to scatter plot"""
        try:
            if update.update_type == 'add':
                # Add new points to existing scatter plot
                new_data = update.data
                if 'x' in new_data and 'y' in new_data:
                    x_new = np.array(new_data['x'])
                    y_new = np.array(new_data['y'])
                    
                    # Add scatter points
                    color = new_data.get('color', 'blue')
                    size = new_data.get('size', 50)
                    alpha = new_data.get('alpha', 0.6)
                    
                    new_scatter = ax.scatter(x_new, y_new, c=color, s=size, alpha=alpha)
                    plot_state.artists.append(new_scatter)
                    plot_state.element_count += len(x_new)
                    
                    # Update bounds
                    self._update_bounds(plot_state, x_new, y_new)
                    
                    return True
            
            elif update.update_type == 'remove':
                # Remove specific points (if we have artist references)
                indices_to_remove = update.data.get('indices', [])
                if indices_to_remove and plot_state.artists:
                    # This is complex for scatter plots - might need full redraw
                    plot_state.needs_full_redraw = True
                    return False
            
            elif update.update_type == 'style':
                # Update styling of existing points
                style_data = update.data
                for artist in plot_state.artists:
                    if hasattr(artist, 'set_color') and 'color' in style_data:
                        artist.set_color(style_data['color'])
                    if hasattr(artist, 'set_alpha') and 'alpha' in style_data:
                        artist.set_alpha(style_data['alpha'])
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying scatter update: {e}")
            return False
    
    def should_full_redraw(self, plot_state: PlotState, updates: List[PlotUpdate]) -> bool:
        """Determine if scatter plot needs full redraw"""
        # Full redraw if too many updates or complex operations
        if len(updates) > 10:
            return True
        
        # Full redraw if bounds changed significantly
        if plot_state.data_bounds and any(update.update_type == 'add' for update in updates):
            return plot_state.element_count > 1000  # Threshold for performance
        
        # Full redraw if remove operations
        if any(update.update_type == 'remove' for update in updates):
            return True
        
        return plot_state.needs_full_redraw
    
    def _update_bounds(self, plot_state: PlotState, x_new: np.ndarray, y_new: np.ndarray):
        """Update plot bounds with new data"""
        x_min, x_max = np.min(x_new), np.max(x_new)
        y_min, y_max = np.min(y_new), np.max(y_new)
        
        if plot_state.data_bounds is None:
            plot_state.data_bounds = (x_min, x_max, y_min, y_max)
        else:
            old_x_min, old_x_max, old_y_min, old_y_max = plot_state.data_bounds
            plot_state.data_bounds = (
                min(old_x_min, x_min), max(old_x_max, x_max),
                min(old_y_min, y_min), max(old_y_max, y_max)
            )

class LineDifferentialRenderer(DifferentialRenderer):
    """Differential renderer for line plots"""
    
    def can_handle(self, plot_type: str) -> bool:
        return plot_type in ['line', 'line_plot', 'progress_plot']
    
    def apply_update(self, ax, plot_state: PlotState, update: PlotUpdate) -> bool:
        """Apply incremental update to line plot"""
        try:
            if update.update_type == 'add':
                # Extend existing line data
                new_data = update.data
                if 'x' in new_data and 'y' in new_data:
                    x_new = np.array(new_data['x'])
                    y_new = np.array(new_data['y'])
                    
                    # Find existing line artist
                    line_artist = None
                    for artist in plot_state.artists:
                        if hasattr(artist, 'get_xdata'):
                            line_artist = artist
                            break
                    
                    if line_artist:
                        # Extend existing line
                        old_x = line_artist.get_xdata()
                        old_y = line_artist.get_ydata()
                        
                        new_x_data = np.concatenate([old_x, x_new])
                        new_y_data = np.concatenate([old_y, y_new])
                        
                        line_artist.set_data(new_x_data, new_y_data)
                        
                        # Update bounds
                        self._update_bounds(plot_state, x_new, y_new)
                        
                        # Update axis limits if needed
                        ax.relim()
                        ax.autoscale_view()
                        
                        return True
                    else:
                        # Create new line
                        color = new_data.get('color', 'blue')
                        linewidth = new_data.get('linewidth', 2)
                        alpha = new_data.get('alpha', 1.0)
                        
                        new_line, = ax.plot(x_new, y_new, color=color, 
                                          linewidth=linewidth, alpha=alpha)
                        plot_state.artists.append(new_line)
                        
                        self._update_bounds(plot_state, x_new, y_new)
                        return True
            
            elif update.update_type == 'modify':
                # Modify existing line data
                modify_data = update.data
                if 'index' in modify_data and 'value' in modify_data:
                    # Modify specific point
                    for artist in plot_state.artists:
                        if hasattr(artist, 'get_ydata'):
                            y_data = list(artist.get_ydata())
                            index = modify_data['index']
                            if 0 <= index < len(y_data):
                                y_data[index] = modify_data['value']
                                artist.set_ydata(y_data)
                                return True
            
            elif update.update_type == 'style':
                # Update line styling
                style_data = update.data
                for artist in plot_state.artists:
                    if hasattr(artist, 'set_color') and 'color' in style_data:
                        artist.set_color(style_data['color'])
                    if hasattr(artist, 'set_linewidth') and 'linewidth' in style_data:
                        artist.set_linewidth(style_data['linewidth'])
                    if hasattr(artist, 'set_alpha') and 'alpha' in style_data:
                        artist.set_alpha(style_data['alpha'])
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error applying line update: {e}")
            return False
    
    def should_full_redraw(self, plot_state: PlotState, updates: List[PlotUpdate]) -> bool:
        """Determine if line plot needs full redraw"""
        # Full redraw if too many updates
        if len(updates) > 20:
            return True
        
        # Full redraw if complex modifications
        if any(update.update_type == 'remove' for update in updates):
            return True
        
        return plot_state.needs_full_redraw
    
    def _update_bounds(self, plot_state: PlotState, x_new: np.ndarray, y_new: np.ndarray):
        """Update plot bounds with new data"""
        x_min, x_max = np.min(x_new), np.max(x_new)
        y_min, y_max = np.min(y_new), np.max(y_new)
        
        if plot_state.data_bounds is None:
            plot_state.data_bounds = (x_min, x_max, y_min, y_max)
        else:
            old_x_min, old_x_max, old_y_min, old_y_max = plot_state.data_bounds
            plot_state.data_bounds = (
                min(old_x_min, x_min), max(old_x_max, x_max),
                min(old_y_min, y_min), max(old_y_max, y_max)
            )

class IncrementalPlotManager:
    """Manages incremental plot updates across multiple plots"""
    
    def __init__(self, max_update_queue_size: int = 1000, 
                 update_batch_size: int = 10,
                 throttle_interval: float = 0.05):
        self.max_queue_size = max_update_queue_size
        self.batch_size = update_batch_size
        self.throttle_interval = throttle_interval
        
        # Data structures
        self.plot_states: Dict[str, PlotState] = {}
        self.update_queue = deque(maxlen=max_update_queue_size)
        self.last_update_times: Dict[str, float] = {}
        self.pending_updates: Dict[str, List[PlotUpdate]] = defaultdict(list)
        
        # Renderers
        self.renderers: List[DifferentialRenderer] = [
            ScatterDifferentialRenderer(),
            LineDifferentialRenderer()
        ]
        
        # Threading
        self._lock = threading.Lock()
        self.update_thread = None
        self.running = False
        
        # Metrics
        self.total_updates_applied = 0
        self.total_full_redraws = 0
        self.time_saved = 0.0
        
        logger.info("IncrementalPlotManager initialized")
    
    def register_plot(self, plot_id: str, plot_type: str, ax, initial_data_hash: str = ""):
        """Register a plot for incremental updates"""
        with self._lock:
            plot_state = PlotState(
                plot_id=plot_id,
                plot_type=plot_type,
                data_hash=initial_data_hash,
                last_update=time.time(),
                artists=list(ax.get_children())  # Store initial artists
            )
            self.plot_states[plot_id] = plot_state
            logger.debug(f"Registered plot: {plot_id} ({plot_type})")
    
    def queue_update(self, plot_id: str, update_type: str, data: Any, 
                    priority: int = 1, metadata: Dict[str, Any] = None):
        """Queue an update for a plot"""
        update = PlotUpdate(
            plot_id=plot_id,
            update_type=update_type,
            data=data,
            priority=priority,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.update_queue.append(update)
            logger.debug(f"Queued update for plot {plot_id}: {update_type}")
    
    def process_updates(self, canvas_dict: Dict[str, Any]) -> Dict[str, bool]:
        """Process all queued updates and return which plots were updated"""
        updated_plots = {}
        
        with self._lock:
            # Group updates by plot_id
            updates_by_plot = defaultdict(list)
            
            # Process queue
            while self.update_queue:
                update = self.update_queue.popleft()
                
                # Check throttling
                if self._should_throttle_update(update.plot_id):
                    # Re-queue for later
                    self.update_queue.append(update)
                    continue
                
                updates_by_plot[update.plot_id].append(update)
        
        # Process updates for each plot
        for plot_id, updates in updates_by_plot.items():
            if plot_id not in self.plot_states:
                continue
            
            plot_state = self.plot_states[plot_id]
            
            # Get appropriate renderer
            renderer = self._get_renderer(plot_state.plot_type)
            if not renderer:
                logger.warning(f"No renderer available for plot type: {plot_state.plot_type}")
                updated_plots[plot_id] = False
                continue
            
            # Get canvas and ax
            canvas = canvas_dict.get(plot_id)
            if not canvas or not hasattr(canvas, 'figure'):
                continue
            
            fig = canvas.figure
            if not fig.axes:
                continue
            
            ax = fig.axes[0]  # Assume first axis
            
            # Determine if full redraw is needed
            if renderer.should_full_redraw(plot_state, updates):
                # Full redraw needed
                self.total_full_redraws += 1
                updated_plots[plot_id] = False  # Indicate full redraw needed
                logger.debug(f"Full redraw needed for plot {plot_id}")
            else:
                # Apply incremental updates
                success = True
                start_time = time.time()
                
                for update in updates:
                    if not renderer.apply_update(ax, plot_state, update):
                        success = False
                        break
                
                if success:
                    # Update successful
                    plot_state.last_update = time.time()
                    self.last_update_times[plot_id] = plot_state.last_update
                    self.total_updates_applied += len(updates)
                    self.time_saved += max(0.1 - (time.time() - start_time), 0)  # Estimate time saved vs full redraw
                    
                    # Redraw canvas
                    canvas.draw_idle()
                    updated_plots[plot_id] = True
                    logger.debug(f"Applied {len(updates)} incremental updates to {plot_id}")
                else:
                    # Incremental update failed, need full redraw
                    updated_plots[plot_id] = False
                    logger.debug(f"Incremental update failed for {plot_id}, full redraw needed")
        
        return updated_plots
    
    def _should_throttle_update(self, plot_id: str) -> bool:
        """Check if update should be throttled"""
        last_update = self.last_update_times.get(plot_id, 0)
        return time.time() - last_update < self.throttle_interval
    
    def _get_renderer(self, plot_type: str) -> Optional[DifferentialRenderer]:
        """Get appropriate renderer for plot type"""
        for renderer in self.renderers:
            if renderer.can_handle(plot_type):
                return renderer
        return None
    
    def start_background_processing(self, canvas_dict: Dict[str, Any]):
        """Start background thread for processing updates"""
        if self.running:
            return
        
        self.running = True
        self.update_thread = threading.Thread(
            target=self._background_update_loop,
            args=(canvas_dict,),
            daemon=True
        )
        self.update_thread.start()
        logger.info("Started background update processing")
    
    def stop_background_processing(self):
        """Stop background update processing"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("Stopped background update processing")
    
    def _background_update_loop(self, canvas_dict: Dict[str, Any]):
        """Background loop for processing updates"""
        while self.running:
            try:
                if self.update_queue:
                    self.process_updates(canvas_dict)
                time.sleep(self.throttle_interval)
            except Exception as e:
                logger.error(f"Error in background update loop: {e}")
                time.sleep(0.1)
    
    def get_plot_state(self, plot_id: str) -> Optional[PlotState]:
        """Get current state of a plot"""
        return self.plot_states.get(plot_id)
    
    def clear_plot_state(self, plot_id: str):
        """Clear state for a plot"""
        with self._lock:
            self.plot_states.pop(plot_id, None)
            self.last_update_times.pop(plot_id, None)
            self.pending_updates.pop(plot_id, None)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self._lock:
            return {
                'total_updates_applied': self.total_updates_applied,
                'total_full_redraws': self.total_full_redraws,
                'time_saved_seconds': self.time_saved,
                'active_plots': len(self.plot_states),
                'queued_updates': len(self.update_queue),
                'update_success_rate': self.total_updates_applied / max(1, self.total_updates_applied + self.total_full_redraws),
                'throttle_interval': self.throttle_interval,
                'batch_size': self.batch_size
            }
    
    def optimize_for_performance(self):
        """Optimize settings for better performance"""
        # Adjust throttle interval based on performance
        if self.time_saved > 5.0:  # If we're saving significant time
            self.throttle_interval = max(0.01, self.throttle_interval * 0.9)  # Reduce throttling
        elif self.total_full_redraws > self.total_updates_applied:
            self.throttle_interval = min(0.1, self.throttle_interval * 1.1)  # Increase throttling
        
        logger.debug(f"Optimized throttle interval to {self.throttle_interval:.3f}s")

# Global instance for easy access
incremental_plot_manager = IncrementalPlotManager()

__all__ = [
    'IncrementalPlotManager', 'PlotUpdate', 'PlotState',
    'DifferentialRenderer', 'ScatterDifferentialRenderer', 'LineDifferentialRenderer',
    'incremental_plot_manager'
]