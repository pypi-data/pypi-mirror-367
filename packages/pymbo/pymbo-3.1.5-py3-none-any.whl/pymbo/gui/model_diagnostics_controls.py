"""
Model Diagnostics Controls Module
Specialized control panel for model diagnostics with unified tool selection and display options
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class ModelDiagnosticsControlPanel:
    """Specialized control panel for model diagnostics plots"""
    
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
        
        # Main diagnostic tool selection
        self.diagnostic_type_var = tk.StringVar(value="residuals")
        
        # Response selection
        responses_list = list(self.responses_config.keys())
        self.response_var = tk.StringVar(value=responses_list[0] if responses_list else "")
        
        # Display options
        self.show_data_points_var = tk.BooleanVar(value=True)
        self.show_reference_line_var = tk.BooleanVar(value=True)
        self.show_statistics_var = tk.BooleanVar(value=True)
        self.show_uncertainty_bands_var = tk.BooleanVar(value=True)
        
        # Advanced controls collapsed state
        self.advanced_expanded_var = tk.BooleanVar(value=False)
        
        # Advanced diagnostic specific settings
        self.diagnostic_settings = {
            # Plot styling
            'point_size': tk.DoubleVar(value=50),
            'point_alpha': tk.DoubleVar(value=0.7),
            'point_color': tk.StringVar(value='blue'),
            
            # Reference lines and statistics
            'reference_line_style': tk.StringVar(value='dashed'),
            'reference_line_color': tk.StringVar(value='red'),
            'reference_line_width': tk.DoubleVar(value=1.5),
            
            # Statistics display
            'stats_position': tk.StringVar(value='upper_left'),
            'stats_fontsize': tk.IntVar(value=10),
            'show_rmse': tk.BooleanVar(value=True),
            'show_mae': tk.BooleanVar(value=True),
            'show_r2': tk.BooleanVar(value=True),
            
            # Feature importance specific
            'importance_threshold': tk.DoubleVar(value=0.01),
            'max_features': tk.IntVar(value=10),
            
            # Uncertainty specific
            'uncertainty_alpha': tk.DoubleVar(value=0.3),
            'confidence_level': tk.DoubleVar(value=0.95),
            
            # Grid and labels
            'show_grid': tk.BooleanVar(value=True),
            'grid_alpha': tk.DoubleVar(value=0.3),
        }
        
        logger.info(f"Model Diagnostics control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ Model Diagnostics Controls")
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
        
        logger.info(f"Model Diagnostics control window created")
    
    def _create_display_controls(self, parent):
        """Create display option controls"""
        # Diagnostic Tool Selection
        tool_frame = ttk.LabelFrame(parent, text="Diagnostic Tool Selection")
        tool_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Radiobutton(tool_frame, text="Residuals Plot", 
                       variable=self.diagnostic_type_var, value="residuals",
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Radiobutton(tool_frame, text="Parity Plot (Predicted vs Actual)", 
                       variable=self.diagnostic_type_var, value="predictions",
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Radiobutton(tool_frame, text="Uncertainty Analysis", 
                       variable=self.diagnostic_type_var, value="uncertainty",
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Radiobutton(tool_frame, text="Feature Importance", 
                       variable=self.diagnostic_type_var, value="feature_importance",
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Response Selection
        response_frame = ttk.LabelFrame(parent, text="Response Selection")
        response_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(response_frame, text="Response:").pack(anchor='w', padx=10, pady=2)
        response_combo = ttk.Combobox(response_frame, textvariable=self.response_var,
                                     values=list(self.responses_config.keys()), state="readonly")
        response_combo.pack(fill=tk.X, padx=10, pady=2)
        # response_combo.bind('<<ComboboxSelected>>', self._on_response_change)  # Removed real-time update
        
        # Display Options
        display_frame = ttk.LabelFrame(parent, text="Display Options")
        display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(display_frame, text="Show Data Points", 
                       variable=self.show_data_points_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(display_frame, text="Show Reference Line", 
                       variable=self.show_reference_line_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(display_frame, text="Show Statistics", 
                       variable=self.show_statistics_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Create uncertainty-specific checkbox (will be shown/hidden based on selection)
        self.uncertainty_checkbox = ttk.Checkbutton(display_frame, text="Show Uncertainty Bands", 
                                                   variable=self.show_uncertainty_bands_var,
                                                   )
        
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
            "• Residuals: Shows prediction errors (actual - predicted)\n"
            "• Parity Plot: Compares actual vs predicted values\n"
            "• Uncertainty: Shows prediction confidence intervals\n"
            "• Feature Importance: Parameter sensitivity analysis\n\n"
            "💡 Select a diagnostic tool above and choose response.\n"
            "Advanced controls include styling and statistical options."
        )
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=('TkDefaultFont', 8, 'italic'),
                              foreground='gray',
                              justify='left',
                              wraplength=400)
        info_label.pack(padx=10, pady=10, anchor='w')
        
        # Update visibility based on initial selection
        self._update_controls_visibility()
    
    def _create_advanced_controls(self, parent):
        """Create advanced controls that are collapsed by default"""
        # Plot Styling
        style_frame = ttk.LabelFrame(parent, text="Plot Styling")
        style_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(style_frame, text="Point Size:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(style_frame, from_=10, to=200, variable=self.diagnostic_settings['point_size'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(style_frame, text="Point Color:").pack(anchor='w', padx=10, pady=2)
        color_combo = ttk.Combobox(style_frame, textvariable=self.diagnostic_settings['point_color'],
                                  values=['blue', 'red', 'green', 'orange', 'purple', 'black'], state="readonly")
        color_combo.pack(fill=tk.X, padx=10, pady=2)
        # color_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
        
        # Reference Line Settings
        ref_frame = ttk.LabelFrame(parent, text="Reference Line Settings")
        ref_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ref_frame, text="Line Style:").pack(anchor='w', padx=10, pady=2)
        style_combo = ttk.Combobox(ref_frame, textvariable=self.diagnostic_settings['reference_line_style'],
                                  values=['solid', 'dashed', 'dotted', 'dashdot'], state="readonly")
        style_combo.pack(fill=tk.X, padx=10, pady=2)
        # style_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
        
        ttk.Label(ref_frame, text="Line Color:").pack(anchor='w', padx=10, pady=2)
        ref_color_combo = ttk.Combobox(ref_frame, textvariable=self.diagnostic_settings['reference_line_color'],
                                      values=['red', 'black', 'blue', 'green'], state="readonly")
        ref_color_combo.pack(fill=tk.X, padx=10, pady=2)
        # ref_color_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
        
        # Statistics Settings
        stats_frame = ttk.LabelFrame(parent, text="Statistics Display")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(stats_frame, text="Position:").pack(anchor='w', padx=10, pady=2)
        pos_combo = ttk.Combobox(stats_frame, textvariable=self.diagnostic_settings['stats_position'],
                                values=['upper_left', 'upper_right', 'lower_left', 'lower_right'], state="readonly")
        pos_combo.pack(fill=tk.X, padx=10, pady=2)
        # pos_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
        
        ttk.Checkbutton(stats_frame, text="Show RMSE", 
                       variable=self.diagnostic_settings['show_rmse'],
                       ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Checkbutton(stats_frame, text="Show MAE", 
                       variable=self.diagnostic_settings['show_mae'],
                       ).pack(anchor='w', padx=10, pady=2)
        
        ttk.Checkbutton(stats_frame, text="Show R²", 
                       variable=self.diagnostic_settings['show_r2'],
                       ).pack(anchor='w', padx=10, pady=2)
        
        # Feature Importance Settings (shown only for feature importance)
        self.importance_frame = ttk.LabelFrame(parent, text="Feature Importance Settings")
        
        ttk.Label(self.importance_frame, text="Importance Threshold:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(self.importance_frame, from_=0.001, to=0.1, variable=self.diagnostic_settings['importance_threshold'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(self.importance_frame, text="Max Features to Show:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(self.importance_frame, from_=5, to=20, textvariable=self.diagnostic_settings['max_features'],
                   width=10).pack(anchor='w', padx=10, pady=2)
        
        # Uncertainty Settings (shown only for uncertainty)
        self.uncertainty_frame = ttk.LabelFrame(parent, text="Uncertainty Settings")
        
        ttk.Label(self.uncertainty_frame, text="Confidence Level:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(self.uncertainty_frame, from_=0.8, to=0.99, variable=self.diagnostic_settings['confidence_level'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(self.uncertainty_frame, text="Band Transparency:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(self.uncertainty_frame, from_=0.1, to=0.8, variable=self.diagnostic_settings['uncertainty_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
    
    def _toggle_advanced_controls(self):
        """Toggle visibility of advanced controls"""
        if self.advanced_expanded_var.get():
            self.advanced_controls_frame.pack(fill=tk.X, padx=10, pady=5)
            self._update_controls_visibility()
        else:
            self.advanced_controls_frame.pack_forget()
    
    def _update_controls_visibility(self):
        """Update visibility of controls based on selected diagnostic type"""
        diagnostic_type = self.diagnostic_type_var.get()
        
        # Show/hide uncertainty checkbox based on diagnostic type
        if diagnostic_type == "uncertainty":
            self.uncertainty_checkbox.pack(anchor='w', padx=10, pady=5)
        else:
            self.uncertainty_checkbox.pack_forget()
        
        # Show/hide advanced controls sections based on diagnostic type
        if hasattr(self, 'importance_frame') and hasattr(self, 'uncertainty_frame'):
            if diagnostic_type == "feature_importance":
                self.importance_frame.pack(fill=tk.X, padx=5, pady=5)
                self.uncertainty_frame.pack_forget()
            elif diagnostic_type == "uncertainty":
                self.uncertainty_frame.pack(fill=tk.X, padx=5, pady=5)
                self.importance_frame.pack_forget()
            else:
                self.importance_frame.pack_forget()
                self.uncertainty_frame.pack_forget()
    
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
    
    def _on_diagnostic_change(self):
        """Handle diagnostic type change"""
        self._update_controls_visibility()
        self._update_plot()
    
    def _on_response_change(self, event=None):
        """Handle response selection change"""
        self._update_plot()
    
    def _on_display_change(self):
        """Handle display option change"""
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
        return {
            'show_data_points': self.show_data_points_var.get(),
            'show_reference_line': self.show_reference_line_var.get(),
            'show_statistics': self.show_statistics_var.get(),
            'show_uncertainty_bands': self.show_uncertainty_bands_var.get()
        }
    
    def get_diagnostic_settings(self):
        """Get the current diagnostic type and response"""
        return {
            'diagnostic_type': self.diagnostic_type_var.get(),
            'response_name': self.response_var.get()
        }
    
    def get_advanced_settings(self):
        """Get all current advanced diagnostic settings"""
        settings = {}
        for key, var in self.diagnostic_settings.items():
            try:
                settings[key] = var.get()
            except:
                settings[key] = None
        
        # Add display options
        settings.update(self.get_display_options())
        
        return settings


def create_model_diagnostics_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                          responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> ModelDiagnosticsControlPanel:
    """Factory function to create a Model Diagnostics control panel"""
    logger.info(f"Creating specialized Model Diagnostics control panel for {plot_type}")
    control_panel = ModelDiagnosticsControlPanel(parent, plot_type, params_config, responses_config, update_callback)
    control_panel.create_window()
    return control_panel