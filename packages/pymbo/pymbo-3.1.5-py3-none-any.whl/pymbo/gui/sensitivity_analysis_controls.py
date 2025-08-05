"""
Specialized Control Panel for Sensitivity Analysis
Provides comprehensive controls for sensitivity analysis including algorithm selection and iteration control
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)


class SensitivityAnalysisControlPanel:
    """Specialized control panel for sensitivity analysis with algorithm and iteration controls"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.control_window = None
        
        # Control variables
        self.response_var = tk.StringVar()
        self.algorithm_var = tk.StringVar()
        self.iterations_var = tk.StringVar(value="500")
        self.confidence_var = tk.StringVar(value="0.95")
        self.bootstrap_var = tk.BooleanVar(value=True)
        self.parallel_var = tk.BooleanVar(value=True)
        self.random_seed_var = tk.StringVar(value="42")
        
        # Axis range controls
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        # Algorithm definitions with specific parameters
        self.sensitivity_algorithms = {
            "Variance-based": {
                "code": "variance",
                "description": "Measures how much each parameter contributes to output variance. Higher values indicate more influential parameters.",
                "iterations": {"default": 500, "min": 100, "max": 5000, "step": 100},
                "supports_confidence": True,
                "supports_bootstrap": True
            },
            "Morris Elementary Effects": {
                "code": "morris",
                "description": "Calculates elementary effects using Morris screening method. Shows local sensitivity with statistical confidence.",
                "iterations": {"default": 200, "min": 50, "max": 1000, "step": 50},
                "supports_confidence": True,
                "supports_bootstrap": False
            },
            "Gradient-based": {
                "code": "gradient",
                "description": "Estimates local gradients at multiple points. Good for smooth response surfaces with uncertainty quantification.",
                "iterations": {"default": 300, "min": 100, "max": 2000, "step": 100},
                "supports_confidence": True,
                "supports_bootstrap": True
            },
            "Sobol-like": {
                "code": "sobol",
                "description": "Simplified Sobol indices showing global sensitivity. Robust across different response surface types.",
                "iterations": {"default": 1000, "min": 500, "max": 10000, "step": 500},
                "supports_confidence": True,
                "supports_bootstrap": True
            },
            "GP Lengthscale": {
                "code": "lengthscale",
                "description": "Uses GP model lengthscales directly. Short lengthscales indicate high sensitivity (model intrinsic).",
                "iterations": {"default": 1, "min": 1, "max": 1, "step": 1},
                "supports_confidence": False,
                "supports_bootstrap": False
            },
            "Feature Importance": {
                "code": "feature_importance",
                "description": "Permutation-based importance using variance differences. Model-agnostic sensitivity measure.",
                "iterations": {"default": 100, "min": 10, "max": 500, "step": 10},
                "supports_confidence": True,
                "supports_bootstrap": True
            },
            "FAST (Fourier Amplitude Sensitivity)": {
                "code": "fast",
                "description": "Fourier Amplitude Sensitivity Test for global sensitivity analysis. Computationally efficient for many parameters.",
                "iterations": {"default": 2000, "min": 1000, "max": 20000, "step": 1000},
                "supports_confidence": True,
                "supports_bootstrap": False
            },
            "Delta Moment-Independent": {
                "code": "delta",
                "description": "Moment-independent measure based on probability distributions. Robust to non-normal distributions.",
                "iterations": {"default": 1000, "min": 500, "max": 5000, "step": 500},
                "supports_confidence": True,
                "supports_bootstrap": True
            }
        }
        
        # Initialize with first response and algorithm
        if self.responses_config:
            self.response_var.set(list(self.responses_config.keys())[0])
        self.algorithm_var.set(list(self.sensitivity_algorithms.keys())[0])
        
        logger.info(f"Sensitivity Analysis control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.control_window is not None:
            self.control_window.lift()
            return
        
        self.control_window = tk.Toplevel(self.parent)
        self.control_window.title(f"Sensitivity Analysis Controls")
        self.control_window.geometry("500x700")
        self.control_window.resizable(True, True)
        
        # Configure window style
        self.control_window.configure(bg='#f0f0f0')
        
        # Main container with scrollbar
        main_frame = tk.Frame(self.control_window, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(main_frame, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create control sections
        self._create_response_selection(scrollable_frame)
        self._create_algorithm_selection(scrollable_frame)
        self._create_iteration_controls(scrollable_frame)
        self._create_advanced_options(scrollable_frame)
        self._create_axis_controls(scrollable_frame)
        self._create_action_buttons(scrollable_frame)
        
        # Bind algorithm change to update iteration defaults
        self.algorithm_var.trace('w', self._on_algorithm_change)
        
        # Handle window closing
        self.control_window.protocol("WM_DELETE_WINDOW", self.hide)
    
    def _create_response_selection(self, parent):
        """Create response variable selection"""
        frame = ttk.LabelFrame(parent, text="Response Variable", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        if self.responses_config:
            response_combo = ttk.Combobox(
                frame,
                textvariable=self.response_var,
                values=list(self.responses_config.keys()),
                state="readonly",
                width=30
            )
            response_combo.pack(fill=tk.X)
            # response_combo.bind('<<ComboboxSelected>>', self._on_response_change)  # Removed real-time update
        else:
            tk.Label(frame, text="No response variables available", 
                    fg="red").pack()
    
    def _create_algorithm_selection(self, parent):
        """Create algorithm selection with description"""
        frame = ttk.LabelFrame(parent, text="Sensitivity Analysis Algorithm", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Algorithm dropdown
        algo_combo = ttk.Combobox(
            frame,
            textvariable=self.algorithm_var,
            values=list(self.sensitivity_algorithms.keys()),
            state="readonly",
            width=30
        )
        algo_combo.pack(fill=tk.X, pady=(0, 10))
        # algo_combo.bind('<<ComboboxSelected>>', self._on_algorithm_change)  # Removed real-time update
        
        # Description label
        self.algo_description = tk.Label(
            frame,
            text=self.sensitivity_algorithms[self.algorithm_var.get()]["description"],
            wraplength=450,
            justify=tk.LEFT,
            bg='#f0f0f0',
            fg='#333333'
        )
        self.algo_description.pack(fill=tk.X)
    
    def _create_iteration_controls(self, parent):
        """Create iteration and sampling controls"""
        frame = ttk.LabelFrame(parent, text="Sampling Parameters", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Iterations control with slider and entry
        iter_frame = tk.Frame(frame, bg='#f0f0f0')
        iter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(iter_frame, text="Number of Iterations:", 
                bg='#f0f0f0').pack(anchor=tk.W)
        
        # Get current algorithm settings
        current_algo = self.sensitivity_algorithms[self.algorithm_var.get()]
        iter_settings = current_algo["iterations"]
        
        # Iteration slider
        self.iteration_slider = tk.Scale(
            iter_frame,
            from_=iter_settings["min"],
            to=iter_settings["max"],
            resolution=iter_settings["step"],
            orient=tk.HORIZONTAL,
            variable=self.iterations_var,
            bg='#f0f0f0'
        )
        self.iteration_slider.pack(fill=tk.X, pady=(5, 0))
        self.iteration_slider.set(iter_settings["default"])
        
        # Iteration entry for precise control
        iter_entry_frame = tk.Frame(iter_frame, bg='#f0f0f0')
        iter_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(iter_entry_frame, text="Exact value:", 
                bg='#f0f0f0').pack(side=tk.LEFT)
        iter_entry = tk.Entry(iter_entry_frame, textvariable=self.iterations_var, width=10)
        iter_entry.pack(side=tk.LEFT, padx=(5, 0))
        # iter_entry.bind('<Return>', self._on_iterations_change)  # Removed real-time update
        # iter_entry.bind('<FocusOut>', self._on_iterations_change)  # Removed real-time update
        
        # Confidence level (if supported)
        self.confidence_frame = tk.Frame(frame, bg='#f0f0f0')
        if current_algo.get("supports_confidence", False):
            self.confidence_frame.pack(fill=tk.X, pady=(0, 5))
            
            tk.Label(self.confidence_frame, text="Confidence Level:", 
                    bg='#f0f0f0').pack(anchor=tk.W)
            
            confidence_combo = ttk.Combobox(
                self.confidence_frame,
                textvariable=self.confidence_var,
                values=["0.90", "0.95", "0.99"],
                state="readonly",
                width=10
            )
            confidence_combo.pack(anchor=tk.W, pady=(2, 0))
        
        # Random seed control
        seed_frame = tk.Frame(frame, bg='#f0f0f0')
        seed_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(seed_frame, text="Random Seed (for reproducibility):", 
                bg='#f0f0f0').pack(anchor=tk.W)
        seed_entry = tk.Entry(seed_frame, textvariable=self.random_seed_var, width=10)
        seed_entry.pack(anchor=tk.W, pady=(2, 0))
    
    def _create_advanced_options(self, parent):
        """Create advanced analysis options"""
        frame = ttk.LabelFrame(parent, text="Advanced Options", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # Get current algorithm settings
        current_algo = self.sensitivity_algorithms[self.algorithm_var.get()]
        
        # Bootstrap option (if supported)
        self.bootstrap_check = None
        if current_algo.get("supports_bootstrap", False):
            self.bootstrap_check = tk.Checkbutton(
                frame,
                text="Use Bootstrap Resampling for Error Estimates",
                variable=self.bootstrap_var,
                bg='#f0f0f0'
            )
            self.bootstrap_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Parallel processing option
        parallel_check = tk.Checkbutton(
            frame,
            text="Enable Parallel Processing (when available)",
            variable=self.parallel_var,
            bg='#f0f0f0'
        )
        parallel_check.pack(anchor=tk.W, pady=(0, 5))
        
        # Algorithm-specific options placeholder
        self.algo_specific_frame = tk.Frame(frame, bg='#f0f0f0')
        self.algo_specific_frame.pack(fill=tk.X, pady=(5, 0))
        
        self._create_algorithm_specific_options()
    
    def _create_algorithm_specific_options(self):
        """Create algorithm-specific options"""
        # Clear existing options if frame exists
        if hasattr(self, 'algo_specific_frame') and self.algo_specific_frame:
            for widget in self.algo_specific_frame.winfo_children():
                widget.destroy()
        else:
            # Frame doesn't exist yet, skip creating specific options
            return
        
        current_algo = self.algorithm_var.get()
        
        if current_algo == "Morris Elementary Effects":
            # Morris-specific options
            tk.Label(self.algo_specific_frame, text="Morris-specific Options:", 
                    bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            
            self.morris_trajectories_var = tk.StringVar(value="10")
            traj_frame = tk.Frame(self.algo_specific_frame, bg='#f0f0f0')
            traj_frame.pack(fill=tk.X, pady=(2, 0))
            tk.Label(traj_frame, text="Number of trajectories:", bg='#f0f0f0').pack(side=tk.LEFT)
            tk.Entry(traj_frame, textvariable=self.morris_trajectories_var, width=5).pack(side=tk.LEFT, padx=(5, 0))
            
        elif current_algo == "Sobol-like":
            # Sobol-specific options
            tk.Label(self.algo_specific_frame, text="Sobol-specific Options:", 
                    bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            
            self.sobol_order_var = tk.StringVar(value="1")
            order_frame = tk.Frame(self.algo_specific_frame, bg='#f0f0f0')
            order_frame.pack(fill=tk.X, pady=(2, 0))
            tk.Label(order_frame, text="Sobol order:", bg='#f0f0f0').pack(side=tk.LEFT)
            order_combo = ttk.Combobox(order_frame, textvariable=self.sobol_order_var,
                                     values=["1", "2"], state="readonly", width=5)
            order_combo.pack(side=tk.LEFT, padx=(5, 0))
            
        elif current_algo == "FAST (Fourier Amplitude Sensitivity)":
            # FAST-specific options
            tk.Label(self.algo_specific_frame, text="FAST-specific Options:", 
                    bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            
            self.fast_M_var = tk.StringVar(value="4")
            M_frame = tk.Frame(self.algo_specific_frame, bg='#f0f0f0')
            M_frame.pack(fill=tk.X, pady=(2, 0))
            tk.Label(M_frame, text="Interference parameter (M):", bg='#f0f0f0').pack(side=tk.LEFT)
            tk.Entry(M_frame, textvariable=self.fast_M_var, width=5).pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_axis_controls(self, parent):
        """Create axis range controls"""
        frame = ttk.LabelFrame(parent, text="Plot Axis Ranges", padding="10")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # X-axis controls
        x_frame = tk.Frame(frame, bg='#f0f0f0')
        x_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(x_frame, text="X-axis:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        x_entry_frame = tk.Frame(x_frame, bg='#f0f0f0')
        x_entry_frame.pack(fill=tk.X, pady=(2, 0))
        
        tk.Label(x_entry_frame, text="Min:", bg='#f0f0f0').pack(side=tk.LEFT)
        x_min_entry = tk.Entry(x_entry_frame, textvariable=self.axis_ranges['x_min']['var'], width=8)
        x_min_entry.pack(side=tk.LEFT, padx=(5, 10))
        # x_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        tk.Label(x_entry_frame, text="Max:", bg='#f0f0f0').pack(side=tk.LEFT)
        x_max_entry = tk.Entry(x_entry_frame, textvariable=self.axis_ranges['x_max']['var'], width=8)
        x_max_entry.pack(side=tk.LEFT, padx=(5, 10))
        # x_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # x_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        tk.Button(x_entry_frame, text="Auto", command=lambda: self._set_auto_range('x'),
                 bg='lightblue').pack(side=tk.LEFT, padx=(5, 0))
        
        # Y-axis controls
        y_frame = tk.Frame(frame, bg='#f0f0f0')
        y_frame.pack(fill=tk.X)
        
        tk.Label(y_frame, text="Y-axis:", bg='#f0f0f0', font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        y_entry_frame = tk.Frame(y_frame, bg='#f0f0f0')
        y_entry_frame.pack(fill=tk.X, pady=(2, 0))
        
        tk.Label(y_entry_frame, text="Min:", bg='#f0f0f0').pack(side=tk.LEFT)
        y_min_entry = tk.Entry(y_entry_frame, textvariable=self.axis_ranges['y_min']['var'], width=8)
        y_min_entry.pack(side=tk.LEFT, padx=(5, 10))
        # y_min_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_min_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        tk.Label(y_entry_frame, text="Max:", bg='#f0f0f0').pack(side=tk.LEFT)
        y_max_entry = tk.Entry(y_entry_frame, textvariable=self.axis_ranges['y_max']['var'], width=8)
        y_max_entry.pack(side=tk.LEFT, padx=(5, 10))
        # y_max_entry.bind('<Return>', self._on_axis_change)  # Removed real-time update
        # y_max_entry.bind('<FocusOut>', self._on_axis_change)  # Removed real-time update
        
        tk.Button(y_entry_frame, text="Auto", command=lambda: self._set_auto_range('y'),
                 bg='lightblue').pack(side=tk.LEFT, padx=(5, 0))
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.X, pady=(10, 0))
        
        # Update plot button
        update_btn = tk.Button(
            frame,
            text="Update Sensitivity Analysis",
            command=self._update_plot,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        )
        update_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset to defaults button
        reset_btn = tk.Button(
            frame,
            text="Reset to Defaults",
            command=self._reset_to_defaults,
            bg='#FF9800',
            fg='white',
            padx=20,
            pady=5
        )
        reset_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export settings button
        export_btn = tk.Button(
            frame,
            text="Export Settings",
            command=self._export_settings,
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=5
        )
        export_btn.pack(side=tk.LEFT)
    
    def _on_algorithm_change(self, *args):
        """Handle algorithm selection change"""
        current_algo = self.algorithm_var.get()
        algo_info = self.sensitivity_algorithms[current_algo]
        
        # Update description
        if hasattr(self, 'algo_description'):
            self.algo_description.config(text=algo_info["description"])
        
        # Update iteration slider range and default
        iter_settings = algo_info["iterations"]
        if hasattr(self, 'iteration_slider'):
            self.iteration_slider.config(
                from_=iter_settings["min"],
                to=iter_settings["max"],
                resolution=iter_settings["step"]
            )
            self.iteration_slider.set(iter_settings["default"])
            self.iterations_var.set(str(iter_settings["default"]))
        
        # Update confidence frame visibility
        if hasattr(self, 'confidence_frame'):
            if algo_info.get("supports_confidence", False):
                self.confidence_frame.pack(fill=tk.X, pady=(0, 5))
            else:
                self.confidence_frame.pack_forget()
        
        # Update bootstrap checkbox visibility
        if hasattr(self, 'bootstrap_check') and self.bootstrap_check:
            if algo_info.get("supports_bootstrap", False):
                self.bootstrap_check.pack(anchor=tk.W, pady=(0, 5))
            else:
                self.bootstrap_check.pack_forget()
        
        # Update algorithm-specific options
        self._create_algorithm_specific_options()
        
        logger.info(f"Algorithm changed to: {current_algo}")
    
    def _on_response_change(self, event=None):
        """Handle response variable change"""
        logger.info(f"Response changed to: {self.response_var.get()}")
        self._update_plot()
    
    def _on_iterations_change(self, event=None):
        """Handle manual iteration count change"""
        try:
            iterations = int(self.iterations_var.get())
            current_algo = self.sensitivity_algorithms[self.algorithm_var.get()]
            iter_settings = current_algo["iterations"]
            
            # Clamp to valid range
            iterations = max(iter_settings["min"], min(iter_settings["max"], iterations))
            self.iterations_var.set(str(iterations))
            
            if hasattr(self, 'iteration_slider'):
                self.iteration_slider.set(iterations)
                
        except ValueError:
            # Reset to default if invalid
            current_algo = self.sensitivity_algorithms[self.algorithm_var.get()]
            default_iter = current_algo["iterations"]["default"]
            self.iterations_var.set(str(default_iter))
            if hasattr(self, 'iteration_slider'):
                self.iteration_slider.set(default_iter)
    
    def _on_axis_change(self, event=None):
        """Handle axis range change"""
        # Update auto flags
        for axis in ['x_min', 'x_max', 'y_min', 'y_max']:
            value = self.axis_ranges[axis]['var'].get().strip().lower()
            self.axis_ranges[axis]['auto'] = (value == 'auto' or value == '')
        
        logger.debug("Axis ranges updated")
        self._update_plot()
    
    def _set_auto_range(self, axis):
        """Set axis range to auto"""
        if axis == 'x':
            self.axis_ranges['x_min']['var'].set('auto')
            self.axis_ranges['x_max']['var'].set('auto')
            self.axis_ranges['x_min']['auto'] = True
            self.axis_ranges['x_max']['auto'] = True
        else:  # y
            self.axis_ranges['y_min']['var'].set('auto')
            self.axis_ranges['y_max']['var'].set('auto')
            self.axis_ranges['y_min']['auto'] = True
            self.axis_ranges['y_max']['auto'] = True
        
        self._update_plot()
    
    def _reset_to_defaults(self):
        """Reset all settings to defaults"""
        # Reset algorithm to first one
        first_algo = list(self.sensitivity_algorithms.keys())[0]
        self.algorithm_var.set(first_algo)
        
        # This will trigger _on_algorithm_change and reset iterations
        self._on_algorithm_change()
        
        # Reset other settings
        self.confidence_var.set("0.95")
        self.bootstrap_var.set(True)
        self.parallel_var.set(True)
        self.random_seed_var.set("42")
        
        # Reset axis ranges
        for axis in ['x_min', 'x_max', 'y_min', 'y_max']:
            self.axis_ranges[axis]['var'].set('auto')
            self.axis_ranges[axis]['auto'] = True
        
        logger.info("Settings reset to defaults")
        self._update_plot()
    
    def _export_settings(self):
        """Export current settings to a dictionary"""
        settings = {
            "response": self.response_var.get(),
            "algorithm": self.algorithm_var.get(),
            "algorithm_code": self.sensitivity_algorithms[self.algorithm_var.get()]["code"],
            "iterations": self.iterations_var.get(),
            "confidence": self.confidence_var.get(),
            "bootstrap": self.bootstrap_var.get(),
            "parallel": self.parallel_var.get(),
            "random_seed": self.random_seed_var.get(),
            "axis_ranges": {
                axis: {"value": info['var'].get(), "auto": info['auto']}
                for axis, info in self.axis_ranges.items()
            }
        }
        
        # Add algorithm-specific settings
        current_algo = self.algorithm_var.get()
        if current_algo == "Morris Elementary Effects" and hasattr(self, 'morris_trajectories_var'):
            settings["morris_trajectories"] = self.morris_trajectories_var.get()
        elif current_algo == "Sobol-like" and hasattr(self, 'sobol_order_var'):
            settings["sobol_order"] = self.sobol_order_var.get()
        elif current_algo == "FAST (Fourier Amplitude Sensitivity)" and hasattr(self, 'fast_M_var'):
            settings["fast_M"] = self.fast_M_var.get()
        
        logger.info(f"Exported sensitivity analysis settings: {settings}")
        return settings
    
    def _update_plot(self):
        """Update the sensitivity analysis plot"""
        if self.update_callback:
            try:
                # Try calling without arguments first (for update_all_plots)
                self.update_callback()
            except TypeError:
                # If that fails, try with settings (for callbacks that expect settings)
                settings = self._export_settings()
                self.update_callback(settings)
    
    def get_sensitivity_settings(self) -> Dict[str, Any]:
        """Get current sensitivity analysis settings"""
        return self._export_settings()
    
    def get_axis_ranges(self) -> Dict[str, Any]:
        """Get current axis ranges for the plot"""
        ranges = {}
        
        # X-axis range
        if not self.axis_ranges['x_min']['auto'] and not self.axis_ranges['x_max']['auto']:
            try:
                x_min = float(self.axis_ranges['x_min']['var'].get())
                x_max = float(self.axis_ranges['x_max']['var'].get())
                ranges['x_range'] = [x_min, x_max]
            except ValueError:
                pass
        
        # Y-axis range
        if not self.axis_ranges['y_min']['auto'] and not self.axis_ranges['y_max']['auto']:
            try:
                y_min = float(self.axis_ranges['y_min']['var'].get())
                y_max = float(self.axis_ranges['y_max']['var'].get())
                ranges['y_range'] = [y_min, y_max]
            except ValueError:
                pass
        
        return ranges
    
    def show(self):
        """Show the control panel window"""
        if self.control_window is None:
            self.create_window()
        else:
            self.control_window.deiconify()
            self.control_window.lift()
        logger.info(f"Sensitivity analysis control panel shown for {self.plot_type}")
    
    def hide(self):
        """Hide the control panel window"""
        if self.control_window:
            self.control_window.withdraw()
        logger.info(f"Sensitivity analysis control panel hidden for {self.plot_type}")
    
    def destroy(self):
        """Destroy the control panel window"""
        if self.control_window:
            self.control_window.destroy()
            self.control_window = None
        logger.info(f"Sensitivity analysis control panel destroyed for {self.plot_type}")


def create_sensitivity_analysis_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                             responses_config: Dict[str, Any] = None, 
                                             update_callback: Callable = None) -> SensitivityAnalysisControlPanel:
    """Factory function to create a sensitivity analysis control panel"""
    try:
        control_panel = SensitivityAnalysisControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created sensitivity analysis control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating sensitivity analysis control panel for {plot_type}: {e}")
        raise


__all__ = [
    'SensitivityAnalysisControlPanel',
    'create_sensitivity_analysis_control_panel'
]