"""
IPFindX - Advanced IP Intelligence Toolkit

A professional-grade command-line IP intelligence toolkit designed for cybersecurity 
professionals, network administrators, threat hunters, and OSINT researchers.

Author: Alex Butler
Organization: Vritra Security Organization
License: MIT
Version: 3.0.1
"""

__version__ = "3.0.1"
__author__ = "Alex Butler"
__email__ = None  # No email provided
__license__ = "MIT"
__description__ = "Advanced IP Intelligence Toolkit for cybersecurity professionals"
__url__ = "https://github.com/VritraSecz/IPFindX"

# Import main functions for package usage
try:
    from .ipfindx import main, get_ip_info, display_ip_info, is_valid_ip
    __all__ = ['main', 'get_ip_info', 'display_ip_info', 'is_valid_ip', '__version__']
except ImportError:
    # Minimal setup if imports fail
    __all__ = ['__version__']

# Package metadata
metadata = {
    'name': 'ipfindx',
    'version': __version__,
    'author': __author__,
    'license': __license__,
    'description': __description__,
    'url': __url__,
    'keywords': ['ip', 'intelligence', 'geolocation', 'osint', 'cybersecurity', 'network', 'security'],
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators', 
        'Intended Audience :: Information Technology',
        'Topic :: Security',
        'Topic :: System :: Networking',
        'Topic :: Internet',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ]
}
