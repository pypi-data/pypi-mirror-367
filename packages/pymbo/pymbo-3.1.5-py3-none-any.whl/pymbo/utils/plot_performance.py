"""
Advanced Plot Performance Optimization Module for PyMBO
Provides comprehensive performance enhancements for plotting and visualization
"""

import time
import hashlib
import threading
import weakref
from functools import wraps, lru_cache
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
import logging
import gc
import numpy as np
import pandas as pd
import torch
from dataclasses import dataclass, field
from collections import defaultdict, deque
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import seaborn as sns

# Try to import optional performance libraries
try:
    import matplotlib.pyplot as plt
    from matplotlib import patheffects
    from matplotlib.collections import LineCollection, PolyCollection
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import datashader as ds
    import datashader.transfer_functions as tf
    DATASHADER_AVAILABLE = True
except ImportError:
    DATASHADER_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class PlotPerformanceMetrics:
    """Metrics for tracking plot performance"""
    render_time: float = 0.0
    data_prep_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    data_points: int = 0
    plot_type: str = ""
    memory_usage_mb: float = 0.0
    
    def get_cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

@dataclass
class PlotConfig:
    """Configuration for plot performance optimization"""
    enable_caching: bool = True
    enable_lazy_loading: bool = True
    enable_data_decimation: bool = True
    enable_gpu_acceleration: bool = True
    cache_size_limit: int = 100  # Number of plots to cache
    max_data_points: int = 10000  # Max points before decimation
    decimation_factor: float = 0.1  # Keep 10% of points when decimating
    update_throttle_ms: int = 50  # Minimum time between updates
    use_webgl: bool = True  # Use WebGL for interactive plots
    background_computation: bool = True  # Compute plots in background

