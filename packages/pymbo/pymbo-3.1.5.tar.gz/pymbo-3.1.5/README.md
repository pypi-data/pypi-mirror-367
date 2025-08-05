# 🚀 PyMBO - Python Multi-objective Bayesian Optimization

[![PyPI version](https://badge.fury.io/py/pymbo.svg)](https://pypi.org/project/pymbo/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![GitHub stars](https://img.shields.io/github/stars/jakub-jagielski/pymbo)](https://github.com/jakub-jagielski/pymbo/stargazers)

> **A comprehensive multi-objective Bayesian optimization framework with advanced visualization and screening capabilities.**

Transform your optimization challenges with PyMBO's intuitive GUI, powerful algorithms, and real-time visualizations. Perfect for researchers, engineers, and data scientists working with complex parameter spaces.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🎯 **Multi-objective Optimization** | Advanced Bayesian optimization with PyTorch/BoTorch backend |
| 📊 **Real-time Visualizations** | Interactive acquisition function heatmaps and 3D surfaces |
| 🔍 **SGLBO Screening** | Efficient parameter space exploration before detailed optimization |
| 🎮 **Interactive GUI** | User-friendly interface with drag-and-drop controls |
| 📈 **Comprehensive Analytics** | Parameter importance, correlation analysis, and trend visualization |
| 💾 **Export & Reporting** | Generate detailed reports in multiple formats |
| 🔬 **Scientific Utilities** | Built-in validation and analysis tools |

## 🚀 Quick Start

### Installation (Recommended)

```bash
pip install pymbo
```

### Run the Application

```bash
python -m pymbo
```

**That's it!** 🎉 PyMBO will launch with a modern GUI ready for your optimization projects.

### Alternative Installation

If you prefer to install from source:

```bash
git clone https://github.com/jakub-jagielski/pymbo.git
cd pymbo
pip install -r requirements.txt
python main.py
```

## 🎮 How to Use PyMBO

### 🖥️ **Graphical Interface**
Launch the GUI and follow these simple steps:

1. **🔧 Configure Parameters** - Define your optimization variables (continuous, discrete, categorical)
2. **🎯 Set Objectives** - Specify what you want to optimize (maximize, minimize, or target values)  
3. **▶️ Run Optimization** - Watch real-time visualizations as PyMBO finds optimal solutions
4. **📊 Analyze Results** - Export detailed reports and generate publication-ready plots

### 🔬 **SGLBO Screening Module**
For complex parameter spaces, start with efficient screening:

```bash
python -m pymbo  # Launch GUI → Select "SGLBO Screening"
```

**Screening Features:**
- 📈 **Response Trends Over Time** - Track optimization progress
- 📊 **Parameter Importance Analysis** - Identify key variables  
- 🔄 **Correlation Matrix** - Understand parameter interactions
- 🎯 **Design Space Generation** - Create focused regions for detailed optimization

### 💻 **Programmatic Usage** 

```python
from pymbo import EnhancedMultiObjectiveOptimizer, SimpleController

# Create optimizer instance
optimizer = EnhancedMultiObjectiveOptimizer(
    bounds=[(0, 10), (0, 10)],
    objectives=['maximize']
)

# Run optimization
controller = SimpleController(optimizer)
controller.run_optimization()
```

## 🏗️ Architecture

PyMBO is built with a modular architecture for maximum flexibility:

```
pymbo/
├── 🧠 core/          # Optimization algorithms and controllers
├── 🎮 gui/           # Interactive graphical interface
├── 🔍 screening/     # SGLBO screening module  
└── 🛠️ utils/         # Plotting, reporting, and scientific utilities
```

### 🔍 **Advanced Screening (SGLBO)**

The **Stochastic Gradient Line Bayesian Optimization** module revolutionizes parameter space exploration:

**Why Use SGLBO Screening?**
- ⚡ **10x Faster** initial exploration vs. full Bayesian optimization  
- 🎯 **Smart Parameter Selection** - Focus on variables that matter most
- 📊 **Rich Visualizations** - 4 different plot types for comprehensive analysis
- 🔄 **Seamless Integration** - Export results directly to main optimization

```python
from pymbo.screening import ScreeningOptimizer

# Quick screening setup
optimizer = ScreeningOptimizer(
    params_config=config["parameters"],
    responses_config=config["responses"]
)

# Get results with built-in analysis
results = optimizer.run_screening()
```

## 🎓 Academic Use & Licensing

### 📜 **License**: Creative Commons BY-NC-ND 4.0

PyMBO is **free for academic and research use**! 

✅ **Permitted:**
- Academic research projects
- Publishing results in journals, theses, conferences  
- Educational use in universities
- Non-commercial research applications

❌ **Not Permitted:**
- Commercial applications without license
- Redistribution of modified versions

> 📖 **For Researchers**: You can freely use PyMBO in your research and publish your findings. We encourage academic use!

## 📚 How to Cite

If PyMBO helps your research, please cite it:

```bibtex
@software{jagielski2025pymbo,
  author = {Jakub Jagielski},
  title = {PyMBO: A Python library for multivariate Bayesian optimization and stochastic Bayesian screening},
  version = {3.1.2},
  year = {2025},
  url = {https://github.com/jakub-jagielski/pymbo}
}
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. 🍴 **Fork** the repository
2. 🌿 **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. 💻 **Make** your changes  
4. ✅ **Add** tests if applicable
5. 📝 **Commit** changes (`git commit -m 'Add amazing feature'`)
6. 📤 **Push** to branch (`git push origin feature/amazing-feature`)
7. 🔄 **Open** a Pull Request

### 🐛 **Found a Bug?**
[Open an issue](https://github.com/jakub-jagielski/pymbo/issues) with:
- Clear description of the problem
- Steps to reproduce  
- Expected vs actual behavior
- System information (OS, Python version)

## ⭐ **Show Your Support**

If PyMBO helps your work, please:
- ⭐ **Star** this repository
- 🐦 **Share** with your colleagues  
- 📝 **Cite** in your publications
- 🤝 **Contribute** improvements

---

<div align="center">

**Made with ❤️ for the optimization community**

[⬆️ Back to Top](#-pymbo---python-multi-objective-bayesian-optimization)

</div>