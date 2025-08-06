"""
CareSurveyor - Survey Automation Pipeline for Clinical Studies

A high-level Python package that simplifies Google Forms automation 
for clinical research and medical surveys.

Usage:
    import caresurveyor as cs
    
    # Create study using convenience function
    study = cs.create_study("My Study")
    
    # Quick form creation
    form = cs.quick_form("Patient Survey", "oncology")
    
    # Or use the class directly
    surveyor = cs.CareSurveyor("My Study")
"""

__version__ = "0.1.1"
__author__ = "CareSurveyor Team"
__email__ = "contact@caresurveyor.dev"
__license__ = "MIT"

# Core imports
from .core import CareSurveyor
from .templates import ClinicalTemplates
from .utils import get_version

# Convenience functions for module-style usage
def create_study(study_name):
    """
    Convenience function for import caresurveyor as cs usage
    
    Usage:
        import caresurveyor as cs
        study = cs.create_study("My Research")
    """
    return CareSurveyor(study_name)

def quick_form(title, form_type="basic"):
    """
    Quick form creation for one-liner usage
    
    Usage:
        import caresurveyor as cs
        form = cs.quick_form("Patient Survey", "oncology")
    """
    surveyor = CareSurveyor(f"Quick_{title}")
    return surveyor.clinical_form(form_type)

def version():
    """Get version info"""
    return __version__

# Package metadata - support both import styles
__all__ = [
    "CareSurveyor",           
    "ClinicalTemplates", 
    "get_version",
    "create_study",           
    "quick_form",             
    "version",                
]

# Development status notice
import warnings
warnings.warn(
    "🚧 CareSurveyor is currently in early development. "
    "API may change in future versions. "
    "This is a placeholder release to reserve the package name.",
    UserWarning,
    stacklevel=2
)