class AdvancedPlotCache:
    """Advanced caching system for plot data and rendered plots"""
    
    def __init__(self, max_size: int = 100, memory_limit_mb: int = 500):
        self.max_size = max_size
        self.memory_limit_mb = memory_limit_mb
        self.cache = {}
        self.metadata = {}
        self.access_times = {}
        self.render_cache = {}  # Cache for rendered plot objects
        self.data_cache = {}    # Cache for processed plot data
        self.memory_usage = 0
        self._lock = threading.Lock()
        self.metrics = defaultdict(PlotPerformanceMetrics)
        
    def _generate_cache_key(self, plot_type: str, data_hash: str, 
                          params: Dict, style_hash: str = "") -> str:
        """Generate comprehensive cache key"""
        param_str = str(sorted(params.items())) if params else ""
        full_key = f"{plot_type}_{data_hash}_{style_hash}_{hashlib.md5(param_str.encode()).hexdigest()[:8]}"
        return full_key
    
    def _estimate_memory_usage(self, data: Any) -> float:
        """Estimate memory usage of cached data in MB"""
        try:
            if isinstance(data, np.ndarray):
                return data.nbytes / 1024 / 1024
            elif isinstance(data, pd.DataFrame):
                return data.memory_usage(deep=True).sum() / 1024 / 1024
            elif isinstance(data, torch.Tensor):
                return data.element_size() * data.nelement() / 1024 / 1024
            elif isinstance(data, Figure):
                # Rough estimate for matplotlib figures
                return 5.0  # MB per figure
            else:
                # Rough estimate for other objects
                return 1.0
        except:
            return 1.0
    
    def get(self, plot_type: str, data_hash: str, params: Dict = None, 
            style_hash: str = "") -> Optional[Any]:
        """Get cached plot with LRU eviction"""
        with self._lock:
            key = self._generate_cache_key(plot_type, data_hash, params, style_hash)
            
            if key in self.cache:
                self.access_times[key] = time.time()
                self.metrics[plot_type].cache_hits += 1
                logger.debug(f"Plot cache hit: {plot_type}")
                return self.cache[key]
            
            self.metrics[plot_type].cache_misses += 1
            logger.debug(f"Plot cache miss: {plot_type}")
            return None
    
    def set(self, plot_type: str, data_hash: str, data: Any, 
            params: Dict = None, style_hash: str = ""):
        """Cache plot data with memory management"""
        with self._lock:
            key = self._generate_cache_key(plot_type, data_hash, params, style_hash)
            
            # Estimate memory usage
            memory_usage = self._estimate_memory_usage(data)
            
            # Check if we need to evict entries
            while (len(self.cache) >= self.max_size or 
                   self.memory_usage + memory_usage > self.memory_limit_mb):
                if not self.cache:
                    break
                self._evict_oldest()
            
            # Cache the data
            self.cache[key] = data
            self.metadata[key] = {
                'plot_type': plot_type,
                'memory_mb': memory_usage,
                'created_at': time.time()
            }
            self.access_times[key] = time.time()
            self.memory_usage += memory_usage
            
            logger.debug(f"Cached plot: {plot_type}, Memory: {memory_usage:.2f}MB")
    
    def _evict_oldest(self):
        """Evict least recently used cache entry"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        
        # Remove from all caches
        self.cache.pop(oldest_key, None)
        memory_freed = self.metadata.pop(oldest_key, {}).get('memory_mb', 0)
        self.access_times.pop(oldest_key, None)
        self.memory_usage -= memory_freed
        
        logger.debug(f"Evicted cache entry: {oldest_key}, Freed: {memory_freed:.2f}MB")
    
    def clear(self):
        """Clear all caches"""
        with self._lock:
            self.cache.clear()
            self.metadata.clear()
            self.access_times.clear()
            self.render_cache.clear()
            self.data_cache.clear()
            self.memory_usage = 0
            logger.info("Plot cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_hits = sum(m.cache_hits for m in self.metrics.values())
            total_misses = sum(m.cache_misses for m in self.metrics.values())
            
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage_mb': self.memory_usage,
                'memory_limit_mb': self.memory_limit_mb,
                'total_hits': total_hits,
                'total_misses': total_misses,
                'hit_rate': total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0,
                'plot_types': list(self.metrics.keys())
            }

class DataDecimationEngine:
    """Intelligent data decimation for large datasets"""
    
    @staticmethod
    def decimate_scatter_data(x: np.ndarray, y: np.ndarray, 
                            max_points: int = 10000, 
                            method: str = "uniform") -> Tuple[np.ndarray, np.ndarray]:
        """Decimate scatter plot data intelligently"""
        if len(x) <= max_points:
            return x, y
        
        if method == "uniform":
            # Uniform sampling
            indices = np.linspace(0, len(x) - 1, max_points, dtype=int)
            return x[indices], y[indices]
        
        elif method == "importance":
            # Importance-based sampling (keep outliers and interesting points)
            try:
                # Calculate point importance based on local density
                from scipy.spatial.distance import pdist, squareform
                
                # Sample a subset for distance calculation if too large
                sample_size = min(1000, len(x))
                sample_indices = np.random.choice(len(x), sample_size, replace=False)
                
                points = np.column_stack([x[sample_indices], y[sample_indices]])
                distances = squareform(pdist(points))
                
                # Calculate average distance to neighbors (inverse = importance)
                importance = 1.0 / (np.mean(distances, axis=1) + 1e-8)
                
                # Select high-importance points
                important_indices = sample_indices[np.argsort(importance)[-max_points:]]
                return x[important_indices], y[important_indices]
                
            except ImportError:
                # Fallback to uniform if scipy not available
                return DataDecimationEngine.decimate_scatter_data(x, y, max_points, "uniform")
        
        elif method == "adaptive":
            # Adaptive decimation based on data density
            try:
                # Use histogram-based decimation
                hist, x_edges, y_edges = np.histogram2d(x, y, bins=50)
                
                # Find high-density regions
                high_density = hist > np.percentile(hist, 75)
                
                # Sample more from low-density regions, less from high-density
                decimated_x, decimated_y = [], []
                
                for i in range(len(x_edges) - 1):
                    for j in range(len(y_edges) - 1):
                        mask = ((x >= x_edges[i]) & (x < x_edges[i+1]) & 
                               (y >= y_edges[j]) & (y < y_edges[j+1]))
                        
                        points_in_bin = np.sum(mask)
                        if points_in_bin == 0:
                            continue
                        
                        # Adaptive sampling rate
                        if high_density[i, j]:
                            sample_rate = max(0.01, max_points / (len(x) * 4))
                        else:
                            sample_rate = max(0.1, max_points / len(x))
                        
                        n_samples = max(1, int(points_in_bin * sample_rate))
                        indices = np.where(mask)[0]
                        
                        if len(indices) > n_samples:
                            selected = np.random.choice(indices, n_samples, replace=False)
                        else:
                            selected = indices
                        
                        decimated_x.extend(x[selected])
                        decimated_y.extend(y[selected])
                
                return np.array(decimated_x), np.array(decimated_y)
                
            except Exception:
                # Fallback to uniform
                return DataDecimationEngine.decimate_scatter_data(x, y, max_points, "uniform")
    
    @staticmethod
    def decimate_line_data(x: np.ndarray, y: np.ndarray, 
                          max_points: int = 10000, 
                          preserve_peaks: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Decimate line plot data while preserving important features"""
        if len(x) <= max_points:
            return x, y
        
        if preserve_peaks:
            try:
                # Find local maxima and minima
                from scipy.signal import find_peaks
                
                peaks_max, _ = find_peaks(y)
                peaks_min, _ = find_peaks(-y)
                important_indices = np.concatenate([peaks_max, peaks_min])
                
                # Add start and end points
                important_indices = np.concatenate([[0], important_indices, [len(x) - 1]])
                important_indices = np.unique(important_indices)
                
                # Ensure we don't exceed max_points
                if len(important_indices) > max_points:
                    # Too many important points, just take a subset
                    important_indices = important_indices[:max_points]
                    return x[important_indices], y[important_indices]
                
                # If we have space for more points, sample the rest uniformly
                remaining_points = max_points - len(important_indices)
                if remaining_points > 0:
                    # Get remaining indices
                    all_indices = np.arange(len(x))
                    remaining_indices = np.setdiff1d(all_indices, important_indices)
                    
                    if len(remaining_indices) > remaining_points:
                        sampled_remaining = np.random.choice(
                            remaining_indices, remaining_points, replace=False
                        )
                        final_indices = np.concatenate([important_indices, sampled_remaining])
                    else:
                        final_indices = np.concatenate([important_indices, remaining_indices])
                    
                    final_indices = np.sort(final_indices)
                    # Ensure we don't exceed max_points
                    final_indices = final_indices[:max_points]
                    return x[final_indices], y[final_indices]
                else:
                    # Use only important points
                    return x[important_indices], y[important_indices]
                    
            except ImportError:
                # Fallback to uniform sampling
                pass
        
        # Uniform sampling fallback
        indices = np.linspace(0, len(x) - 1, max_points, dtype=int)
        return x[indices], y[indices]

