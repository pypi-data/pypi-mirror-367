"""
Parallel Coordinates Controls Module
Specialized control panel for parallel coordinates plot with variable selection
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable, List

logger = logging.getLogger(__name__)


class ParallelCoordinatesControlPanel:
    """Specialized control panel for parallel coordinates plot"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.window = None
        self.axis_ranges = {}
        
        # Initialize variable selection checkboxes
        all_variables = list(self.params_config.keys()) + list(self.responses_config.keys())
        self.variable_selection_vars = {}
        for var_name in all_variables:
            var = tk.BooleanVar(value=True)  # Default to including all variables
            self.variable_selection_vars[var_name] = var
        
        # Initialize default axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        logger.info(f"Parallel coordinates control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ Parallel Coordinates Controls")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 Parallel Coordinates Controls", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Create notebook for organized controls
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Variable Selection tab
        variables_tab = ttk.Frame(notebook)
        notebook.add(variables_tab, text="Variable Selection")
        self._create_variable_selection_controls(variables_tab)
        
        # Appearance tab
        appearance_tab = ttk.Frame(notebook)
        notebook.add(appearance_tab, text="Appearance") 
        self._create_appearance_controls(appearance_tab)
        
        # Export tab
        export_tab = ttk.Frame(notebook)
        notebook.add(export_tab, text="Export")
        self._create_export_controls(export_tab)
        
        # Action buttons
        self._create_window_buttons(main_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        logger.info(f"Parallel coordinates control window created")
    
    def _create_variable_selection_controls(self, parent):
        """Create variable selection controls"""
        # Parameters section
        if self.params_config:
            params_frame = ttk.LabelFrame(parent, text="Parameters")
            params_frame.pack(fill=tk.X, padx=10, pady=10)
            
            for param_name in self.params_config.keys():
                if param_name in self.variable_selection_vars:
                    ttk.Checkbutton(
                        params_frame,
                        text=param_name,
                        variable=self.variable_selection_vars[param_name],
                        # command=self._on_variable_selection_change  # Removed real-time update
                    ).pack(anchor='w', padx=10, pady=2)
        
        # Responses section
        if self.responses_config:
            responses_frame = ttk.LabelFrame(parent, text="Responses")
            responses_frame.pack(fill=tk.X, padx=10, pady=10)
            
            for response_name in self.responses_config.keys():
                if response_name in self.variable_selection_vars:
                    ttk.Checkbutton(
                        responses_frame,
                        text=response_name,
                        variable=self.variable_selection_vars[response_name],
                        # command=self._on_variable_selection_change  # Removed real-time update
                    ).pack(anchor='w', padx=10, pady=2)
        
        # Selection control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(control_frame, text="Select All", 
                  command=self._select_all_variables).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Clear All", 
                  command=self._clear_all_variables).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Select Params Only", 
                  command=self._select_params_only).pack(side=tk.LEFT)
    
    def _create_appearance_controls(self, parent):
        """Create appearance control options"""
        # Grid options
        grid_frame = ttk.LabelFrame(parent, text="Grid Options")
        grid_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.show_grid_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid_frame, text="Show Grid", 
                       variable=self.show_grid_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Color scheme
        color_frame = ttk.LabelFrame(parent, text="Color Scheme")
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.color_scheme_var = tk.StringVar(value="viridis")
        color_schemes = ["viridis", "plasma", "inferno", "cividis", "rainbow", "coolwarm"]
        
        for scheme in color_schemes:
            ttk.Radiobutton(color_frame, text=scheme.title(), 
                           variable=self.color_scheme_var, value=scheme,
                           ).pack(anchor='w', padx=10, pady=2)
    
    def _create_export_controls(self, parent):
        """Create export control options"""
        export_frame = ttk.LabelFrame(parent, text="Export Settings")
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # DPI settings
        dpi_frame = ttk.Frame(export_frame)
        dpi_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dpi_frame, text="Resolution (DPI):").pack(side=tk.LEFT)
        self.dpi_var = tk.StringVar(value="300")
        dpi_combo = ttk.Combobox(dpi_frame, textvariable=self.dpi_var, 
                                values=["150", "300", "600", "1200"], width=10)
        dpi_combo.pack(side=tk.RIGHT)
        
        # Format settings
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["PNG", "PDF", "SVG", "JPG"], width=10)
        format_combo.pack(side=tk.RIGHT)
        
        # Export button
        export_btn = ttk.Button(export_frame, text="💾 Export Plot", 
                               command=self._export_plot)
        export_btn.pack(pady=10)
    
    def _create_window_buttons(self, parent):
        """Create action buttons for window"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side buttons
        refresh_button = ttk.Button(button_frame, text="🔄 Update Plot", 
                                   command=self._refresh_plot, style='Accent.TButton')
        refresh_button.pack(side=tk.LEFT)
        
        apply_button = ttk.Button(button_frame, text="✓ Apply Settings", 
                                 command=self._apply_settings)
        apply_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Right side buttons
        close_button = ttk.Button(button_frame, text="✕ Close", command=self.hide)
        close_button.pack(side=tk.RIGHT)
        
        reset_button = ttk.Button(button_frame, text="↺ Reset", command=self._reset_settings)
        reset_button.pack(side=tk.RIGHT, padx=(0, 5))
    
    def _on_variable_selection_change(self):
        """Handle variable selection changes"""
        logger.info("Variable selection changed for parallel coordinates")
        
        # Update the main GUI's parallel_coords_vars if it exists
        if hasattr(self.parent, 'parallel_coords_vars'):
            # Sync our selections with the main GUI
            for var_name, var_obj in self.variable_selection_vars.items():
                if var_name in self.parent.parallel_coords_vars:
                    self.parent.parallel_coords_vars[var_name].set(var_obj.get())
        
        # Trigger plot update
        self._refresh_plot()
    
    def _on_appearance_change(self):
        """Handle appearance changes"""
        logger.info("Appearance changed for parallel coordinates")
        # For now, just trigger a plot update
        # In the future, we could apply appearance changes to the existing plot
        self._refresh_plot()
    
    def _select_all_variables(self):
        """Select all variables"""
        for var in self.variable_selection_vars.values():
            var.set(True)
        self._on_variable_selection_change()
    
    def _clear_all_variables(self):
        """Clear all variable selections"""
        for var in self.variable_selection_vars.values():
            var.set(False)
        self._on_variable_selection_change()
    
    def _select_params_only(self):
        """Select only parameter variables"""
        for var_name, var in self.variable_selection_vars.items():
            if var_name in self.params_config:
                var.set(True)
            else:
                var.set(False)
        self._on_variable_selection_change()
    
    def _refresh_plot(self):
        """Refresh the plot with current settings"""
        logger.info("Plot refresh requested for parallel coordinates")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info("Update callback executed for parallel coordinates")
            except Exception as e:
                logger.error(f"Error calling update callback for parallel coordinates: {e}")
        else:
            logger.warning("No update callback available for parallel coordinates")
    
    def _apply_settings(self):
        """Apply current settings to the plot"""
        logger.info("Settings applied for parallel coordinates")
        self._refresh_plot()
    
    def _reset_settings(self):
        """Reset all settings to defaults"""
        # Reset variable selections to all true
        for var in self.variable_selection_vars.values():
            var.set(True)
        
        # Reset appearance settings
        self.show_grid_var.set(True)
        self.color_scheme_var.set("viridis")
        self.dpi_var.set("300")
        self.format_var.set("PNG")
        
        logger.info("Settings reset for parallel coordinates")
        self._on_variable_selection_change()
    
    def _export_plot(self):
        """Export the plot with current settings"""
        from tkinter import filedialog, messagebox
        import matplotlib.pyplot as plt
        
        try:
            format_ext = self.format_var.get().lower()
            dpi_value = int(self.dpi_var.get())
            
            # Get filename from user
            filename = filedialog.asksaveasfilename(
                title="Export Parallel Coordinates Plot",
                defaultextension=f".{format_ext}",
                filetypes=[
                    (f"{format_ext.upper()} files", f"*.{format_ext}"),
                    ("All files", "*.*")
                ]
            )
            
            if not filename:
                return  # User cancelled
            
            # Try to find the current figure for this plot type
            figure = None
            parent_gui = self.parent
            
            if hasattr(parent_gui, 'parallel_coords_fig'):
                figure = parent_gui.parallel_coords_fig
            
            if figure is None:
                figure = plt.gcf()
            
            if figure:
                figure.savefig(filename, format=format_ext, dpi=dpi_value, 
                             bbox_inches='tight', facecolor='white')
                
                messagebox.showinfo("Export Successful", 
                                  f"Plot exported successfully to:\n{filename}")
                logger.info(f"Parallel coordinates plot exported to {filename}")
            else:
                messagebox.showerror("Export Error", 
                                   "Could not find the plot to export.")
                logger.error("Could not find figure to export for parallel coordinates")
                
        except Exception as e:
            error_msg = f"Failed to export plot: {str(e)}"
            messagebox.showerror("Export Error", error_msg)
            logger.error(f"Export error for parallel coordinates: {e}")
    
    def show(self):
        """Show the control panel window"""
        if self.window is None:
            self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        logger.info("Parallel coordinates control window shown")
    
    def hide(self):
        """Hide the control panel window"""
        if self.window:
            self.window.withdraw()
        logger.info("Parallel coordinates control window hidden")
    
    def get_axis_ranges(self):
        """Get current axis range settings (not used for parallel coordinates)"""
        return {}
    
    def get_selected_variables(self) -> List[str]:
        """Get list of currently selected variables"""
        return [
            var_name
            for var_name, var in self.variable_selection_vars.items()
            if var.get()
        ]


def create_parallel_coordinates_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                            responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> ParallelCoordinatesControlPanel:
    """Factory function to create a parallel coordinates control panel"""
    try:
        control_panel = ParallelCoordinatesControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created parallel coordinates control panel")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating parallel coordinates control panel: {e}")
        raise