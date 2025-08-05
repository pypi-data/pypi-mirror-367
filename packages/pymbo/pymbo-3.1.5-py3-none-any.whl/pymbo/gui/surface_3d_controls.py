"""
3D Surface Plot Controls Module
Specialized control panels for 3D surface plots with extensive customization options
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable
import matplotlib.pyplot as plt
from matplotlib import cm

logger = logging.getLogger(__name__)


class Surface3DControlPanel:
    """Specialized control panel for 3D surface plots with extensive options"""
    
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
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'z_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'z_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        # Add selection controls for response and parameters
        responses_list = list(self.responses_config.keys())
        params_list = list(self.params_config.keys())
        
        self.response_var = tk.StringVar(value=responses_list[0] if responses_list else "")
        self.param1_var = tk.StringVar(value=params_list[0] if params_list else "")
        self.param2_var = tk.StringVar(value=params_list[1] if len(params_list) > 1 else (params_list[0] if params_list else ""))
        
        # Initialize Surface 3D-specific main display controls
        self.show_surface_var = tk.BooleanVar(value=True)
        self.show_data_points_var = tk.BooleanVar(value=False)
        self.show_contours_var = tk.BooleanVar(value=False)
        self.show_wireframe_var = tk.BooleanVar(value=False)
        self.show_colorbar_var = tk.BooleanVar(value=True)
        
        # Advanced controls collapsed state
        self.advanced_expanded_var = tk.BooleanVar(value=False)
        
        # Advanced 3D Surface specific settings
        self.surface_settings = {
            
            # Surface appearance
            'colormap': tk.StringVar(value='viridis'),
            'alpha': tk.DoubleVar(value=0.8),
            'surface_fill': tk.BooleanVar(value=True),
            'edge_color': tk.StringVar(value='black'),
            'edge_alpha': tk.DoubleVar(value=0.3),
            'antialiased': tk.BooleanVar(value=True),
            
            # Mesh resolution
            'x_resolution': tk.IntVar(value=50),
            'y_resolution': tk.IntVar(value=50),
            'interpolation_method': tk.StringVar(value='linear'),
            
            # Lighting and shading
            'lighting_enabled': tk.BooleanVar(value=True),
            'light_elevation': tk.DoubleVar(value=45),
            'light_azimuth': tk.DoubleVar(value=45),
            'shade': tk.BooleanVar(value=True),
            'norm_colors': tk.BooleanVar(value=True),
            
            # View angle
            'elevation': tk.DoubleVar(value=30),
            'azimuth': tk.DoubleVar(value=45),
            'roll': tk.DoubleVar(value=0),
            'distance': tk.DoubleVar(value=10),
            
            # Contour options
            'contour_levels': tk.IntVar(value=10),
            'contour_offset': tk.DoubleVar(value=-0.1),
            'contour_alpha': tk.DoubleVar(value=0.6),
            
            # Color bar
            'colorbar_position': tk.StringVar(value='right'),
            'colorbar_shrink': tk.DoubleVar(value=0.8),
            'colorbar_aspect': tk.IntVar(value=20),
            
            # Data points
            'data_point_size': tk.DoubleVar(value=30),
            'data_point_color': tk.StringVar(value='red'),
            'data_point_alpha': tk.DoubleVar(value=0.8),
            
            # Grid and axes
            'show_grid': tk.BooleanVar(value=True),
            'grid_alpha': tk.DoubleVar(value=0.3),
            'axes_visible': tk.BooleanVar(value=True),
            'tick_density': tk.StringVar(value='medium'),
            
            # Labels and title
            'x_label': tk.StringVar(value='X Parameter'),
            'y_label': tk.StringVar(value='Y Parameter'),
            'z_label': tk.StringVar(value='Response'),
            'title': tk.StringVar(value='3D Surface Plot'),
            'title_size': tk.IntVar(value=12),
            'label_size': tk.IntVar(value=10),
        }
        
        logger.info(f"3D Surface control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ 3D Surface Plot Controls")
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
        
        logger.info(f"3D Surface control window created")
    
    def _create_display_controls(self, parent):
        """Create display option controls"""
        # Plot selection frame (response and parameters)
        selection_frame = ttk.LabelFrame(parent, text="Plot Selection")
        selection_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Response selection
        ttk.Label(selection_frame, text="Response (Z-axis):").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        response_combo = ttk.Combobox(selection_frame, textvariable=self.response_var,
                                     values=list(self.responses_config.keys()), state="readonly", width=20)
        response_combo.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        # response_combo.bind('<<ComboboxSelected>>', self._on_selection_change)  # Removed real-time update
        
        # Parameter 1 selection (X-axis)
        ttk.Label(selection_frame, text="Parameter 1 (X-axis):").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        param1_combo = ttk.Combobox(selection_frame, textvariable=self.param1_var,
                                   values=list(self.params_config.keys()), state="readonly", width=20)
        param1_combo.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        # param1_combo.bind('<<ComboboxSelected>>', self._on_selection_change)  # Removed real-time update
        
        # Parameter 2 selection (Y-axis)
        ttk.Label(selection_frame, text="Parameter 2 (Y-axis):").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        param2_combo = ttk.Combobox(selection_frame, textvariable=self.param2_var,
                                   values=list(self.params_config.keys()), state="readonly", width=20)
        param2_combo.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        # param2_combo.bind('<<ComboboxSelected>>', self._on_selection_change)  # Removed real-time update
        
        # Surface elements frame
        surface_frame = ttk.LabelFrame(parent, text="Surface Elements")
        surface_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(surface_frame, text="Show 3D Surface", 
                       variable=self.show_surface_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(surface_frame, text="Show Wireframe", 
                       variable=self.show_wireframe_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        ttk.Checkbutton(surface_frame, text="Show Contour Lines", 
                       variable=self.show_contours_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Data overlay frame
        data_frame = ttk.LabelFrame(parent, text="Data Overlay")
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(data_frame, text="Show Original Data Points", 
                       variable=self.show_data_points_var,
                       ).pack(anchor='w', padx=10, pady=5)
        
        # Visual elements frame
        visual_frame = ttk.LabelFrame(parent, text="Visual Elements")
        visual_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(visual_frame, text="Show Color Bar", 
                       variable=self.show_colorbar_var,
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
            "• Surface: 3D surface representation of data\n"
            "• Wireframe: Grid lines showing surface structure\n"
            "• Contours: 2D contour lines projected below surface\n"
            "• Data Points: Original experimental observations\n"
            "• Color Bar: Legend showing value-to-color mapping\n\n"
            "💡 Advanced controls include mesh resolution, lighting,\n"
            "view angles, and detailed appearance settings"
        )
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=('TkDefaultFont', 8, 'italic'),
                              foreground='gray',
                              justify='left')
        info_label.pack(padx=10, pady=10, anchor='w')
    
    def _create_advanced_controls(self, parent):
        """Create advanced controls that are collapsed by default"""
        # Resolution controls
        res_frame = ttk.LabelFrame(parent, text="Mesh Resolution")
        res_frame.pack(fill=tk.X, padx=5, pady=5)
        
        res_grid = ttk.Frame(res_frame)
        res_grid.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(res_grid, text="X Resolution:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(res_grid, from_=10, to=200, textvariable=self.surface_settings['x_resolution'],
                   width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(res_grid, text="Y Resolution:").grid(row=1, column=0, sticky='w', pady=(5, 0))
        ttk.Spinbox(res_grid, from_=10, to=200, textvariable=self.surface_settings['y_resolution'],
                   width=10).grid(row=1, column=1, padx=5, pady=(5, 0))
        
        # Appearance controls
        appearance_frame = ttk.LabelFrame(parent, text="Surface Appearance")
        appearance_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(appearance_frame, text="Colormap:").pack(anchor='w', padx=10, pady=2)
        colormap_combo = ttk.Combobox(appearance_frame, textvariable=self.surface_settings['colormap'],
                                     values=['viridis', 'plasma', 'inferno', 'magma', 'coolwarm', 
                                            'RdYlBu', 'seismic', 'terrain'], state="readonly")
        colormap_combo.pack(fill=tk.X, padx=10, pady=2)
        # colormap_combo.bind('<<ComboboxSelected>>', self._on_advanced_change)  # Removed real-time update
        
        ttk.Label(appearance_frame, text="Surface Alpha:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(appearance_frame, from_=0.0, to=1.0, variable=self.surface_settings['alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # View angle controls
        view_frame = ttk.LabelFrame(parent, text="View Angle")
        view_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(view_frame, text="Elevation:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(view_frame, from_=-90, to=90, variable=self.surface_settings['elevation'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(view_frame, text="Azimuth:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(view_frame, from_=0, to=360, variable=self.surface_settings['azimuth'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Lighting controls
        lighting_frame = ttk.LabelFrame(parent, text="Lighting & Shading")
        lighting_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Checkbutton(lighting_frame, text="Enable Lighting", 
                       variable=self.surface_settings['lighting_enabled'],
                       ).pack(anchor='w', padx=10, pady=2)
        ttk.Checkbutton(lighting_frame, text="Enable Shading", 
                       variable=self.surface_settings['shade'],
                       ).pack(anchor='w', padx=10, pady=2)
    
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
        
        # Z-axis section
        z_frame = ttk.LabelFrame(parent, text="Z-Axis Range")
        z_frame.pack(fill=tk.X, padx=10, pady=10)
        
        z_controls = ttk.Frame(z_frame)
        z_controls.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(z_controls, text="Min:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        z_min_entry = ttk.Entry(z_controls, textvariable=self.axis_ranges['z_min']['var'], width=12)
        z_min_entry.grid(row=0, column=1, padx=(0, 10))  
        # z_min_entry.bind('<KeyRelease>', self._on_axis_change)  # Removed real-time update
        
        ttk.Label(z_controls, text="Max:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        z_max_entry = ttk.Entry(z_controls, textvariable=self.axis_ranges['z_max']['var'], width=12)
        z_max_entry.grid(row=0, column=3)
        # z_max_entry.bind('<KeyRelease>', self._on_axis_change)  # Removed real-time update
        
        # Auto scale button
        auto_frame = ttk.Frame(parent)
        auto_frame.pack(pady=10)
        
        auto_button = ttk.Button(auto_frame, text="🔄 Auto Scale All Axes", 
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
    
    def _on_selection_change(self, event=None):
        """Handle response or parameter selection change"""
        self._update_plot()
    
    def _on_display_change(self):
        """Handle display option change"""
        # Ensure at least the surface is shown for a meaningful plot
        if not self.show_surface_var.get() and not self.show_wireframe_var.get() and not self.show_contours_var.get():
            # If user unchecked everything, keep at least surface
            self.show_surface_var.set(True)
        
        self._update_plot()
    
    def _on_advanced_change(self, event=None):
        """Handle advanced option change"""
        self._update_plot()
    
    def _on_axis_change(self, event=None):
        """Handle axis range change"""
        # Parse the ranges and update
        for axis in ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']:
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
        for axis in ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']:
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
        z_min_val, z_max_val, z_auto = self._get_axis_value('z_min')
        
        # Format for main GUI expectation: (min_val, max_val, is_auto)
        ranges['x_axis'] = (x_min_val, x_max_val, x_auto)
        ranges['y_axis'] = (y_min_val, y_max_val, y_auto)
        ranges['z_axis'] = (z_min_val, z_max_val, z_auto)
        
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
            'show_surface': self.show_surface_var.get(),
            'show_wireframe': self.show_wireframe_var.get(),
            'show_contours': self.show_contours_var.get(),
            'show_data_points': self.show_data_points_var.get(),
            'show_colorbar': self.show_colorbar_var.get()
        }
    
    def get_surface_settings(self):
        """Get all current 3D surface settings"""
        settings = {}
        for key, var in self.surface_settings.items():
            try:
                settings[key] = var.get()
            except:
                settings[key] = None
        
        # Add display options
        settings.update(self.get_display_options())
        
        return settings
    
    def get_plot_selection(self):
        """Get the current plot selection (response and parameters)"""
        return {
            'response': self.response_var.get(),
            'param1': self.param1_var.get(),
            'param2': self.param2_var.get()
        }


def create_surface_3d_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                   responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> Surface3DControlPanel:
    """Factory function to create a 3D surface control panel"""
    logger.info(f"Creating specialized 3D surface control panel for {plot_type}")
    control_panel = Surface3DControlPanel(parent, plot_type, params_config, responses_config, update_callback)
    control_panel.create_window()
    return control_panel