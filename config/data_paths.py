"""
Data Path Configuration Module

Centralized configuration for all external data paths used by import scripts.
Supports multiple environments and flexible path resolution.
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class DataPaths:
    """Configuration for external data paths."""
    
    # Base paths
    lotro_companion_root: Path
    project_root: Path
    
    # Data file paths
    items_xml: Path
    progressions_xml: Path
    dps_tables_xml: Path
    
    # Icon paths
    icons_source_dir: Path
    icons_dest_dir: Path
    
    # Validation
    def validate(self) -> Optional[str]:
        """Validate that all required paths exist.
        
        Returns:
            Optional[str]: Error message if validation fails, None if valid
        """
        required_files = [
            (self.items_xml, "items.xml"),
            (self.progressions_xml, "progressions.xml"),
            (self.dps_tables_xml, "dpsTables.xml"),
        ]
        
        for file_path, name in required_files:
            if not file_path.exists():
                return f"Required file not found: {name} at {file_path}"
        
        if not self.lotro_companion_root.exists():
            return f"LOTRO Companion root directory not found: {self.lotro_companion_root}"
        
        if not self.icons_source_dir.exists():
            return f"Icons source directory not found: {self.icons_source_dir}"
        
        return None
    
    def get_paths_dict(self) -> Dict[str, Path]:
        """Get all paths as a dictionary for easy access."""
        return {
            'lotro_companion_root': self.lotro_companion_root,
            'items_xml': self.items_xml,
            'progressions_xml': self.progressions_xml,
            'dps_tables_xml': self.dps_tables_xml,
            'icons_source_dir': self.icons_source_dir,
            'icons_dest_dir': self.icons_dest_dir,
        }

def load_data_paths() -> DataPaths:
    """Load data path configuration from environment variables.
    
    Environment Variables:
        LOTRO_COMPANION_ROOT: Base path to lotro_companion repository
        LOTRO_FORGE_PROJECT_ROOT: Base path to this project (optional, auto-detected)
    
    Returns:
        DataPaths: Configured data paths
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Load environment variables
    load_dotenv()
    
    # Get project root (auto-detect if not set)
    project_root = Path(os.getenv('LOTRO_FORGE_PROJECT_ROOT', Path(__file__).parent.parent))
    
    # Get LOTRO Companion root (required)
    lotro_companion_root = os.getenv('LOTRO_COMPANION_ROOT')
    if not lotro_companion_root:
        raise ValueError(
            "LOTRO_COMPANION_ROOT environment variable not set. "
            "Please set it to the path of your lotro_companion repository."
        )
    
    lotro_companion_root = Path(lotro_companion_root)
    
    # Construct data paths
    paths = DataPaths(
        lotro_companion_root=lotro_companion_root,
        project_root=project_root,
        
        # Data files
        items_xml=lotro_companion_root / 'lotro-items-db' / 'items.xml',
        progressions_xml=lotro_companion_root / 'lotro-data' / 'lore' / 'progressions.xml',
        dps_tables_xml=lotro_companion_root / 'lotro-data' / 'lore' / 'dpsTables.xml',
        
        # Icon directories
        icons_source_dir=lotro_companion_root / 'lotro-icons' / 'items',
        icons_dest_dir=project_root / 'web' / 'static' / 'icons' / 'items',
    )
    
    # Validate paths
    if error := paths.validate():
        raise ValueError(f"Data path validation failed: {error}")
    
    return paths

def get_data_paths() -> DataPaths:
    """Get data paths singleton instance."""
    if not hasattr(get_data_paths, '_instance'):
        get_data_paths._instance = load_data_paths()
    return get_data_paths._instance

# Convenience functions for backward compatibility
def get_lotro_companion_root() -> Path:
    """Get the LOTRO Companion root directory."""
    return get_data_paths().lotro_companion_root

def get_items_xml_path() -> Path:
    """Get the path to items.xml."""
    return get_data_paths().items_xml

def get_progressions_xml_path() -> Path:
    """Get the path to progressions.xml."""
    return get_data_paths().progressions_xml

def get_dps_tables_xml_path() -> Path:
    """Get the path to dpsTables.xml."""
    return get_data_paths().dps_tables_xml

def get_icons_source_dir() -> Path:
    """Get the icons source directory."""
    return get_data_paths().icons_source_dir

def get_icons_dest_dir() -> Path:
    """Get the icons destination directory."""
    return get_data_paths().icons_dest_dir 