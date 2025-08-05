"""
Uncertainty Analysis Controls Module
Specialized control panel for uncertainty analysis plots with user-friendly display options
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class UncertaintyAnalysisControlPanel:
    """Specialized control panel for uncertainty analysis plots"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.window = None
        
        # Initialize axis ranges like other control panels
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        # Main display controls - what type of uncertainty to show
        # Use StringVar for radio button behavior instead of multiple BooleanVars
        self.uncertainty_type_var = tk.StringVar(value="data_density")
        self.show_original_data_var = tk.BooleanVar(value=True)
        
        # Parameter selection for axes
        params_list = list(self.params_config.keys())
        self.x_parameter_var = tk.StringVar(value=params_list[0] if params_list else "")
        self.y_parameter_var = tk.StringVar(value=params_list[1] if len(params_list) > 1 else "")
        
        # Response selection
        responses_list = list(self.responses_config.keys())
        self.response_var = tk.StringVar(value=responses_list[0] if responses_list else "")
        
        # Advanced controls collapsed state
        self.advanced_expanded_var = tk.BooleanVar(value=False)
        
        # Advanced uncertainty analysis specific settings
        self.uncertainty_settings = {
            # Visualization type
            'uncertainty_metric': tk.StringVar(value='data_density'),  # 'gp_uncertainty', 'data_density', 'std', 'variance'
            'plot_style': tk.StringVar(value='heatmap'),  # 'heatmap', 'contour', 'filled_contour'
            
            # Resolution and quality
            'resolution': tk.IntVar(value=70),
            'colormap': tk.StringVar(value='Reds'),
            
            
            # Visualization appearance
            'show_colorbar': tk.BooleanVar(value=True),
            'contour_levels': tk.IntVar(value=15),
            'alpha': tk.DoubleVar(value=0.8),
            
            # Data point appearance
            'data_point_size': tk.DoubleVar(value=50),
            'data_point_color': tk.StringVar(value='black'),
            'data_point_alpha': tk.DoubleVar(value=0.8),
            
            # Grid and labels
            'show_grid': tk.BooleanVar(value=True),
            'grid_alpha': tk.DoubleVar(value=0.3),
        }
        
        logger.info(f"Uncertainty Analysis control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ Uncertainty Analysis Controls")
        self.window.geometry("480x700")
        self.window.resizable(True, True)
        
        # Set window icon (if available)
        try:
            self.window.iconbitmap(default='')
        except:
            pass
            
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create notebook for different control categories
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Display tab (main controls)
        display_tab = ttk.Frame(notebook)
        notebook.add(display_tab, text="Display Options")
        self._create_display_controls(display_tab)
        
        # Axis tab
        axis_tab = ttk.Frame(notebook)
        notebook.add(axis_tab, text="Axis Settings")
        self._create_axis_controls(axis_tab)
        
        # Export tab
        export_tab = ttk.Frame(notebook)
        notebook.add(export_tab, text="Export")
        self._create_export_controls(export_tab)
        
        # Action buttons
        self._create_buttons(scrollable_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        logger.info(f"Uncertainty Analysis control window created")
    
    def _create_display_controls(self, parent):
        """Create display option controls"""
        # Parameter selection frame
        param_frame = ttk.LabelFrame(parent, text="Parameter Selection")
        param_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Response selection
        ttk.Label(param_frame, text="Response:").pack(anchor='w', padx=10, pady=2)
        response_combo = ttk.Combobox(param_frame, textvariable=self.response_var,
                                     values=list(self.responses_config.keys()), state="readonly")
        response_combo.pack(fill=tk.X, padx=10, pady=2)
        # response_combo.bind('<<ComboboxSelected>>', self._on_parameter_change)  # Removed real-time update
        
        # X-axis parameter
        ttk.Label(param_frame, text="X-Axis Parameter:").pack(anchor='w', padx=10, pady=2)
        x_param_combo = ttk.Combobox(param_frame, textvariable=self.x_parameter_var,
                                    values=list(self.params_config.keys()), state="readonly")
        x_param_combo.pack(fill=tk.X, padx=10, pady=2)
        # x_param_combo.bind('<<ComboboxSelected>>', self._on_parameter_change)  # Removed real-time update
        
        # Y-axis parameter
        ttk.Label(param_frame, text="Y-Axis Parameter:").pack(anchor='w', padx=10, pady=2)
        y_param_combo = ttk.Combobox(param_frame, textvariable=self.y_parameter_var,
                                    values=list(self.params_config.keys()), state="readonly")
        y_param_combo.pack(fill=tk.X, padx=10, pady=2)
        # y_param_combo.bind('<<ComboboxSelected>>', self._on_parameter_change)  # Removed real-time update
        
        # Uncertainty visualization frame
        uncertainty_frame = ttk.LabelFrame(parent, text="Uncertainty Visualization")
        uncertainty_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Radiobutton(uncertainty_frame, text="Show GP Prediction Uncertainty", 
                       variable=self.uncertainty_type_var, value="gp_uncertainty",
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Radiobutton(uncertainty_frame, text="Show Data Density", 
                       variable=self.uncertainty_type_var, value="data_density",
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Data overlay frame
        data_frame = ttk.LabelFrame(parent, text="Data Overlay")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(data_frame, text="Show Original Data Points", 
                       variable=self.show_original_data_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Advanced controls collapsible section
        advanced_frame = ttk.LabelFrame(parent, text="Advanced Controls")
        advanced_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Toggle button for advanced controls
        advanced_toggle = ttk.Checkbutton(advanced_frame, text="Show Advanced Control Panel", 
                                         variable=self.advanced_expanded_var,
                                         command=self._toggle_advanced_controls)
        advanced_toggle.pack(anchor='w', padx=10, pady=5)
        
        # Advanced controls container (initially hidden)
        self.advanced_controls_frame = ttk.Frame(advanced_frame)
        self._create_advanced_controls(self.advanced_controls_frame)
        
        # Information section
        info_frame = ttk.LabelFrame(parent, text="Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = (
            "• GP Uncertainty: Model's predictive uncertainty\n"
            "• Data Density: Spatial distribution of experimental data\n"
            "• Original Data: Experimental observation points\n\n"
            "💡 Select one uncertainty visualization type above.\n"
            "Advanced controls include resolution, colormaps,\n"
            "and detailed appearance settings"
        )
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=('TkDefaultFont', 8, 'italic'),
                              foreground='gray',
                              justify='left',
                              wraplength=400)
        info_label.pack(padx=10, pady=10, anchor='w')
    
    def _create_advanced_controls(self, parent):
        """Create advanced controls that are collapsed by default"""
        # Visualization type controls
        viz_frame = ttk.LabelFrame(parent, text="Visualization Settings")
        viz_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(viz_frame, text="Plot Style:").pack(anchor='w', padx=10, pady=2)
        style_combo = ttk.Combobox(viz_frame, textvariable=self.uncertainty_settings['plot_style'],
                                  values=['heatmap', 'contour', 'filled_contour'], state="readonly")
        style_combo.pack(fill=tk.X, padx=10, pady=2)
        # style_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
        
        ttk.Label(viz_frame, text="Colormap:").pack(anchor='w', padx=10, pady=2)
        colormap_combo = ttk.Combobox(viz_frame, textvariable=self.uncertainty_settings['colormap'],
                                     values=['Reds', 'Blues', 'Greens', 'Oranges', 'viridis', 'plasma', 'coolwarm'], 
                                     state="readonly")
        colormap_combo.pack(fill=tk.X, padx=10, pady=2)
        # colormap_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
        
        # Resolution controls
        res_frame = ttk.LabelFrame(parent, text="Resolution & Quality")
        res_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(res_frame, text="Grid Resolution:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(res_frame, from_=30, to=200, textvariable=self.uncertainty_settings['resolution'],
                   width=10).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(res_frame, text="Contour Levels:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(res_frame, from_=5, to=50, textvariable=self.uncertainty_settings['contour_levels'],
                   width=10).pack(anchor='w', padx=10, pady=2)
        
        
        # Data point appearance
        points_frame = ttk.LabelFrame(parent, text="Data Point Appearance")
        points_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(points_frame, text="Point Size:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(points_frame, from_=10, to=200, variable=self.uncertainty_settings['data_point_size'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(points_frame, text="Point Color:").pack(anchor='w', padx=10, pady=2)
        color_combo = ttk.Combobox(points_frame, textvariable=self.uncertainty_settings['data_point_color'],
                                  values=['black', 'red', 'blue', 'green', 'orange', 'purple'], state="readonly")
        color_combo.pack(fill=tk.X, padx=10, pady=2)
        # color_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
    
    def _toggle_advanced_controls(self):
        """Toggle visibility of advanced controls"""
        if self.advanced_expanded_var.get():
            self.advanced_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        else:
            self.advanced_controls_frame.pack_forget()
    
    def _create_axis_controls(self, parent):
        """Create axis range controls"""
        # X-axis section
        x_frame = ttk.LabelFrame(parent, text="X-Axis Range")
        x_frame.pack(fill=tk.X, padx=10, pady=10)
        
        x_controls = ttk.Frame(x_frame)
        x_controls.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(x_controls, text="Min:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        x_min_entry = ttk.Entry(x_controls, textvariable=self.axis_ranges['x_min']['var'], width=12)
        x_min_entry.grid(row=0, column=1, padx=(0, 10))
        # x_min_entry.bind('<KeyRelease>', self._on_axis_change)  # Removed real-time update
        
        ttk.Label(x_controls, text="Max:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        x_max_entry = ttk.Entry(x_controls, textvariable=self.axis_ranges['x_max']['var'], width=12)
        x_max_entry.grid(row=0, column=3)
        # x_max_entry.bind('<KeyRelease>', self._on_axis_change)  # Removed real-time update
        
        # Y-axis section
        y_frame = ttk.LabelFrame(parent, text="Y-Axis Range")
        y_frame.pack(fill=tk.X, padx=10, pady=10)
        
        y_controls = ttk.Frame(y_frame)
        y_controls.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(y_controls, text="Min:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        y_min_entry = ttk.Entry(y_controls, textvariable=self.axis_ranges['y_min']['var'], width=12)
        y_min_entry.grid(row=0, column=1, padx=(0, 10))
        # y_min_entry.bind('<KeyRelease>', self._on_axis_change)  # Removed real-time update
        
        ttk.Label(y_controls, text="Max:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        y_max_entry = ttk.Entry(y_controls, textvariable=self.axis_ranges['y_max']['var'], width=12)
        y_max_entry.grid(row=0, column=3)
        # y_max_entry.bind('<KeyRelease>', self._on_axis_change)  # Removed real-time update
        
        # Auto scale button
        auto_frame = ttk.Frame(parent)
        auto_frame.pack(pady=10)
        
        auto_button = ttk.Button(auto_frame, text="🔄 Auto Scale Both Axes", 
                                command=self._auto_scale, style='Accent.TButton')
        auto_button.pack()
    
    def _create_export_controls(self, parent):
        """Create export control options"""
        export_frame = ttk.LabelFrame(parent, text="Export Settings")
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # DPI settings
        dpi_frame = ttk.Frame(export_frame)
        dpi_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(dpi_frame, text="Export DPI:").pack(side=tk.LEFT)
        self.export_dpi_var = tk.StringVar(value="300")
        dpi_combo = ttk.Combobox(dpi_frame, textvariable=self.export_dpi_var, 
                                values=["150", "300", "600", "1200"], width=8, state="readonly")
        dpi_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Export button
        export_button = ttk.Button(export_frame, text="📁 Export Plot", 
                                  command=self._export_plot)
        export_button.pack(pady=10)
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Update button
        update_button = ttk.Button(button_frame, text="🔄 Update Plot", 
                                  command=self._update_plot, style='Accent.TButton')
        update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_button = ttk.Button(button_frame, text="✖ Close", command=self.hide)
        close_button.pack(side=tk.RIGHT)
    
    def _on_parameter_change(self, event=None):
        """Handle parameter selection change"""
        self._update_plot()
    
    def _on_display_change(self):
        """Handle display option change"""
        # Get the selected uncertainty type
        uncertainty_type = self.uncertainty_type_var.get()
        
        # Set the appropriate uncertainty metric
        if uncertainty_type == "gp_uncertainty":
            self.uncertainty_settings['uncertainty_metric'].set('gp_uncertainty')
        elif uncertainty_type == "data_density":
            self.uncertainty_settings['uncertainty_metric'].set('data_density')
        
        self._update_plot()
    
    def _on_advanced_change(self, event=None):
        """Handle advanced option change"""
        self._update_plot()
    
    def _on_axis_change(self, event=None):
        """Handle axis range change"""
        # Parse the ranges and update
        for axis in ['x_min', 'x_max', 'y_min', 'y_max']:
            value = self.axis_ranges[axis]['var'].get().strip()
            if value.lower() == 'auto' or value == '':
                self.axis_ranges[axis]['auto'] = True
            else:
                try:
                    float(value)
                    self.axis_ranges[axis]['auto'] = False
                except ValueError:
                    # Invalid value, reset to auto
                    self.axis_ranges[axis]['var'].set('auto')
                    self.axis_ranges[axis]['auto'] = True
        
        self._update_plot()
    
    def _auto_scale(self):
        """Reset to auto scaling"""
        for axis in ['x_min', 'x_max', 'y_min', 'y_max']:
            self.axis_ranges[axis]['var'].set('auto')
            self.axis_ranges[axis]['auto'] = True
        self._update_plot()
    
    def _export_plot(self):
        """Export the current plot"""
        logger.info("Export plot functionality not implemented yet")
    
    def _update_plot(self):
        """Update the plot with current settings"""
        if self.update_callback:
            self.update_callback()
    
    def show(self):
        """Show the control window"""
        if self.window is None:
            self.create_window()
        else:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
    
    def hide(self):
        """Hide the control window"""
        if self.window:
            self.window.withdraw()
    
    def destroy(self):
        """Destroy the control window"""
        if self.window:
            self.window.destroy()
            self.window = None
    
    def get_axis_ranges(self):
        """Get the current axis ranges in the format expected by the GUI"""
        ranges = {}
        
        # X-axis range - get values and determine if auto
        x_min_val, x_max_val, x_auto = self._get_axis_value('x_min')
        y_min_val, y_max_val, y_auto = self._get_axis_value('y_min')
        
        # Format for main GUI expectation: (min_val, max_val, is_auto)
        ranges['x_axis'] = (x_min_val, x_max_val, x_auto)
        ranges['y_axis'] = (y_min_val, y_max_val, y_auto)
        
        return ranges
    
    def _get_axis_value(self, axis_key):
        """Helper to get axis values and determine if auto"""
        if axis_key.endswith('_min'):
            base_axis = axis_key[:-4]  # Remove '_min'
            min_value = self.axis_ranges[f'{base_axis}_min']['var'].get()
            max_value = self.axis_ranges[f'{base_axis}_max']['var'].get()
            
            min_auto = min_value.lower() == 'auto'
            max_auto = max_value.lower() == 'auto'
            is_auto = min_auto or max_auto
            
            try:
                min_val = None if min_auto else float(min_value)
                max_val = None if max_auto else float(max_value)
            except ValueError:
                min_val = max_val = None
                is_auto = True
                
            return min_val, max_val, is_auto
        return None, None, True
    
    def get_display_options(self):
        """Get the current display options"""
        uncertainty_type = self.uncertainty_type_var.get()
        return {
            'show_gp_uncertainty': uncertainty_type == "gp_uncertainty",
            'show_data_density': uncertainty_type == "data_density", 
            'show_statistical_deviation': False,  # Removed this option
            'show_experimental_data': self.show_original_data_var.get()
        }
    
    def get_parameters(self):
        """Get the selected parameters"""
        return {
            'response': self.response_var.get(),
            'x_parameter': self.x_parameter_var.get(),
            'y_parameter': self.y_parameter_var.get()
        }
    
    def get_uncertainty_settings(self):
        """Get all current uncertainty analysis settings"""
        settings = {}
        for key, var in self.uncertainty_settings.items():
            try:
                settings[key] = var.get()
            except:
                settings[key] = None
        
        # Add display options
        settings.update(self.get_display_options())
        
        return settings


def create_uncertainty_analysis_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                             responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> UncertaintyAnalysisControlPanel:
    """Factory function to create an Uncertainty Analysis control panel"""
    logger.info(f"Creating specialized Uncertainty Analysis control panel for {plot_type}")
    control_panel = UncertaintyAnalysisControlPanel(parent, plot_type, params_config, responses_config, update_callback)
    control_panel.create_window()
    return control_panel