class GPUAcceleratedPlotting:
    """GPU-accelerated plotting operations"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_available = torch.cuda.is_available()
        
    def accelerated_histogram(self, data: np.ndarray, bins: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """GPU-accelerated histogram computation"""
        if not self.gpu_available:
            return np.histogram(data, bins=bins)
        
        try:
            # Convert to tensor and move to GPU
            data_tensor = torch.from_numpy(data).to(self.device)
            
            # Compute histogram on GPU
            hist = torch.histc(data_tensor, bins=bins)
            
            # Create bin edges
            data_min, data_max = torch.min(data_tensor), torch.max(data_tensor)
            bin_edges = torch.linspace(data_min, data_max, bins + 1)
            
            # Move back to CPU and convert to numpy
            return hist.cpu().numpy(), bin_edges.cpu().numpy()
            
        except Exception as e:
            logger.debug(f"GPU histogram failed, using CPU: {e}")
            return np.histogram(data, bins=bins)
    
    def accelerated_correlation_matrix(self, data: np.ndarray) -> np.ndarray:
        """GPU-accelerated correlation matrix computation"""
        if not self.gpu_available:
            return np.corrcoef(data.T)
        
        try:
            # Convert to tensor and move to GPU
            data_tensor = torch.from_numpy(data).to(self.device)
            
            # Compute correlation matrix on GPU
            corr_matrix = torch.corrcoef(data_tensor.T)
            
            return corr_matrix.cpu().numpy()
            
        except Exception as e:
            logger.debug(f"GPU correlation failed, using CPU: {e}")
            return np.corrcoef(data.T)
    
    def accelerated_contour_data(self, X: np.ndarray, Y: np.ndarray, 
                                Z: np.ndarray, levels: int = 20) -> Dict[str, np.ndarray]:
        """GPU-accelerated contour data preparation"""
        if not self.gpu_available:
            return {"X": X, "Y": Y, "Z": Z}
        
        try:
            # Move data to GPU
            X_tensor = torch.from_numpy(X).to(self.device)
            Y_tensor = torch.from_numpy(Y).to(self.device)
            Z_tensor = torch.from_numpy(Z).to(self.device)
            
            # Perform GPU operations (smoothing, interpolation, etc.)
            # This is a placeholder - actual implementation would depend on specific needs
            
            return {
                "X": X_tensor.cpu().numpy(),
                "Y": Y_tensor.cpu().numpy(), 
                "Z": Z_tensor.cpu().numpy()
            }
            
        except Exception as e:
            logger.debug(f"GPU contour processing failed, using CPU: {e}")
            return {"X": X, "Y": Y, "Z": Z}

class IncrementalPlotUpdater:
    """Manages incremental plot updates for better performance"""
    
    def __init__(self):
        self.plot_states = {}
        self.update_queue = deque(maxlen=1000)
        self.last_update_times = {}
        self.throttle_interval = 0.05  # 50ms minimum between updates
        
    def register_plot(self, plot_id: str, plot_type: str, initial_data: Any):
        """Register a plot for incremental updates"""
        self.plot_states[plot_id] = {
            'type': plot_type,
            'data': initial_data,
            'last_update': time.time(),
            'version': 0
        }
    
    def queue_update(self, plot_id: str, new_data: Any, update_type: str = "append"):
        """Queue an incremental update"""
        self.update_queue.append({
            'plot_id': plot_id,
            'data': new_data,
            'type': update_type,
            'timestamp': time.time()
        })
    
    def should_update(self, plot_id: str) -> bool:
        """Check if plot should be updated based on throttling"""
        last_update = self.last_update_times.get(plot_id, 0)
        return time.time() - last_update >= self.throttle_interval
    
    def process_updates(self) -> List[Dict[str, Any]]:
        """Process queued updates and return list of plots to update"""
        updates_to_process = []
        
        while self.update_queue:
            update = self.update_queue.popleft()
            plot_id = update['plot_id']
            
            if self.should_update(plot_id):
                updates_to_process.append(update)
                self.last_update_times[plot_id] = time.time()
        
        return updates_to_process

class LazyPlotLoader:
    """Lazy loading system for plots and plot data"""
    
    def __init__(self):
        self.plot_loaders = {}
        self.loaded_plots = {}
        self.viewport_cache = {}
        
    def register_lazy_plot(self, plot_id: str, loader_func: Callable, 
                          viewport_bounds: Optional[Tuple] = None):
        """Register a plot for lazy loading"""
        self.plot_loaders[plot_id] = {
            'loader': loader_func,
            'viewport': viewport_bounds,
            'loaded': False
        }
    
    def load_plot_in_viewport(self, plot_id: str, viewport: Tuple[float, float, float, float]):
        """Load plot data only for the current viewport"""
        if plot_id not in self.plot_loaders:
            return None
        
        # Check if we already have data for this viewport
        viewport_key = f"{plot_id}_{viewport}"
        if viewport_key in self.viewport_cache:
            return self.viewport_cache[viewport_key]
        
        # Load data for viewport
        loader = self.plot_loaders[plot_id]['loader']
        try:
            plot_data = loader(viewport=viewport)
            self.viewport_cache[viewport_key] = plot_data
            return plot_data
        except Exception as e:
            logger.error(f"Failed to load plot {plot_id}: {e}")
            return None

def plot_performance_timer(func):
    """Decorator to time plot operations"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            # Log slow plots
            if duration > 0.5:  # Log plots taking more than 500ms
                logger.warning(f"Slow plot operation: {func.__name__} took {duration:.3f}s")
            else:
                logger.debug(f"Plot operation: {func.__name__} took {duration:.3f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Plot operation failed: {func.__name__} after {duration:.3f}s - {e}")
            raise
    
    return wrapper

