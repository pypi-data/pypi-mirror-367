"""
GP Uncertainty Plot Controls Module
Specialized control panels for Gaussian Process uncertainty plots with extensive customization options
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable
import matplotlib.pyplot as plt
from matplotlib import cm

logger = logging.getLogger(__name__)


class GPUncertaintyControlPanel:
    """Specialized control panel for GP uncertainty plots with extensive options"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.window = None
        
        # GP Uncertainty specific settings
        self.uncertainty_settings = {
            # Axis ranges
            'x_min': tk.StringVar(value='auto'),
            'x_max': tk.StringVar(value='auto'),
            'y_min': tk.StringVar(value='auto'),
            'y_max': tk.StringVar(value='auto'),
            
            # Mean prediction settings
            'show_mean': tk.BooleanVar(value=True),
            'mean_line_style': tk.StringVar(value='solid'),
            'mean_line_width': tk.DoubleVar(value=2.0),
            'mean_color': tk.StringVar(value='blue'),
            'mean_alpha': tk.DoubleVar(value=1.0),
            'mean_marker': tk.StringVar(value='none'),
            'mean_marker_size': tk.DoubleVar(value=6.0),
            
            # Uncertainty band settings
            'show_uncertainty': tk.BooleanVar(value=True),
            'uncertainty_type': tk.StringVar(value='confidence_interval'),
            'confidence_level': tk.DoubleVar(value=95.0),
            'num_std_devs': tk.DoubleVar(value=2.0),
            'uncertainty_alpha': tk.DoubleVar(value=0.3),
            'uncertainty_color': tk.StringVar(value='blue'),
            'uncertainty_fill_style': tk.StringVar(value='solid'),
            'show_std_lines': tk.BooleanVar(value=False),
            'std_line_style': tk.StringVar(value='dashed'),
            'std_line_alpha': tk.DoubleVar(value=0.6),
            
            # Data points settings
            'show_training_points': tk.BooleanVar(value=True),
            'training_point_size': tk.DoubleVar(value=50),
            'training_point_color': tk.StringVar(value='red'),
            'training_point_alpha': tk.DoubleVar(value=0.8),
            'training_point_marker': tk.StringVar(value='o'),
            'training_point_edge_color': tk.StringVar(value='darkred'),
            'training_point_edge_width': tk.DoubleVar(value=1.0),
            
            # Prediction points settings
            'show_prediction_points': tk.BooleanVar(value=False),
            'prediction_point_size': tk.DoubleVar(value=30),
            'prediction_point_color': tk.StringVar(value='green'),
            'prediction_point_alpha': tk.DoubleVar(value=0.6),
            'prediction_point_marker': tk.StringVar(value='x'),
            
            # Sampling and resolution
            'prediction_resolution': tk.IntVar(value=100),
            'extrapolation_factor': tk.DoubleVar(value=0.1),
            'interpolation_method': tk.StringVar(value='linear'),
            'smoothing_factor': tk.DoubleVar(value=0.0),
            
            # Error metrics display
            'show_rmse': tk.BooleanVar(value=False),
            'show_mae': tk.BooleanVar(value=False),
            'show_r2': tk.BooleanVar(value=False),
            'show_likelihood': tk.BooleanVar(value=False),
            'metrics_position': tk.StringVar(value='top_right'),
            'metrics_font_size': tk.IntVar(value=10),
            'metrics_background': tk.BooleanVar(value=True),
            
            # Acquisition function overlay
            'show_acquisition': tk.BooleanVar(value=False),
            'acquisition_type': tk.StringVar(value='EI'),
            'acquisition_alpha': tk.DoubleVar(value=0.5),
            'acquisition_color': tk.StringVar(value='orange'),
            'acquisition_scale': tk.StringVar(value='secondary_y'),
            'acquisition_line_style': tk.StringVar(value='dotted'),
            
            # Gradient information
            'show_gradients': tk.BooleanVar(value=False),
            'gradient_arrow_scale': tk.DoubleVar(value=1.0),
            'gradient_arrow_color': tk.StringVar(value='purple'),
            'gradient_arrow_alpha': tk.DoubleVar(value=0.7),
            'gradient_arrow_width': tk.DoubleVar(value=0.5),
            
            # Contour options (for 2D parameter space)
            'show_uncertainty_contours': tk.BooleanVar(value=False),
            'contour_levels': tk.IntVar(value=10),
            'contour_alpha': tk.DoubleVar(value=0.4),
            'contour_colormap': tk.StringVar(value='Reds'),
            'filled_contours': tk.BooleanVar(value=True),
            
            # Grid and layout
            'show_grid': tk.BooleanVar(value=True),
            'grid_style': tk.StringVar(value='solid'),
            'grid_alpha': tk.DoubleVar(value=0.3),
            'grid_color': tk.StringVar(value='gray'),
            'major_grid_only': tk.BooleanVar(value=False),
            
            # Legends and labels
            'show_legend': tk.BooleanVar(value=True),
            'legend_position': tk.StringVar(value='best'),
            'legend_font_size': tk.IntVar(value=10),
            'legend_frameon': tk.BooleanVar(value=True),
            'legend_shadow': tk.BooleanVar(value=False),
            'x_label': tk.StringVar(value='Parameter'),
            'y_label': tk.StringVar(value='Response'),
            'title': tk.StringVar(value='GP Uncertainty Plot'),
            'title_size': tk.IntVar(value=12),
            'label_size': tk.IntVar(value=10),
            
            # Advanced GP settings
            'kernel_type': tk.StringVar(value='RBF'),
            'length_scale': tk.DoubleVar(value=1.0),
            'noise_level': tk.DoubleVar(value=0.1),
            'show_kernel_info': tk.BooleanVar(value=False),
            'optimize_hyperparams': tk.BooleanVar(value=True),
            
            # Visualization style
            'plot_style': tk.StringVar(value='default'),
            'color_scheme': tk.StringVar(value='default'),
            'figure_dpi': tk.IntVar(value=100),
            'tight_layout': tk.BooleanVar(value=True),
        }
        
        logger.info(f"GP Uncertainty control panel created for {plot_type}")
    
    def create_window(self):
        """Create the comprehensive GP uncertainty control window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ GP Uncertainty Plot Controls - {self.plot_type.replace('_', ' ').title()}")
        self.window.geometry("1125x650")
        self.window.resizable(False, False)
        
        # Create main frame with scrollable content
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create content frame directly without scrollable canvas
        scrollable_frame = ttk.Frame(main_frame)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tabbed interface for organized controls
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure notebook to use wider space efficiently
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[15, 5])
        
        # Create all control tabs
        self._create_axes_tab(notebook)
        self._create_mean_prediction_tab(notebook)
        self._create_uncertainty_tab(notebook)
        self._create_data_points_tab(notebook)
        self._create_sampling_tab(notebook)
        self._create_metrics_tab(notebook)
        self._create_acquisition_tab(notebook)
        self._create_contours_tab(notebook)
        self._create_layout_tab(notebook)
        self._create_gp_model_tab(notebook)
        
        # Action buttons at the bottom
        self._create_action_buttons(scrollable_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        logger.info(f"GP Uncertainty control window created for {self.plot_type}")
    
    def _create_axes_tab(self, notebook):
        """Create axes and ranges tab"""
        axes_tab = ttk.Frame(notebook)
        notebook.add(axes_tab, text="📊 Axes & Ranges")
        
        # X-axis section
        x_frame = ttk.LabelFrame(axes_tab, text="X-Axis Configuration")
        x_frame.pack(fill=tk.X, padx=10, pady=5)
        
        x_range_frame = ttk.Frame(x_frame)
        x_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(x_range_frame, text="Range:").grid(row=0, column=0, sticky='w')
        ttk.Label(x_range_frame, text="Min:").grid(row=0, column=1, sticky='w', padx=(10, 0))
        ttk.Entry(x_range_frame, textvariable=self.uncertainty_settings['x_min'], width=10).grid(row=0, column=2, padx=5)
        ttk.Label(x_range_frame, text="Max:").grid(row=0, column=3, sticky='w', padx=(10, 0))
        ttk.Entry(x_range_frame, textvariable=self.uncertainty_settings['x_max'], width=10).grid(row=0, column=4, padx=5)
        
        # Y-axis section
        y_frame = ttk.LabelFrame(axes_tab, text="Y-Axis Configuration")
        y_frame.pack(fill=tk.X, padx=10, pady=5)
        
        y_range_frame = ttk.Frame(y_frame)
        y_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(y_range_frame, text="Range:").grid(row=0, column=0, sticky='w')
        ttk.Label(y_range_frame, text="Min:").grid(row=0, column=1, sticky='w', padx=(10, 0))
        ttk.Entry(y_range_frame, textvariable=self.uncertainty_settings['y_min'], width=10).grid(row=0, column=2, padx=5)
        ttk.Label(y_range_frame, text="Max:").grid(row=0, column=3, sticky='w', padx=(10, 0))
        ttk.Entry(y_range_frame, textvariable=self.uncertainty_settings['y_max'], width=10).grid(row=0, column=4, padx=5)
        
        # Extrapolation
        extrap_frame = ttk.LabelFrame(axes_tab, text="Extrapolation")
        extrap_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(extrap_frame, text="Extrapolation Factor:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(extrap_frame, from_=0.0, to=0.5, variable=self.uncertainty_settings['extrapolation_factor'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Auto scale button
        ttk.Button(axes_tab, text="🔄 Auto Scale Axes", command=self._auto_scale_axes).pack(pady=10)
    
    def _create_mean_prediction_tab(self, notebook):
        """Create mean prediction settings tab"""
        mean_tab = ttk.Frame(notebook)
        notebook.add(mean_tab, text="📈 Mean Prediction")
        
        # Mean line settings
        mean_frame = ttk.LabelFrame(mean_tab, text="Mean Prediction Line")
        mean_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(mean_frame, text="Show Mean Prediction", 
                       variable=self.uncertainty_settings['show_mean']).pack(anchor='w', padx=10, pady=2)
        
        # Line style
        style_frame = ttk.Frame(mean_frame)
        style_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(style_frame, text="Line Style:").grid(row=0, column=0, sticky='w')
        style_combo = ttk.Combobox(style_frame, textvariable=self.uncertainty_settings['mean_line_style'],
                                  values=['solid', 'dashed', 'dotted', 'dashdot'], width=10)
        style_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(style_frame, text="Color:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        color_combo = ttk.Combobox(style_frame, textvariable=self.uncertainty_settings['mean_color'],
                                  values=['blue', 'red', 'green', 'black', 'orange', 'purple', 'brown'], width=10)
        color_combo.grid(row=0, column=3, padx=5)
        
        # Line properties
        ttk.Label(mean_frame, text="Line Width:").pack(anchor='w', padx=10, pady=(10, 2))
        ttk.Scale(mean_frame, from_=0.5, to=5.0, variable=self.uncertainty_settings['mean_line_width'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(mean_frame, text="Line Alpha:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(mean_frame, from_=0.0, to=1.0, variable=self.uncertainty_settings['mean_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Marker settings
        marker_frame = ttk.LabelFrame(mean_tab, text="Mean Line Markers")
        marker_frame.pack(fill=tk.X, padx=10, pady=5)
        
        marker_style_frame = ttk.Frame(marker_frame)
        marker_style_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(marker_style_frame, text="Marker:").grid(row=0, column=0, sticky='w')
        marker_combo = ttk.Combobox(marker_style_frame, textvariable=self.uncertainty_settings['mean_marker'],
                                   values=['none', 'o', 's', '^', 'v', '<', '>', 'd', 'x', '+'], width=10)
        marker_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(marker_frame, text="Marker Size:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(marker_frame, from_=1.0, to=15.0, variable=self.uncertainty_settings['mean_marker_size'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
    
    def _create_uncertainty_tab(self, notebook):
        """Create uncertainty visualization tab"""
        uncertainty_tab = ttk.Frame(notebook)
        notebook.add(uncertainty_tab, text="🌊 Uncertainty")
        
        # Uncertainty display settings
        uncertainty_frame = ttk.LabelFrame(uncertainty_tab, text="Uncertainty Visualization")
        uncertainty_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(uncertainty_frame, text="Show Uncertainty Band", 
                       variable=self.uncertainty_settings['show_uncertainty']).pack(anchor='w', padx=10, pady=2)
        
        # Uncertainty type
        type_frame = ttk.Frame(uncertainty_frame)
        type_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(type_frame, text="Type:").grid(row=0, column=0, sticky='w')
        type_combo = ttk.Combobox(type_frame, textvariable=self.uncertainty_settings['uncertainty_type'],
                                 values=['confidence_interval', 'prediction_interval', 'standard_deviation'], width=15)
        type_combo.grid(row=0, column=1, padx=5)
        
        # Confidence level
        ttk.Label(uncertainty_frame, text="Confidence Level (%):").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(uncertainty_frame, from_=50.0, to=99.9, variable=self.uncertainty_settings['confidence_level'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Number of standard deviations
        ttk.Label(uncertainty_frame, text="Number of Std Devs:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(uncertainty_frame, from_=0.5, to=3.0, variable=self.uncertainty_settings['num_std_devs'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Band appearance
        band_frame = ttk.LabelFrame(uncertainty_tab, text="Band Appearance")
        band_frame.pack(fill=tk.X, padx=10, pady=5)
        
        band_props_frame = ttk.Frame(band_frame)
        band_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(band_props_frame, text="Color:").grid(row=0, column=0, sticky='w')
        band_color_combo = ttk.Combobox(band_props_frame, textvariable=self.uncertainty_settings['uncertainty_color'],
                                       values=['blue', 'red', 'green', 'gray', 'orange', 'purple'], width=10)
        band_color_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(band_props_frame, text="Fill Style:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        fill_combo = ttk.Combobox(band_props_frame, textvariable=self.uncertainty_settings['uncertainty_fill_style'],
                                 values=['solid', 'hatched', 'crosshatched'], width=10)
        fill_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(band_frame, text="Band Alpha:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(band_frame, from_=0.0, to=1.0, variable=self.uncertainty_settings['uncertainty_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Standard deviation lines
        std_frame = ttk.LabelFrame(uncertainty_tab, text="Standard Deviation Lines")
        std_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(std_frame, text="Show Std Dev Lines", 
                       variable=self.uncertainty_settings['show_std_lines']).pack(anchor='w', padx=10, pady=2)
        
        std_props_frame = ttk.Frame(std_frame)
        std_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(std_props_frame, text="Line Style:").grid(row=0, column=0, sticky='w')
        std_style_combo = ttk.Combobox(std_props_frame, textvariable=self.uncertainty_settings['std_line_style'],
                                      values=['dashed', 'dotted', 'dashdot', 'solid'], width=10)
        std_style_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(std_frame, text="Line Alpha:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(std_frame, from_=0.0, to=1.0, variable=self.uncertainty_settings['std_line_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
    
    def _create_data_points_tab(self, notebook):
        """Create data points settings tab"""
        points_tab = ttk.Frame(notebook)
        notebook.add(points_tab, text="📍 Data Points")
        
        # Training points
        training_frame = ttk.LabelFrame(points_tab, text="Training Data Points")
        training_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(training_frame, text="Show Training Points", 
                       variable=self.uncertainty_settings['show_training_points']).pack(anchor='w', padx=10, pady=2)
        
        # Training point properties
        train_props_frame = ttk.Frame(training_frame)
        train_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(train_props_frame, text="Marker:").grid(row=0, column=0, sticky='w')
        train_marker_combo = ttk.Combobox(train_props_frame, textvariable=self.uncertainty_settings['training_point_marker'],
                                         values=['o', 's', '^', 'v', 'd', 'x', '+', '*'], width=8)
        train_marker_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(train_props_frame, text="Color:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        train_color_combo = ttk.Combobox(train_props_frame, textvariable=self.uncertainty_settings['training_point_color'],
                                        values=['red', 'blue', 'green', 'orange', 'purple', 'black'], width=8)
        train_color_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(training_frame, text="Point Size:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(training_frame, from_=10, to=200, variable=self.uncertainty_settings['training_point_size'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(training_frame, text="Point Alpha:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(training_frame, from_=0.0, to=1.0, variable=self.uncertainty_settings['training_point_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Edge properties
        edge_frame = ttk.Frame(training_frame)
        edge_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(edge_frame, text="Edge Color:").grid(row=0, column=0, sticky='w')
        edge_color_combo = ttk.Combobox(edge_frame, textvariable=self.uncertainty_settings['training_point_edge_color'],
                                       values=['darkred', 'darkblue', 'darkgreen', 'black', 'none'], width=10)
        edge_color_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(edge_frame, text="Edge Width:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        ttk.Spinbox(edge_frame, from_=0.0, to=3.0, increment=0.1, 
                   textvariable=self.uncertainty_settings['training_point_edge_width'], width=8).grid(row=0, column=3, padx=5)
        
        # Prediction points
        prediction_frame = ttk.LabelFrame(points_tab, text="Prediction Points")
        prediction_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(prediction_frame, text="Show Prediction Points", 
                       variable=self.uncertainty_settings['show_prediction_points']).pack(anchor='w', padx=10, pady=2)
        
        pred_props_frame = ttk.Frame(prediction_frame)
        pred_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(pred_props_frame, text="Marker:").grid(row=0, column=0, sticky='w')
        pred_marker_combo = ttk.Combobox(pred_props_frame, textvariable=self.uncertainty_settings['prediction_point_marker'],
                                        values=['x', '+', '*', 'o', 's', '^'], width=8)
        pred_marker_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(pred_props_frame, text="Color:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        pred_color_combo = ttk.Combobox(pred_props_frame, textvariable=self.uncertainty_settings['prediction_point_color'],
                                       values=['green', 'orange', 'purple', 'cyan', 'magenta'], width=8)
        pred_color_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(prediction_frame, text="Point Size:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(prediction_frame, from_=10, to=100, variable=self.uncertainty_settings['prediction_point_size'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
    
    def _create_sampling_tab(self, notebook):
        """Create sampling and resolution tab"""
        sampling_tab = ttk.Frame(notebook)
        notebook.add(sampling_tab, text="🔍 Sampling")
        
        # Resolution settings
        resolution_frame = ttk.LabelFrame(sampling_tab, text="Prediction Resolution")
        resolution_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(resolution_frame, text="Prediction Points:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(resolution_frame, from_=50, to=1000, textvariable=self.uncertainty_settings['prediction_resolution'],
                   width=10).pack(anchor='w', padx=10, pady=2)
        
        # Interpolation settings
        interp_frame = ttk.LabelFrame(sampling_tab, text="Interpolation")
        interp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(interp_frame, text="Method:").pack(anchor='w', padx=10, pady=2)
        interp_combo = ttk.Combobox(interp_frame, textvariable=self.uncertainty_settings['interpolation_method'],
                                   values=['linear', 'cubic', 'nearest'], width=15)
        interp_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(interp_frame, text="Smoothing Factor:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(interp_frame, from_=0.0, to=1.0, variable=self.uncertainty_settings['smoothing_factor'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Quick preset buttons
        preset_frame = ttk.Frame(sampling_tab)
        preset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(preset_frame, text="Low Resolution", 
                  command=lambda: self._set_resolution_preset('low')).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Medium Resolution", 
                  command=lambda: self._set_resolution_preset('medium')).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="High Resolution", 
                  command=lambda: self._set_resolution_preset('high')).pack(side=tk.LEFT, padx=2)
    
    def _create_metrics_tab(self, notebook):
        """Create error metrics display tab"""
        metrics_tab = ttk.Frame(notebook)
        notebook.add(metrics_tab, text="📊 Metrics")
        
        # Error metrics
        metrics_frame = ttk.LabelFrame(metrics_tab, text="Error Metrics Display")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Organize checkboxes in a 2x2 grid
        metrics_grid = ttk.Frame(metrics_frame)
        metrics_grid.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(metrics_grid, text="Show RMSE", 
                       variable=self.uncertainty_settings['show_rmse']).grid(row=0, column=0, sticky='w', padx=(0, 20))
        ttk.Checkbutton(metrics_grid, text="Show MAE", 
                       variable=self.uncertainty_settings['show_mae']).grid(row=0, column=1, sticky='w')
        ttk.Checkbutton(metrics_grid, text="Show R²", 
                       variable=self.uncertainty_settings['show_r2']).grid(row=1, column=0, sticky='w', padx=(0, 20), pady=(2, 0))
        ttk.Checkbutton(metrics_grid, text="Show Log Likelihood", 
                       variable=self.uncertainty_settings['show_likelihood']).grid(row=1, column=1, sticky='w', pady=(2, 0))
        
        # Metrics display settings
        display_frame = ttk.LabelFrame(metrics_tab, text="Display Settings")
        display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(display_frame, text="Position:").pack(anchor='w', padx=10, pady=2)
        position_combo = ttk.Combobox(display_frame, textvariable=self.uncertainty_settings['metrics_position'],
                                     values=['top_right', 'top_left', 'bottom_right', 'bottom_left', 'center'])
        position_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(display_frame, text="Font Size:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(display_frame, from_=6, to=16, textvariable=self.uncertainty_settings['metrics_font_size'],
                   width=10).pack(anchor='w', padx=10, pady=2)
        
        ttk.Checkbutton(display_frame, text="Background Box", 
                       variable=self.uncertainty_settings['metrics_background']).pack(anchor='w', padx=10, pady=2)
    
    def _create_acquisition_tab(self, notebook):
        """Create acquisition function overlay tab"""
        acquisition_tab = ttk.Frame(notebook)
        notebook.add(acquisition_tab, text="🎯 Acquisition")
        
        # Acquisition function settings
        acq_frame = ttk.LabelFrame(acquisition_tab, text="Acquisition Function Overlay")
        acq_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(acq_frame, text="Show Acquisition Function", 
                       variable=self.uncertainty_settings['show_acquisition']).pack(anchor='w', padx=10, pady=2)
        
        acq_props_frame = ttk.Frame(acq_frame)
        acq_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(acq_props_frame, text="Type:").grid(row=0, column=0, sticky='w')
        acq_type_combo = ttk.Combobox(acq_props_frame, textvariable=self.uncertainty_settings['acquisition_type'],
                                     values=['EI', 'UCB', 'PI', 'Thompson', 'Entropy'], width=10)
        acq_type_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(acq_props_frame, text="Color:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        acq_color_combo = ttk.Combobox(acq_props_frame, textvariable=self.uncertainty_settings['acquisition_color'],
                                      values=['orange', 'red', 'green', 'purple', 'brown'], width=10)
        acq_color_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(acq_frame, text="Scale:").pack(anchor='w', padx=10, pady=2)
        scale_combo = ttk.Combobox(acq_frame, textvariable=self.uncertainty_settings['acquisition_scale'],
                                  values=['secondary_y', 'normalized', 'raw'])
        scale_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(acq_frame, text="Alpha:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(acq_frame, from_=0.0, to=1.0, variable=self.uncertainty_settings['acquisition_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Gradient overlay
        gradient_frame = ttk.LabelFrame(acquisition_tab, text="Gradient Information")
        gradient_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(gradient_frame, text="Show Gradients", 
                       variable=self.uncertainty_settings['show_gradients']).pack(anchor='w', padx=10, pady=2)
        
        grad_props_frame = ttk.Frame(gradient_frame)
        grad_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(grad_props_frame, text="Arrow Scale:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(grad_props_frame, from_=0.1, to=5.0, increment=0.1,
                   textvariable=self.uncertainty_settings['gradient_arrow_scale'], width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(grad_props_frame, text="Color:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        grad_color_combo = ttk.Combobox(grad_props_frame, textvariable=self.uncertainty_settings['gradient_arrow_color'],
                                       values=['purple', 'orange', 'red', 'blue', 'green'], width=8)
        grad_color_combo.grid(row=0, column=3, padx=5)
    
    def _create_contours_tab(self, notebook):
        """Create uncertainty contours tab"""
        contours_tab = ttk.Frame(notebook)
        notebook.add(contours_tab, text="📈 Contours")
        
        # Uncertainty contours (for 2D parameter spaces)
        contour_frame = ttk.LabelFrame(contours_tab, text="Uncertainty Contours")
        contour_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(contour_frame, text="Show Uncertainty Contours", 
                       variable=self.uncertainty_settings['show_uncertainty_contours']).pack(anchor='w', padx=10, pady=2)
        
        contour_props_frame = ttk.Frame(contour_frame)
        contour_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(contour_props_frame, text="Levels:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(contour_props_frame, from_=5, to=50, textvariable=self.uncertainty_settings['contour_levels'],
                   width=8).grid(row=0, column=1, padx=5)
        
        ttk.Label(contour_props_frame, text="Colormap:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        contour_cmap_combo = ttk.Combobox(contour_props_frame, textvariable=self.uncertainty_settings['contour_colormap'],
                                         values=['Reds', 'Blues', 'Greens', 'Oranges', 'Purples', 'Greys'], width=10)
        contour_cmap_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(contour_frame, text="Contour Alpha:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(contour_frame, from_=0.0, to=1.0, variable=self.uncertainty_settings['contour_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Checkbutton(contour_frame, text="Filled Contours", 
                       variable=self.uncertainty_settings['filled_contours']).pack(anchor='w', padx=10, pady=2)
    
    def _create_layout_tab(self, notebook):
        """Create layout and appearance tab"""
        layout_tab = ttk.Frame(notebook)
        notebook.add(layout_tab, text="🎨 Layout")
        
        # Grid settings
        grid_frame = ttk.LabelFrame(layout_tab, text="Grid Settings")
        grid_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(grid_frame, text="Show Grid", 
                       variable=self.uncertainty_settings['show_grid']).pack(anchor='w', padx=10, pady=2)
        
        grid_props_frame = ttk.Frame(grid_frame)
        grid_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(grid_props_frame, text="Style:").grid(row=0, column=0, sticky='w')
        grid_style_combo = ttk.Combobox(grid_props_frame, textvariable=self.uncertainty_settings['grid_style'],
                                       values=['solid', 'dashed', 'dotted'], width=10)
        grid_style_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(grid_props_frame, text="Color:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        grid_color_combo = ttk.Combobox(grid_props_frame, textvariable=self.uncertainty_settings['grid_color'],
                                       values=['gray', 'lightgray', 'black', 'blue'], width=10)
        grid_color_combo.grid(row=0, column=3, padx=5)
        
        ttk.Checkbutton(grid_frame, text="Major Grid Only", 
                       variable=self.uncertainty_settings['major_grid_only']).pack(anchor='w', padx=10, pady=2)
        
        # Legend settings
        legend_frame = ttk.LabelFrame(layout_tab, text="Legend Settings")
        legend_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(legend_frame, text="Show Legend", 
                       variable=self.uncertainty_settings['show_legend']).pack(anchor='w', padx=10, pady=2)
        
        legend_props_frame = ttk.Frame(legend_frame)
        legend_props_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(legend_props_frame, text="Position:").grid(row=0, column=0, sticky='w')
        legend_pos_combo = ttk.Combobox(legend_props_frame, textvariable=self.uncertainty_settings['legend_position'],
                                       values=['best', 'upper right', 'upper left', 'lower right', 'lower left'], width=12)
        legend_pos_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(legend_props_frame, text="Size:").grid(row=0, column=2, sticky='w', padx=(10, 0))
        ttk.Spinbox(legend_props_frame, from_=6, to=14, textvariable=self.uncertainty_settings['legend_font_size'],
                   width=6).grid(row=0, column=3, padx=5)
        
        ttk.Checkbutton(legend_frame, text="Frame", 
                       variable=self.uncertainty_settings['legend_frameon']).pack(anchor='w', padx=10, pady=2)
        ttk.Checkbutton(legend_frame, text="Shadow", 
                       variable=self.uncertainty_settings['legend_shadow']).pack(anchor='w', padx=10, pady=2)
        
        # Labels
        labels_frame = ttk.LabelFrame(layout_tab, text="Labels & Title")
        labels_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(labels_frame, text="X Label:").pack(anchor='w', padx=10, pady=2)
        ttk.Entry(labels_frame, textvariable=self.uncertainty_settings['x_label']).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(labels_frame, text="Y Label:").pack(anchor='w', padx=10, pady=2)
        ttk.Entry(labels_frame, textvariable=self.uncertainty_settings['y_label']).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(labels_frame, text="Title:").pack(anchor='w', padx=10, pady=2)
        ttk.Entry(labels_frame, textvariable=self.uncertainty_settings['title']).pack(fill=tk.X, padx=10, pady=2)
        
        # Style settings
        style_frame = ttk.LabelFrame(layout_tab, text="Plot Style")
        style_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(style_frame, text="Style:").pack(anchor='w', padx=10, pady=2)
        style_combo = ttk.Combobox(style_frame, textvariable=self.uncertainty_settings['plot_style'],
                                  values=['default', 'seaborn', 'ggplot', 'bmh', 'fivethirtyeight'])
        style_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Checkbutton(style_frame, text="Tight Layout", 
                       variable=self.uncertainty_settings['tight_layout']).pack(anchor='w', padx=10, pady=2)
    
    def _create_gp_model_tab(self, notebook):
        """Create GP model settings tab"""
        gp_tab = ttk.Frame(notebook)
        notebook.add(gp_tab, text="🧠 GP Model")
        
        # Kernel settings
        kernel_frame = ttk.LabelFrame(gp_tab, text="Kernel Settings")
        kernel_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(kernel_frame, text="Kernel Type:").pack(anchor='w', padx=10, pady=2)
        kernel_combo = ttk.Combobox(kernel_frame, textvariable=self.uncertainty_settings['kernel_type'],
                                   values=['RBF', 'Matern32', 'Matern52', 'RationalQuadratic', 'Linear'])
        kernel_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(kernel_frame, text="Length Scale:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(kernel_frame, from_=0.1, to=10.0, variable=self.uncertainty_settings['length_scale'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(kernel_frame, text="Noise Level:").pack(anchor='w', padx=10, pady=(5, 2))
        ttk.Scale(kernel_frame, from_=0.001, to=1.0, variable=self.uncertainty_settings['noise_level'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Model options
        model_frame = ttk.LabelFrame(gp_tab, text="Model Options")
        model_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(model_frame, text="Show Kernel Info", 
                       variable=self.uncertainty_settings['show_kernel_info']).pack(anchor='w', padx=10, pady=2)
        ttk.Checkbutton(model_frame, text="Optimize Hyperparameters", 
                       variable=self.uncertainty_settings['optimize_hyperparams']).pack(anchor='w', padx=10, pady=2)
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Left side buttons
        ttk.Button(button_frame, text="🔄 Apply & Refresh", 
                  command=self._apply_and_refresh, style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="📊 Refit GP Model", 
                  command=self._refit_model).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="📋 Export Settings", 
                  command=self._export_settings).pack(side=tk.LEFT, padx=2)
        
        # Right side buttons
        ttk.Button(button_frame, text="✕ Close", command=self.hide).pack(side=tk.RIGHT, padx=2)
        
        ttk.Button(button_frame, text="↺ Reset All", 
                  command=self._reset_all_settings).pack(side=tk.RIGHT, padx=2)
        
        ttk.Button(button_frame, text="💾 Save Plot", 
                  command=self._save_plot).pack(side=tk.RIGHT, padx=2)
    
    def _auto_scale_axes(self):
        """Auto scale axes"""
        self.uncertainty_settings['x_min'].set('auto')
        self.uncertainty_settings['x_max'].set('auto')
        self.uncertainty_settings['y_min'].set('auto')
        self.uncertainty_settings['y_max'].set('auto')
        logger.info(f"Auto scale applied for {self.plot_type}")
    
    def _set_resolution_preset(self, preset):
        """Set resolution preset"""
        presets = {
            'low': 50,
            'medium': 100,
            'high': 300
        }
        if preset in presets:
            self.uncertainty_settings['prediction_resolution'].set(presets[preset])
            logger.info(f"Resolution preset '{preset}' applied for {self.plot_type}")
    
    def _apply_and_refresh(self):
        """Apply settings and refresh plot"""
        logger.info(f"Applying GP uncertainty settings for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"GP uncertainty plot updated for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error updating GP uncertainty plot for {self.plot_type}: {e}")
    
    def _refit_model(self):
        """Refit the GP model with current settings"""
        logger.info(f"Refitting GP model for {self.plot_type}")
    
    def _export_settings(self):
        """Export current settings"""
        logger.info(f"Exporting settings for {self.plot_type}")
    
    def _reset_all_settings(self):
        """Reset all settings to defaults"""
        # Reset to default values - abbreviated for brevity
        defaults = {
            'x_min': 'auto', 'x_max': 'auto', 'y_min': 'auto', 'y_max': 'auto',
            'show_mean': True, 'mean_line_style': 'solid', 'mean_line_width': 2.0, 'mean_color': 'blue',
            'show_uncertainty': True, 'uncertainty_type': 'confidence_interval', 'confidence_level': 95.0,
            'show_training_points': True, 'training_point_size': 50, 'training_point_color': 'red',
            'prediction_resolution': 100, 'show_grid': True, 'show_legend': True,
            'x_label': 'Parameter', 'y_label': 'Response', 'title': 'GP Uncertainty Plot'
        }
        
        for key, value in defaults.items():
            if key in self.uncertainty_settings:
                self.uncertainty_settings[key].set(value)
        
        logger.info(f"All settings reset to defaults for {self.plot_type}")
    
    def _save_plot(self):
        """Save the plot"""
        logger.info(f"Save plot requested for {self.plot_type}")
    
    def show(self):
        """Show the control panel window"""
        if self.window is None:
            self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        logger.info(f"GP Uncertainty control window shown for {self.plot_type}")
    
    def hide(self):
        """Hide the control panel window"""
        if self.window:
            self.window.withdraw()
        logger.info(f"GP Uncertainty control window hidden for {self.plot_type}")
    
    def get_uncertainty_settings(self):
        """Get all current GP uncertainty settings"""
        settings = {}
        for key, var in self.uncertainty_settings.items():
            try:
                settings[key] = var.get()
            except:
                settings[key] = None
        return settings


def create_gp_uncertainty_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                       responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> GPUncertaintyControlPanel:
    """Factory function to create a GP uncertainty control panel"""
    try:
        control_panel = GPUncertaintyControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created GP uncertainty control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating GP uncertainty control panel for {plot_type}: {e}")
        raise