"""
Smart Defaults and Auto-Configuration System for PyMBO
Automatically optimizes settings based on system capabilities and usage patterns
"""

import torch
import psutil
import platform
import logging
from typing import Dict, Any, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemCapabilityDetector:
    """Detect system capabilities for optimization"""
    
    def __init__(self):
        self.capabilities = self._detect_all_capabilities()
        
    def _detect_all_capabilities(self) -> Dict[str, Any]:
        """Comprehensive system capability detection"""
        caps = {}
        
        # Hardware detection
        caps['cpu_count'] = psutil.cpu_count(logical=False)
        caps['logical_cpu_count'] = psutil.cpu_count(logical=True)
        caps['total_memory_gb'] = psutil.virtual_memory().total / (1024**3)
        caps['available_memory_gb'] = psutil.virtual_memory().available / (1024**3)
        
        # GPU detection
        caps['gpu_available'] = torch.cuda.is_available()
        if caps['gpu_available']:
            caps['gpu_count'] = torch.cuda.device_count()
            caps['gpu_memory_gb'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            caps['gpu_name'] = torch.cuda.get_device_name(0)
        else:
            caps['gpu_count'] = 0
            caps['gpu_memory_gb'] = 0
            caps['gpu_name'] = None
        
        # Platform info
        caps['platform'] = platform.system()
        caps['python_version'] = platform.python_version()
        
        # Performance characteristics
        caps['is_high_performance'] = (
            caps['cpu_count'] >= 4 and 
            caps['total_memory_gb'] >= 8 and
            caps['gpu_available']
        )
        caps['is_low_resource'] = (
            caps['cpu_count'] <= 2 or 
            caps['total_memory_gb'] <= 4
        )
        
        logger.info(f"System capabilities detected: {caps}")
        return caps
    
    def get_optimal_settings(self) -> Dict[str, Any]:
        """Generate optimal settings based on capabilities"""
        settings = {}
        
        # Memory settings
        if self.capabilities['total_memory_gb'] >= 16:
            settings['plot_cache_size'] = 100
            settings['batch_size'] = 1024
        elif self.capabilities['total_memory_gb'] >= 8:
            settings['plot_cache_size'] = 50
            settings['batch_size'] = 512
        else:
            settings['plot_cache_size'] = 20
            settings['batch_size'] = 256
        
        # CPU settings
        if self.capabilities['cpu_count'] >= 8:
            settings['num_workers'] = 6
            settings['enable_parallel_training'] = True
        elif self.capabilities['cpu_count'] >= 4:
            settings['num_workers'] = 3
            settings['enable_parallel_training'] = True
        else:
            settings['num_workers'] = 1
            settings['enable_parallel_training'] = False
        
        # GPU settings
        if self.capabilities['gpu_available']:
            if self.capabilities['gpu_memory_gb'] >= 8:
                settings['enable_gpu'] = True
                settings['gpu_batch_size'] = 2048
                settings['use_mixed_precision'] = True
            elif self.capabilities['gpu_memory_gb'] >= 4:
                settings['enable_gpu'] = True
                settings['gpu_batch_size'] = 1024
                settings['use_mixed_precision'] = True
            else:
                settings['enable_gpu'] = False  # Low VRAM
        else:
            settings['enable_gpu'] = False
            settings['gpu_batch_size'] = 0
            settings['use_mixed_precision'] = False
        
        # Performance vs Quality trade-offs
        if self.capabilities['is_high_performance']:
            settings['plot_quality'] = 'high'
            settings['model_complexity'] = 'high'
            settings['acquisition_samples'] = 2048
        elif self.capabilities['is_low_resource']:
            settings['plot_quality'] = 'medium'
            settings['model_complexity'] = 'low'
            settings['acquisition_samples'] = 512
        else:
            settings['plot_quality'] = 'high'
            settings['model_complexity'] = 'medium'
            settings['acquisition_samples'] = 1024
        
        return settings

class UserPreferenceLearner:
    """Learn user preferences and adapt interface"""
    
    def __init__(self, preferences_file: str = "user_preferences.json"):
        self.preferences_file = Path(preferences_file)
        self.preferences = self._load_preferences()
        self.usage_stats = self.preferences.get('usage_stats', {})
        
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load preferences: {e}")
        
        return self._get_default_preferences()
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Default user preferences"""
        return {
            'interface_theme': 'modern',
            'default_plot_type': 'pareto',
            'auto_update_plots': True,
            'show_advanced_options': False,
            'preferred_export_format': 'png',
            'usage_stats': {},
            'feature_usage': {},
            'workflow_patterns': []
        }
    
    def save_preferences(self):
        """Save preferences to file"""
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save preferences: {e}")
    
    def track_feature_usage(self, feature_name: str):
        """Track which features user uses most"""
        if 'feature_usage' not in self.preferences:
            self.preferences['feature_usage'] = {}
        
        current_count = self.preferences['feature_usage'].get(feature_name, 0)
        self.preferences['feature_usage'][feature_name] = current_count + 1
        
        # Auto-save every 10 uses
        if sum(self.preferences['feature_usage'].values()) % 10 == 0:
            self.save_preferences()
    
    def get_personalized_settings(self) -> Dict[str, Any]:
        """Get settings personalized to user behavior"""
        settings = {}
        
        # Most used plot type becomes default
        feature_usage = self.preferences.get('feature_usage', {})
        plot_features = {k: v for k, v in feature_usage.items() if 'plot' in k}
        if plot_features:
            most_used_plot = max(plot_features, key=plot_features.get)
            settings['default_plot_type'] = most_used_plot.replace('_plot', '')
        
        # Show advanced options if user frequently uses them
        advanced_features = ['3d_surface', 'sensitivity_analysis', 'gp_uncertainty']
        advanced_usage = sum(feature_usage.get(f, 0) for f in advanced_features)
        settings['show_advanced_options'] = advanced_usage > 20
        
        # Adjust update frequency based on usage patterns
        total_usage = sum(feature_usage.values())
        if total_usage > 100:  # Experienced user
            settings['auto_update_plots'] = False  # Let them control updates
            settings['show_performance_tips'] = False
        else:  # New user
            settings['auto_update_plots'] = True
            settings['show_performance_tips'] = True
        
        return settings

class SmartDefaultsManager:
    """Main class for managing smart defaults and auto-configuration"""
    
    def __init__(self):
        self.system_detector = SystemCapabilityDetector()
        self.preference_learner = UserPreferenceLearner()
        self.current_settings = {}
        
    def get_optimal_configuration(self) -> Dict[str, Any]:
        """Get optimal configuration combining system and user preferences"""
        # Start with system-optimized settings
        settings = self.system_detector.get_optimal_settings()
        
        # Overlay with user preferences
        user_settings = self.preference_learner.get_personalized_settings()
        settings.update(user_settings)
        
        # Add smart defaults for common scenarios
        settings.update(self._get_smart_defaults())
        
        self.current_settings = settings
        logger.info(f"Optimal configuration: {settings}")
        
        return settings
    
    def _get_smart_defaults(self) -> Dict[str, Any]:
        """Smart defaults based on common usage patterns"""
        defaults = {}
        
        # Auto-configure sampling strategy
        if self.system_detector.capabilities['is_high_performance']:
            defaults['initial_sampling_method'] = 'LHS'  # Better for powerful systems
            defaults['initial_sample_count'] = 20
        else:
            defaults['initial_sampling_method'] = 'random'  # Faster for weak systems
            defaults['initial_sample_count'] = 10
        
        # Auto-configure acquisition function parameters
        if self.system_detector.capabilities['gpu_available']:
            defaults['acquisition_optimization_restarts'] = 20
            defaults['acquisition_raw_samples'] = 2048
        else:
            defaults['acquisition_optimization_restarts'] = 10
            defaults['acquisition_raw_samples'] = 512
        
        # Auto-configure plot settings
        if self.system_detector.capabilities['total_memory_gb'] >= 8:
            defaults['plot_dpi'] = 150  # High quality
            defaults['plot_animation'] = True
        else:
            defaults['plot_dpi'] = 100  # Standard quality
            defaults['plot_animation'] = False
        
        return defaults
    
    def track_user_action(self, action: str, context: Dict[str, Any] = None):
        """Track user actions for learning preferences"""
        self.preference_learner.track_feature_usage(action)
        
        # Update settings if significant pattern changes detected
        if self._should_update_settings():
            self.current_settings = self.get_optimal_configuration()
    
    def _should_update_settings(self) -> bool:
        """Check if settings should be updated based on usage"""
        feature_usage = self.preference_learner.preferences.get('feature_usage', {})
        total_usage = sum(feature_usage.values())
        
        # Update every 50 actions
        return total_usage > 0 and total_usage % 50 == 0
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance improvement recommendations"""
        recommendations = []
        caps = self.system_detector.capabilities
        
        if not caps['gpu_available'] and caps['total_memory_gb'] >= 8:
            recommendations.append("Consider adding a GPU for 5-10x faster optimization")
        
        if caps['total_memory_gb'] < 8:
            recommendations.append("Additional RAM would improve plot caching performance")
        
        if caps['cpu_count'] >= 4 and not self.current_settings.get('enable_parallel_training'):
            recommendations.append("Enable parallel training in settings for faster model building")
        
        feature_usage = self.preference_learner.preferences.get('feature_usage', {})
        if feature_usage.get('update_all_plots', 0) > 50:
            recommendations.append("Consider disabling auto-plot updates for better performance")
        
        return recommendations
    
    def apply_settings_to_optimizer(self, optimizer):
        """Apply smart settings to optimizer instance"""
        settings = self.current_settings
        
        if hasattr(optimizer, 'num_restarts'):
            optimizer.num_restarts = settings.get('acquisition_optimization_restarts', 10)
        
        if hasattr(optimizer, 'raw_samples'):
            optimizer.raw_samples = settings.get('acquisition_raw_samples', 512)
        
        if hasattr(optimizer, 'device') and settings.get('enable_gpu'):
            optimizer.device = torch.device('cuda')
        
        logger.info("Smart settings applied to optimizer")

# Global instance
smart_defaults = SmartDefaultsManager()

def get_smart_configuration() -> Dict[str, Any]:
    """Get smart configuration for the application"""
    return smart_defaults.get_optimal_configuration()

def track_user_action(action: str, context: Dict[str, Any] = None):
    """Track user action for preference learning"""
    smart_defaults.track_user_action(action, context)

def get_recommendations() -> List[str]:
    """Get performance recommendations"""
    return smart_defaults.get_performance_recommendations()

# Auto-configuration decorator
def auto_configure(func):
    """Decorator to auto-configure functions with smart defaults"""
    def wrapper(*args, **kwargs):
        # Apply smart defaults to function parameters
        config = smart_defaults.get_optimal_configuration()
        
        # Override with any explicitly provided kwargs
        smart_kwargs = {k: v for k, v in config.items() if k not in kwargs}
        kwargs.update(smart_kwargs)
        
        return func(*args, **kwargs)
    
    return wrapper