"""
Enhanced Plotting Manager with Performance Optimizations
Wraps the existing plotting system with comprehensive performance enhancements
"""

import time
import logging
import threading
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
from functools import wraps

# Import our performance optimization modules
from pymbo.utils.plot_performance import (
    PlotPerformanceOptimizer, PlotConfig, plot_performance_timer,
    AdvancedPlotCache, DataDecimationEngine, IncrementalPlotUpdater
)

# Import the existing plotting system
try:
    from pymbo.utils.plotting import SimplePlotManager
    ORIGINAL_PLOTTING_AVAILABLE = True
except ImportError:
    ORIGINAL_PLOTTING_AVAILABLE = False
    SimplePlotManager = None

logger = logging.getLogger(__name__)

class PerformanceEnhancedPlotManager:
    """Enhanced plot manager with comprehensive performance optimizations"""
    
    def __init__(self, optimizer, config: Optional[PlotConfig] = None):
        self.optimizer = optimizer
        self.config = config or PlotConfig()
        
        # Initialize performance components
        self.perf_optimizer = PlotPerformanceOptimizer(self.config)
        self.incremental_updater = IncrementalPlotUpdater()
        
        # Initialize the original plot manager if available
        if ORIGINAL_PLOTTING_AVAILABLE:
            self.original_plotter = SimplePlotManager(optimizer)
        else:
            self.original_plotter = None
            logger.warning("Original plotting system not available")
        
        # Performance tracking
        self.plot_call_count = 0
        self.total_time_saved = 0.0
        self.active_plots = {}
        self._lock = threading.Lock()
        
        # Set up matplotlib for better performance
        self._optimize_matplotlib_settings()
        
        logger.info("PerformanceEnhancedPlotManager initialized with optimizations enabled")
    
    def _optimize_matplotlib_settings(self):
        """Optimize matplotlib settings for better performance"""
        try:
            # Use non-interactive backend for better performance
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            
            # Optimize rendering settings
            plt.rcParams['path.simplify'] = True
            plt.rcParams['path.simplify_threshold'] = 0.1
            plt.rcParams['agg.path.chunksize'] = 10000
            
            # Disable anti-aliasing for large datasets (can be re-enabled for small plots)
            plt.rcParams['lines.antialiased'] = False
            plt.rcParams['patch.antialiased'] = False
            
            # Use faster color cycle
            plt.rcParams['axes.prop_cycle'] = plt.cycler('color', 
                ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])
            
            logger.debug("Matplotlib settings optimized for performance")
            
        except Exception as e:
            logger.warning(f"Failed to optimize matplotlib settings: {e}")
    
    def _prepare_plot_data(self, plot_type: str, data: Dict[str, Any], 
                          params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare and optimize plot data"""
        # Convert data to appropriate format
        optimized_data = {}
        
        # Handle different data types
        for key, value in data.items():
            if isinstance(value, pd.Series):
                optimized_data[key] = value.values
            elif isinstance(value, pd.DataFrame):
                if len(value.columns) == 1:
                    optimized_data[key] = value.iloc[:, 0].values
                else:
                    optimized_data[key] = value.values
            elif isinstance(value, list):
                optimized_data[key] = np.array(value)
            else:
                optimized_data[key] = value
        
        # Apply performance optimizations
        return self.perf_optimizer.optimize_plot_data(plot_type, optimized_data, params)
    
    def _should_use_fast_rendering(self, data_size: int) -> bool:
        """Determine if fast rendering mode should be used"""
        return data_size > self.config.max_data_points
    
    @plot_performance_timer
    def create_pareto_plot(self, fig, canvas, x_obj, y_obj, pareto_X_df, 
                          pareto_objectives_df, x_range=None, y_range=None):
        """Enhanced Pareto plot with performance optimizations"""
        
        with self._lock:
            self.plot_call_count += 1
        
        start_time = time.time()
        
        try:
            # Prepare data for optimization
            all_objectives_df = self._get_all_objectives_data()
            
            if all_objectives_df.empty:
                return self._create_fallback_plot(fig, canvas, "No experimental data available")
            
            # Prepare plot data
            plot_data = {
                'all_x': all_objectives_df[x_obj].values if x_obj in all_objectives_df.columns else [],
                'all_y': all_objectives_df[y_obj].values if y_obj in all_objectives_df.columns else [],
                'pareto_x': pareto_objectives_df[x_obj].values if not pareto_objectives_df.empty and x_obj in pareto_objectives_df.columns else [],
                'pareto_y': pareto_objectives_df[y_obj].values if not pareto_objectives_df.empty and y_obj in pareto_objectives_df.columns else []
            }
            
            # Optimize data
            plot_params = {'x_obj': x_obj, 'y_obj': y_obj, 'x_range': x_range, 'y_range': y_range}
            optimized_data = self._prepare_plot_data('pareto_plot', plot_data, plot_params)
            
            # Check if we should use fast rendering
            total_points = len(optimized_data.get('all_x', [])) + len(optimized_data.get('pareto_x', []))
            use_fast_rendering = self._should_use_fast_rendering(total_points)
            
            # Create the plot
            fig.clear()
            ax = fig.add_subplot(111)
            
            # Plot all points with optimization
            if len(optimized_data.get('all_x', [])) > 0:
                scatter_kwargs = {
                    'c': 'lightblue',
                    's': 20 if use_fast_rendering else 50,
                    'alpha': 0.4 if use_fast_rendering else 0.6,
                    'label': 'All Solutions',
                    'edgecolors': 'none' if use_fast_rendering else 'navy',
                    'linewidths': 0 if use_fast_rendering else 0.5,
                }
                
                ax.scatter(optimized_data['all_x'], optimized_data['all_y'], **scatter_kwargs)
            
            # Plot Pareto points with emphasis
            if len(optimized_data.get('pareto_x', [])) > 0:
                pareto_kwargs = {
                    'c': 'red',
                    's': 80 if use_fast_rendering else 100,
                    'alpha': 0.8,
                    'label': 'Pareto Front',
                    'edgecolors': 'darkred',
                    'linewidths': 1,
                    'marker': 'o',
                    'zorder': 5
                }
                
                ax.scatter(optimized_data['pareto_x'], optimized_data['pareto_y'], **pareto_kwargs)
                
                # Connect Pareto points if not too many
                if len(optimized_data['pareto_x']) <= 50:
                    # Sort by x-coordinate for line connection
                    sorted_indices = np.argsort(optimized_data['pareto_x'])
                    sorted_pareto_x = optimized_data['pareto_x'][sorted_indices]
                    sorted_pareto_y = optimized_data['pareto_y'][sorted_indices]
                    
                    ax.plot(sorted_pareto_x, sorted_pareto_y, 'r--', alpha=0.5, linewidth=1, zorder=4)
            
            # Format plot
            ax.set_xlabel(f"{x_obj}", fontsize=10)
            ax.set_ylabel(f"{y_obj}", fontsize=10)
            ax.set_title("Pareto Front Analysis", fontsize=12, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            
            # Set ranges if provided
            if x_range:
                ax.set_xlim(x_range)
            if y_range:
                ax.set_ylim(y_range)
            
            plt.tight_layout()
            canvas.draw()
            
            # Record performance metrics
            render_time = time.time() - start_time
            self.perf_optimizer.plot_metrics['pareto_plot'].render_time += render_time
            
            logger.debug(f"Pareto plot rendered in {render_time:.3f}s with {total_points} points")
            
        except Exception as e:
            logger.error(f"Error creating enhanced Pareto plot: {e}")
            # Fallback to original implementation if available
            if self.original_plotter:
                return self.original_plotter.create_pareto_plot(
                    fig, canvas, x_obj, y_obj, pareto_X_df, pareto_objectives_df, x_range, y_range
                )
            else:
                self._create_fallback_plot(fig, canvas, f"Error creating plot: {e}")
    
    @plot_performance_timer
    def create_progress_plot(self, fig, canvas, x_range=None, y_range=None):
        """Enhanced progress plot with performance optimizations"""
        
        with self._lock:
            self.plot_call_count += 1
        
        start_time = time.time()
        
        try:
            # Get progress data from optimizer
            if not hasattr(self.optimizer, 'iteration_history') or not self.optimizer.iteration_history:
                return self._create_fallback_plot(fig, canvas, "No optimization progress data available")
            
            # Extract progress data
            iterations = []
            hypervolumes = []
            
            for i, iteration_data in enumerate(self.optimizer.iteration_history):
                iterations.append(i + 1)
                
                # Handle both old and new hypervolume formats
                hv_data = iteration_data.get('hypervolume', 0.0)
                if isinstance(hv_data, dict):
                    hypervolume = hv_data.get('raw_hypervolume', 0.0)
                else:
                    hypervolume = hv_data
                
                hypervolumes.append(hypervolume)
            
            # Prepare plot data
            plot_data = {
                'x': np.array(iterations),
                'y': np.array(hypervolumes)
            }
            
            # Optimize data
            plot_params = {'x_range': x_range, 'y_range': y_range}
            optimized_data = self._prepare_plot_data('progress_plot', plot_data, plot_params)
            
            # Create the plot
            fig.clear()
            ax = fig.add_subplot(111)
            
            # Determine rendering style based on data size
            data_size = len(optimized_data['x'])
            use_fast_rendering = self._should_use_fast_rendering(data_size)
            
            # Plot progress line
            line_kwargs = {
                'color': 'blue',
                'linewidth': 1 if use_fast_rendering else 2,
                'marker': 'o' if data_size <= 50 else None,
                'markersize': 3 if data_size <= 50 else 0,
                'alpha': 0.8
            }
            
            ax.plot(optimized_data['x'], optimized_data['y'], **line_kwargs)
            
            # Add trend line if enough data points
            if len(optimized_data['x']) >= 5:
                try:
                    z = np.polyfit(optimized_data['x'], optimized_data['y'], 1)
                    p = np.poly1d(z)
                    ax.plot(optimized_data['x'], p(optimized_data['x']), "r--", alpha=0.5, linewidth=1, label='Trend')
                    ax.legend()
                except:
                    pass
            
            # Format plot
            ax.set_xlabel("Iteration", fontsize=10)
            ax.set_ylabel("Hypervolume", fontsize=10)
            ax.set_title("Optimization Progress", fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            
            # Set ranges if provided
            if x_range:
                ax.set_xlim(x_range)
            if y_range:
                ax.set_ylim(y_range)
            
            plt.tight_layout()
            canvas.draw()
            
            # Record performance metrics
            render_time = time.time() - start_time
            self.perf_optimizer.plot_metrics['progress_plot'].render_time += render_time
            
            logger.debug(f"Progress plot rendered in {render_time:.3f}s with {data_size} points")
            
        except Exception as e:
            logger.error(f"Error creating enhanced progress plot: {e}")
            # Fallback to original implementation if available
            if self.original_plotter:
                return self.original_plotter.create_progress_plot(fig, canvas, x_range, y_range)
            else:
                self._create_fallback_plot(fig, canvas, f"Error creating plot: {e}")
    
    @plot_performance_timer
    def create_acquisition_function_plot(self, fig, canvas, param1_name, param2_name, 
                                       grid_resolution=50, base_params=None):
        """Enhanced acquisition function plot with performance optimizations"""
        
        with self._lock:
            self.plot_call_count += 1
        
        start_time = time.time()
        
        try:
            # Validate parameters
            if not self._validate_acquisition_plot_requirements(param1_name, param2_name):
                return self._create_fallback_plot(fig, canvas, "Invalid parameters for acquisition plot")
            
            # Generate grid with optimized resolution based on performance settings
            if self.config.enable_data_decimation and grid_resolution > 25:
                grid_resolution = min(grid_resolution, 25)  # Reduce for performance
            
            # Get parameter bounds
            param1_bounds = self.optimizer.params_config[param1_name]['bounds']
            param2_bounds = self.optimizer.params_config[param2_name]['bounds']
            
            # Create meshgrid
            x1 = np.linspace(param1_bounds[0], param1_bounds[1], grid_resolution)
            x2 = np.linspace(param2_bounds[0], param2_bounds[1], grid_resolution)
            X1, X2 = np.meshgrid(x1, x2)
            
            # Calculate acquisition function values
            acq_values = self._calculate_acquisition_values_optimized(
                X1, X2, param1_name, param2_name, base_params
            )
            
            # Prepare plot data
            plot_data = {
                'X': X1,
                'Y': X2,
                'Z': acq_values,
                'grid_resolution': grid_resolution
            }
            
            # Optimize data
            optimized_data = self._prepare_plot_data('acquisition_plot', plot_data)
            
            # Create the plot
            fig.clear()
            ax = fig.add_subplot(111)
            
            # Create contour plot with performance optimizations
            contour_levels = min(20, grid_resolution // 3)  # Adaptive level count
            
            if self._should_use_fast_rendering(grid_resolution * grid_resolution):
                # Fast rendering mode
                contour = ax.contourf(optimized_data['X'], optimized_data['Y'], optimized_data['Z'], 
                                    levels=contour_levels, alpha=0.7, cmap='viridis')
            else:
                # High quality rendering mode
                contour = ax.contourf(optimized_data['X'], optimized_data['Y'], optimized_data['Z'], 
                                    levels=contour_levels, alpha=0.8, cmap='viridis')
                ax.contour(optimized_data['X'], optimized_data['Y'], optimized_data['Z'], 
                          levels=contour_levels, colors='black', alpha=0.3, linewidths=0.5)
            
            # Add colorbar
            cbar = plt.colorbar(contour, ax=ax)
            cbar.set_label('Acquisition Function Value', fontsize=9)
            
            # Mark existing data points
            if hasattr(self.optimizer, 'experimental_data') and not self.optimizer.experimental_data.empty:
                exp_data = self.optimizer.experimental_data
                if param1_name in exp_data.columns and param2_name in exp_data.columns:
                    # Decimate points if too many
                    exp_x = exp_data[param1_name].values
                    exp_y = exp_data[param2_name].values
                    
                    if len(exp_x) > 100:  # Decimate for performance
                        indices = np.linspace(0, len(exp_x) - 1, 100, dtype=int)
                        exp_x, exp_y = exp_x[indices], exp_y[indices]
                    
                    ax.scatter(exp_x, exp_y, c='red', s=30, marker='x', 
                              alpha=0.8, label='Existing Data', zorder=5)
                    ax.legend()
            
            # Format plot
            ax.set_xlabel(param1_name, fontsize=10)
            ax.set_ylabel(param2_name, fontsize=10)
            ax.set_title("Acquisition Function Landscape", fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            canvas.draw()
            
            # Record performance metrics
            render_time = time.time() - start_time
            self.perf_optimizer.plot_metrics['acquisition_plot'].render_time += render_time
            
            logger.debug(f"Acquisition plot rendered in {render_time:.3f}s with {grid_resolution}x{grid_resolution} grid")
            
        except Exception as e:
            logger.error(f"Error creating enhanced acquisition plot: {e}")
            # Fallback to original implementation if available
            if self.original_plotter:
                return self.original_plotter.create_acquisition_function_plot(
                    fig, canvas, param1_name, param2_name, grid_resolution, base_params
                )
            else:
                self._create_fallback_plot(fig, canvas, f"Error creating plot: {e}")
    
    def _calculate_acquisition_values_optimized(self, X1, X2, param1_name, param2_name, base_params):
        """Optimized calculation of acquisition function values"""
        try:
            # Build models if not available
            models = self.optimizer._build_models()
            if models is None:
                return np.zeros_like(X1)
            
            # Setup acquisition function
            acq_func = self.optimizer._setup_acquisition_function(models)
            if acq_func is None:
                return np.zeros_like(X1)
            
            # Use GPU acceleration if available
            if self.perf_optimizer.gpu_plotter.gpu_available:
                return self._calculate_acquisition_gpu(X1, X2, param1_name, param2_name, 
                                                     base_params, acq_func)
            else:
                return self._calculate_acquisition_cpu(X1, X2, param1_name, param2_name, 
                                                     base_params, acq_func)
                
        except Exception as e:
            logger.error(f"Error calculating acquisition values: {e}")
            return np.zeros_like(X1)
    
    def _calculate_acquisition_cpu(self, X1, X2, param1_name, param2_name, base_params, acq_func):
        """CPU-based acquisition function calculation with vectorization"""
        acq_values = np.zeros_like(X1)
        
        # Prepare base parameters
        if base_params is None:
            base_params = {}
            for param_name in self.optimizer.parameter_transformer.param_names:
                if param_name not in [param1_name, param2_name]:
                    config = self.optimizer.params_config[param_name]
                    if config['type'] == 'continuous':
                        bounds = config['bounds']
                        base_params[param_name] = (bounds[0] + bounds[1]) / 2
                    elif config['type'] == 'categorical':
                        base_params[param_name] = config['bounds'][0]
        
        # Vectorized calculation
        flat_X1 = X1.flatten()
        flat_X2 = X2.flatten()
        
        # Batch process for better performance
        batch_size = min(1000, len(flat_X1))
        
        for i in range(0, len(flat_X1), batch_size):
            end_idx = min(i + batch_size, len(flat_X1))
            batch_x1 = flat_X1[i:end_idx]
            batch_x2 = flat_X2[i:end_idx]
            
            # Create parameter tensors for batch
            batch_params = []
            for x1_val, x2_val in zip(batch_x1, batch_x2):
                param_dict = base_params.copy()
                param_dict[param1_name] = x1_val
                param_dict[param2_name] = x2_val
                param_tensor = self.optimizer.parameter_transformer.params_to_tensor(param_dict)
                batch_params.append(param_tensor)
            
            # Stack and evaluate
            if batch_params:
                batch_tensor = torch.stack(batch_params).to(self.optimizer.device)
                
                with torch.no_grad():
                    batch_values = acq_func(batch_tensor.unsqueeze(1)).cpu().numpy()
                
                acq_values.flat[i:end_idx] = batch_values.flatten()
        
        return acq_values
    
    def _calculate_acquisition_gpu(self, X1, X2, param1_name, param2_name, base_params, acq_func):
        """GPU-accelerated acquisition function calculation"""
        # This is a placeholder - GPU acceleration would require more sophisticated implementation
        # For now, fall back to CPU with note about GPU usage
        logger.debug("GPU acquisition calculation requested, falling back to optimized CPU")
        return self._calculate_acquisition_cpu(X1, X2, param1_name, param2_name, base_params, acq_func)
    
    def _validate_acquisition_plot_requirements(self, param1_name, param2_name):
        """Validate requirements for acquisition plot"""
        # Use original validation if available
        if self.original_plotter and hasattr(self.original_plotter, '_validate_acquisition_plot_requirements'):
            return self.original_plotter._validate_acquisition_plot_requirements(param1_name, param2_name)
        
        # Basic validation
        if param1_name == param2_name:
            return False
        
        if (param1_name not in self.optimizer.params_config or 
            param2_name not in self.optimizer.params_config):
            return False
        
        return True
    
    def _get_all_objectives_data(self):
        """Get all objectives data with caching"""
        if hasattr(self.optimizer, 'experimental_data'):
            return self.optimizer.experimental_data
        return pd.DataFrame()
    
    def _create_fallback_plot(self, fig, canvas, message):
        """Create a simple fallback plot with message"""
        fig.clear()
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, message, horizontalalignment='center', 
                verticalalignment='center', transform=ax.transAxes, 
                fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.axis('off')
        canvas.draw()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        base_stats = self.perf_optimizer.get_performance_stats()
        
        # Add enhanced plotting specific stats
        enhanced_stats = {
            'enhanced_plotting': {
                'total_plot_calls': self.plot_call_count,
                'total_time_saved': self.total_time_saved,
                'active_plots': len(self.active_plots),
                'original_plotter_available': ORIGINAL_PLOTTING_AVAILABLE,
                'optimizations_enabled': {
                    'caching': self.config.enable_caching,
                    'data_decimation': self.config.enable_data_decimation,
                    'gpu_acceleration': self.config.enable_gpu_acceleration,
                    'lazy_loading': self.config.enable_lazy_loading
                }
            }
        }
        
        # Merge stats
        base_stats.update(enhanced_stats)
        return base_stats
    
    def clear_cache(self):
        """Clear all plot caches"""
        self.perf_optimizer.clear_cache()
        logger.info("Enhanced plotting cache cleared")
    
    def cleanup_resources(self):
        """Clean up plotting resources"""
        self.clear_cache()
        plt.close('all')  # Close all matplotlib figures
        logger.info("Enhanced plotting resources cleaned up")

# Convenience function to create enhanced plot manager
def create_enhanced_plot_manager(optimizer, **config_kwargs):
    """Create an enhanced plot manager with optimal settings"""
    config = PlotConfig(**config_kwargs)
    return PerformanceEnhancedPlotManager(optimizer, config)

__all__ = [
    'PerformanceEnhancedPlotManager',
    'create_enhanced_plot_manager'
]