class PlotPerformanceOptimizer:
    """Main class coordinating all plot performance optimizations"""
    
    def __init__(self, config: Optional[PlotConfig] = None):
        self.config = config or PlotConfig()
        self.cache = AdvancedPlotCache(
            max_size=self.config.cache_size_limit,
            memory_limit_mb=500
        )
        self.decimation_engine = DataDecimationEngine()
        self.gpu_plotter = GPUAcceleratedPlotting()
        self.incremental_updater = IncrementalPlotUpdater()
        self.lazy_loader = LazyPlotLoader()
        
        # Performance tracking
        self.plot_metrics = defaultdict(PlotPerformanceMetrics)
        self.total_plots_generated = 0
        self.total_time_saved = 0.0
        
        logger.info(f"PlotPerformanceOptimizer initialized with config: {self.config}")
    
    def get_data_hash(self, data: Any) -> str:
        """Generate hash for data caching"""
        try:
            if isinstance(data, pd.DataFrame):
                return hashlib.md5(pd.util.hash_pandas_object(data).values.tobytes()).hexdigest()[:16]
            elif isinstance(data, np.ndarray):
                return hashlib.md5(data.tobytes()).hexdigest()[:16]
            elif isinstance(data, torch.Tensor):
                return hashlib.md5(data.cpu().numpy().tobytes()).hexdigest()[:16]
            else:
                return hashlib.md5(str(data).encode()).hexdigest()[:16]
        except Exception:
            return hashlib.md5(str(data).encode()).hexdigest()[:16]
    
    @plot_performance_timer
    def optimize_plot_data(self, plot_type: str, data: Dict[str, Any], 
                          params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize plot data before rendering"""
        start_time = time.time()
        
        # Check cache first
        if self.config.enable_caching:
            data_hash = self.get_data_hash(data)
            cached_result = self.cache.get(plot_type, data_hash, params)
            if cached_result is not None:
                return cached_result
        
        optimized_data = data.copy()
        
        # Apply data decimation if needed
        if self.config.enable_data_decimation:
            optimized_data = self._apply_data_decimation(plot_type, optimized_data)
        
        # Apply GPU acceleration if available
        if self.config.enable_gpu_acceleration and self.gpu_plotter.gpu_available:
            optimized_data = self._apply_gpu_acceleration(plot_type, optimized_data)
        
        # Cache the result
        if self.config.enable_caching:
            self.cache.set(plot_type, data_hash, optimized_data, params)
        
        # Update metrics
        processing_time = time.time() - start_time
        metrics = self.plot_metrics[plot_type]
        metrics.data_prep_time += processing_time
        metrics.data_points = self._count_data_points(optimized_data)
        
        return optimized_data
    
    def _apply_data_decimation(self, plot_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply intelligent data decimation"""
        if plot_type in ['scatter', 'scatter_plot', 'pareto_plot']:
            for x_key, y_key in [('x', 'y'), ('all_x', 'all_y'), ('pareto_x', 'pareto_y')]:
                if x_key in data and y_key in data:
                    x, y = np.array(data[x_key]), np.array(data[y_key])
                    if len(x) > self.config.max_data_points:
                        x_dec, y_dec = self.decimation_engine.decimate_scatter_data(
                            x, y, self.config.max_data_points, method="uniform"  # Use uniform for reliability
                        )
                        data[x_key], data[y_key] = x_dec.tolist(), y_dec.tolist()
        
        elif plot_type in ['line', 'line_plot', 'progress_plot']:
            if 'x' in data and 'y' in data:
                x, y = np.array(data['x']), np.array(data['y'])
                if len(x) > self.config.max_data_points:
                    x_dec, y_dec = self.decimation_engine.decimate_line_data(
                        x, y, self.config.max_data_points, preserve_peaks=False  # Disable peak preservation for reliability
                    )
                    data['x'], data['y'] = x_dec.tolist(), y_dec.tolist()
        
        elif plot_type == 'histogram':
            if 'values' in data:
                values = np.array(data['values'])
                if len(values) > self.config.max_data_points * 10:  # Histograms can handle more data
                    # Sample the data for histogram
                    sampled = np.random.choice(
                        values, 
                        size=self.config.max_data_points * 10, 
                        replace=False
                    )
                    data['values'] = sampled.tolist()
        
        return data
    
    def _apply_gpu_acceleration(self, plot_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply GPU acceleration where possible"""
        try:
            if plot_type == 'histogram' and 'values' in data:
                values = np.array(data['values'])
                hist, bin_edges = self.gpu_plotter.accelerated_histogram(values)
                data['hist'] = hist
                data['bin_edges'] = bin_edges
            
            elif plot_type == 'correlation_matrix' and 'matrix_data' in data:
                matrix_data = np.array(data['matrix_data'])
                corr_matrix = self.gpu_plotter.accelerated_correlation_matrix(matrix_data)
                data['correlation_matrix'] = corr_matrix
            
            elif plot_type == 'contour' and all(k in data for k in ['X', 'Y', 'Z']):
                X, Y, Z = np.array(data['X']), np.array(data['Y']), np.array(data['Z'])
                contour_data = self.gpu_plotter.accelerated_contour_data(X, Y, Z)
                data.update(contour_data)
        
        except Exception as e:
            logger.debug(f"GPU acceleration failed for {plot_type}: {e}")
        
        return data
    
    def _count_data_points(self, data: Dict[str, Any]) -> int:
        """Count total data points in plot data"""
        total = 0
        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)):
                total += len(value)
            elif isinstance(value, pd.DataFrame):
                total += len(value)
        return total
    
    def clear_cache(self):
        """Clear all caches"""
        self.cache.clear()
        logger.info("Plot performance cache cleared")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_stats = self.cache.get_stats()
        
        total_data_prep_time = sum(m.data_prep_time for m in self.plot_metrics.values())
        total_render_time = sum(m.render_time for m in self.plot_metrics.values())
        total_data_points = sum(m.data_points for m in self.plot_metrics.values())
        
        return {
            'cache_performance': cache_stats,
            'total_plots_generated': self.total_plots_generated,
            'total_data_prep_time': total_data_prep_time,
            'total_render_time': total_render_time,
            'total_data_points': total_data_points,
            'avg_data_prep_time': total_data_prep_time / max(1, self.total_plots_generated),
            'avg_render_time': total_render_time / max(1, self.total_plots_generated),
            'time_saved_from_caching': self.total_time_saved,
            'gpu_acceleration_available': self.gpu_plotter.gpu_available,
            'plot_types_processed': list(self.plot_metrics.keys()),
            'config': {
                'enable_caching': self.config.enable_caching,
                'enable_data_decimation': self.config.enable_data_decimation,
                'enable_gpu_acceleration': self.config.enable_gpu_acceleration,
                'max_data_points': self.config.max_data_points
            }
        }

# Global instance for easy access
plot_performance_optimizer = PlotPerformanceOptimizer()

# Export main classes and functions
__all__ = [
    'PlotPerformanceOptimizer', 'PlotConfig', 'AdvancedPlotCache',
    'DataDecimationEngine', 'GPUAcceleratedPlotting', 'IncrementalPlotUpdater',
    'LazyPlotLoader', 'plot_performance_timer', 'plot_performance_optimizer'
]