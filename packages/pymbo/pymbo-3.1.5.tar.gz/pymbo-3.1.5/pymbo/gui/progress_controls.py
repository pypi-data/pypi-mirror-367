"""
Progress Plot Controls Module
Specialized control panel for hypervolume progress plot with display options for different metrics
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class ProgressControlPanel:
    """Specialized control panel for hypervolume progress plot"""
    
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
        
        # Initialize Progress-specific controls
        self.show_raw_hv_var = tk.BooleanVar(value=True)
        self.show_normalized_hv_var = tk.BooleanVar(value=True)
        self.show_trend_var = tk.BooleanVar(value=True)
        self.show_legend_var = tk.BooleanVar(value=True)
        
        logger.info(f"Progress control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ Progress Plot Controls")
        self.window.geometry("400x500")
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
        
        logger.info(f"Progress control window created")
    
    def _create_display_controls(self, parent):
        """Create display option controls"""
        # Hypervolume metrics frame
        hv_frame = ttk.LabelFrame(parent, text="Hypervolume Metrics")
        hv_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(hv_frame, text="Show Raw Hypervolume", 
                       variable=self.show_raw_hv_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(hv_frame, text="Show Normalized Hypervolume", 
                       variable=self.show_normalized_hv_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Analysis frame
        analysis_frame = ttk.LabelFrame(parent, text="Analysis Elements")
        analysis_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(analysis_frame, text="Show Trend Line", 
                       variable=self.show_trend_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Legend frame
        legend_frame = ttk.LabelFrame(parent, text="Legend")
        legend_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(legend_frame, text="Show Legend", 
                       variable=self.show_legend_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Information section
        info_frame = ttk.LabelFrame(parent, text="Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = (
            "• Raw Hypervolume: Absolute hypervolume values\n"
            "• Normalized HV: Scaled to 0-1 range (secondary axis)\n"
            "• Trend Line: Polynomial fit showing progress direction\n\n"
            "💡 Normalized HV uses a secondary y-axis when both are shown"
        )
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=('TkDefaultFont', 8, 'italic'),
                              foreground='gray',
                              justify='left')
        info_label.pack(padx=10, pady=10, anchor='w')
    
    def _create_axis_controls(self, parent):
        """Create axis range controls"""
        # X-axis section
        x_frame = ttk.LabelFrame(parent, text="X-Axis Range (Experiment Number)")
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
        y_frame = ttk.LabelFrame(parent, text="Y-Axis Range (Hypervolume)")
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
        
        # Note about normalized HV
        note_label = ttk.Label(y_frame, 
                              text="Note: Y-axis range applies to raw hypervolume.\nNormalized HV uses fixed 0-1 range on secondary axis.",
                              font=('TkDefaultFont', 8, 'italic'),
                              foreground='gray')
        note_label.pack(pady=5)
        
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
        # Ensure at least one hypervolume metric is shown
        if not self.show_raw_hv_var.get() and not self.show_normalized_hv_var.get():
            # If user unchecked the last option, keep at least raw HV
            self.show_raw_hv_var.set(True)
        
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
            'show_raw_hv': self.show_raw_hv_var.get(),
            'show_normalized_hv': self.show_normalized_hv_var.get(),
            'show_trend': self.show_trend_var.get(),
            'show_legend': self.show_legend_var.get()
        }


def create_progress_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
    """Factory function to create a Progress control panel"""
    logger.info(f"Creating specialized Progress control panel for {plot_type}")
    control_panel = ProgressControlPanel(parent, plot_type, params_config, responses_config, update_callback)
    control_panel.create_window()
    return control_panel