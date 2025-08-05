"""
GP Slice Plot Controls Module
Specialized control panel for GP slice plots with display options for confidence intervals, data points, and GP elements
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class GPSliceControlPanel:
    """Specialized control panel for GP slice plots"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.window = None
        self.axis_ranges = {}
        
        # Initialize default axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        # Initialize GP-specific display controls
        self.show_mean_line_var = tk.BooleanVar(value=True)
        self.show_68_ci_var = tk.BooleanVar(value=True)
        self.show_95_ci_var = tk.BooleanVar(value=True)
        self.show_data_points_var = tk.BooleanVar(value=True)
        self.show_legend_var = tk.BooleanVar(value=True)
        self.show_grid_var = tk.BooleanVar(value=True)
        self.show_diagnostics_var = tk.BooleanVar(value=True)
        
        # Style options
        self.mean_line_style_var = tk.StringVar(value="solid")
        self.ci_transparency_var = tk.StringVar(value="medium")
        self.data_point_size_var = tk.StringVar(value="medium")
        
        logger.info(f"GP slice control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ GP Slice Plot Controls")
        self.window.geometry("450x600")
        self.window.resizable(False, False)
        
        # Set window icon (if available)
        try:
            self.window.iconbitmap(default='')
        except:
            pass
            
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for different control categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Display tab
        display_tab = ttk.Frame(notebook)
        notebook.add(display_tab, text="Display Options")
        self._create_display_controls(display_tab)
        
        # Style tab
        style_tab = ttk.Frame(notebook)
        notebook.add(style_tab, text="Style Settings")
        self._create_style_controls(style_tab)
        
        # Axis tab
        axis_tab = ttk.Frame(notebook)
        notebook.add(axis_tab, text="Axis Settings")
        self._create_axis_controls(axis_tab)
        
        # Export tab
        export_tab = ttk.Frame(notebook)
        notebook.add(export_tab, text="Export")
        self._create_export_controls(export_tab)
        
        # Action buttons
        self._create_buttons(main_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        logger.info(f"GP slice control window created")
    
    def _create_display_controls(self, parent):
        """Create display option controls"""
        # GP Elements frame
        gp_frame = ttk.LabelFrame(parent, text="GP Model Elements")
        gp_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(gp_frame, text="Show Mean Prediction Line", 
                       variable=self.show_mean_line_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(gp_frame, text="Show Model Diagnostics", 
                       variable=self.show_diagnostics_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Confidence Intervals frame
        ci_frame = ttk.LabelFrame(parent, text="Confidence Intervals")
        ci_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(ci_frame, text="Show 68% Confidence Interval (±1σ)", 
                       variable=self.show_68_ci_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(ci_frame, text="Show 95% Confidence Interval (±2σ)", 
                       variable=self.show_95_ci_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Data Points frame
        data_frame = ttk.LabelFrame(parent, text="Experimental Data")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(data_frame, text="Show Experimental Data Points", 
                       variable=self.show_data_points_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Plot Elements frame
        elements_frame = ttk.LabelFrame(parent, text="Plot Elements")
        elements_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(elements_frame, text="Show Legend", 
                       variable=self.show_legend_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(elements_frame, text="Show Grid", 
                       variable=self.show_grid_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Information section
        info_frame = ttk.LabelFrame(parent, text="Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = (
            "• Mean Line: GP predicted mean response\n"
            "• 68% CI: ±1 standard deviation (inner band)\n"
            "• 95% CI: ±2 standard deviations (outer band)\n"
            "• Data Points: Experimental observations\n"
            "• Diagnostics: Model quality information\n\n"
            "💡 Confidence intervals show model uncertainty"
        )
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=('TkDefaultFont', 8, 'italic'),
                              foreground='gray',
                              justify='left')
        info_label.pack(padx=10, pady=10, anchor='w')
    
    def _create_style_controls(self, parent):
        """Create style control options"""
        # Mean line style
        line_frame = ttk.LabelFrame(parent, text="Mean Line Style")
        line_frame.pack(fill=tk.X, padx=10, pady=10)
        
        line_style_frame = ttk.Frame(line_frame)
        line_style_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(line_style_frame, text="Line Style:").pack(side=tk.LEFT)
        line_combo = ttk.Combobox(line_style_frame, textvariable=self.mean_line_style_var,
                                 values=["solid", "dashed", "dotted", "dashdot"], 
                                 width=12, state="readonly")
        line_combo.pack(side=tk.LEFT, padx=(10, 0))
        # line_combo.bind('<<ComboboxSelected>>', self._on_style_change)  # Removed real-time update
        
        # Confidence interval transparency
        ci_style_frame = ttk.LabelFrame(parent, text="Confidence Interval Styling")
        ci_style_frame.pack(fill=tk.X, padx=10, pady=10)
        
        transparency_frame = ttk.Frame(ci_style_frame)
        transparency_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(transparency_frame, text="Transparency:").pack(side=tk.LEFT)
        transparency_combo = ttk.Combobox(transparency_frame, textvariable=self.ci_transparency_var,
                                         values=["low", "medium", "high"], 
                                         width=12, state="readonly")
        transparency_combo.pack(side=tk.LEFT, padx=(10, 0))
        # transparency_combo.bind('<<ComboboxSelected>>', self._on_style_change)  # Removed real-time update
        
        # Data point styling
        point_frame = ttk.LabelFrame(parent, text="Data Point Styling")
        point_frame.pack(fill=tk.X, padx=10, pady=10)
        
        size_frame = ttk.Frame(point_frame)
        size_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(size_frame, text="Point Size:").pack(side=tk.LEFT)
        size_combo = ttk.Combobox(size_frame, textvariable=self.data_point_size_var,
                                 values=["small", "medium", "large"], 
                                 width=12, state="readonly")
        size_combo.pack(side=tk.LEFT, padx=(10, 0))
        # size_combo.bind('<<ComboboxSelected>>', self._on_style_change)  # Removed real-time update
        
        # Style preview note
        preview_note = ttk.Label(parent, 
                                text="🎨 Style changes are applied when the plot is updated",
                                font=('TkDefaultFont', 8, 'italic'),
                                foreground='gray')
        preview_note.pack(pady=10)
    
    def _create_axis_controls(self, parent):
        """Create axis range controls"""
        # X-axis section
        x_frame = ttk.LabelFrame(parent, text="X-Axis Range (Parameter)")
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
        y_frame = ttk.LabelFrame(parent, text="Y-Axis Range (Response)")
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
    
    def _on_display_change(self):
        """Handle display option change"""
        # Ensure at least the mean line is shown for a meaningful plot
        if not self.show_mean_line_var.get() and not self.show_68_ci_var.get() and not self.show_95_ci_var.get():
            # If user unchecked everything, keep at least mean line
            self.show_mean_line_var.set(True)
        
        self._update_plot()
    
    def _on_style_change(self, event=None):
        """Handle style option change"""
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
        # This would typically call a method on the parent to export the plot
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
            'show_mean_line': self.show_mean_line_var.get(),
            'show_68_ci': self.show_68_ci_var.get(),
            'show_95_ci': self.show_95_ci_var.get(),
            'show_data_points': self.show_data_points_var.get(),
            'show_legend': self.show_legend_var.get(),
            'show_grid': self.show_grid_var.get(),
            'show_diagnostics': self.show_diagnostics_var.get()
        }
    
    def get_style_options(self):
        """Get the current style options"""
        return {
            'mean_line_style': self.mean_line_style_var.get(),
            'ci_transparency': self.ci_transparency_var.get(),
            'data_point_size': self.data_point_size_var.get()
        }


def create_gp_slice_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
    """Factory function to create a GP slice control panel"""
    logger.info(f"Creating specialized GP slice control panel for {plot_type}")
    control_panel = GPSliceControlPanel(parent, plot_type, params_config, responses_config, update_callback)
    control_panel.create_window()
    return control_panel