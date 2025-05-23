"""
Essence Value (EV) Calculator Service

Calculates essence value scores for equipment items based on their concrete stats.
The EV represents how many essences it would take to replicate the stats on an item.
"""
from typing import Dict, Optional
from sqlalchemy.orm import Session
from database.models.item import Essence

class EVCalculator:
    """Service for calculating Essence Value scores."""
    
    def __init__(self, db: Session):
        self.db = db
        self._essence_values: Optional[Dict[str, float]] = None
    
    def _load_essence_values(self) -> Dict[str, float]:
        """Load reference essence values for EV calculation."""
        if self._essence_values is not None:
            return self._essence_values
        
        essence_values = {}
        
        # Get Vivid essences at ilvl 532 (baseline for most stats)
        vivid_essences = self.db.query(Essence).filter(Essence.base_ilvl == 532).all()
        
        for essence in vivid_essences:
            for stat in essence.stats:
                stat_name = stat.stat_name
                stat_value = stat.get_value(532)
                
                # Skip VITALITY and FATE here - handled separately
                if stat_name not in ['VITALITY', 'FATE']:
                    essence_values[stat_name] = stat_value
        
        # Special handling for VITALITY and FATE - use supplemental essences at ilvl 508
        supplemental_essences = self.db.query(Essence).filter(
            Essence.base_ilvl == 508,
            Essence.name.contains('Supplemental')
        ).all()
        
        for essence in supplemental_essences:
            for stat in essence.stats:
                stat_name = stat.stat_name
                if stat_name in ['VITALITY', 'FATE']:
                    stat_value = stat.get_value(508)
                    essence_values[stat_name] = stat_value
        
        self._essence_values = essence_values
        return essence_values
    
    def calculate_stat_ev(self, stat_name: str, stat_value: float) -> float:
        """Calculate EV contribution for a single stat."""
        essence_values = self._load_essence_values()
        
        # Handle ARMOUR special case - convert to mitigations
        if stat_name == 'ARMOUR':
            # Physical mitigation = armour value * 1.0
            phys_mit_ev = 0.0
            if 'PHYSICAL_MITIGATION' in essence_values:
                phys_mit_ev = stat_value / essence_values['PHYSICAL_MITIGATION']
            
            # Tactical mitigation = armour value * 0.2
            tact_mit_ev = 0.0
            if 'TACTICAL_MITIGATION' in essence_values:
                tact_mit_ev = (stat_value * 0.2) / essence_values['TACTICAL_MITIGATION']
            
            return phys_mit_ev + tact_mit_ev
        
        # Standard stat calculation
        if stat_name not in essence_values:
            return 0.0
        
        return stat_value / essence_values[stat_name]
    
    def calculate_socket_ev(self, socket_summary: Dict[str, int]) -> float:
        """Calculate EV contribution for sockets."""
        essence_values = self._load_essence_values()
        
        total_socket_ev = 0.0
        
        # Most sockets are worth 1 EV each
        basic_sockets = socket_summary.get('basic', 0)
        primary_sockets = socket_summary.get('primary', 0)
        cloak_sockets = socket_summary.get('cloak', 0)
        necklace_sockets = socket_summary.get('necklace', 0)
        pvp_sockets = socket_summary.get('pvp', 0)
        
        total_socket_ev += basic_sockets + primary_sockets + cloak_sockets + necklace_sockets + pvp_sockets
        
        # Vital sockets are special - they're worth the ratio of supplemental to vivid vitality
        vital_sockets = socket_summary.get('vital', 0)
        if vital_sockets > 0:
            # Get vivid vitality value (ilvl 532)
            vivid_vitality = 0.0
            vivid_essences = self.db.query(Essence).filter(
                Essence.base_ilvl == 532,
                Essence.name.contains('Vitality')
            ).first()
            if vivid_essences:
                for stat in vivid_essences.stats:
                    if stat.stat_name == 'VITALITY':
                        vivid_vitality = stat.get_value(532)
                        break
            
            # Get supplemental vitality value (ilvl 508)
            supplemental_vitality = essence_values.get('VITALITY', 0)
            
            if vivid_vitality > 0 and supplemental_vitality > 0:
                vital_socket_value = vivid_vitality / supplemental_vitality
                total_socket_ev += vital_sockets * vital_socket_value
            else:
                # Fallback to 1 EV per socket if we can't calculate the ratio
                total_socket_ev += vital_sockets
        
        return total_socket_ev
    
    def calculate_equipment_ev(self, stat_values: list, socket_summary: Optional[Dict[str, int]] = None) -> float:
        """
        Calculate total EV for an equipment item.
        
        Args:
            stat_values: List of stat dictionaries with 'stat_name' and 'value' keys
            socket_summary: Dictionary with socket counts by type
            
        Returns:
            Total essence value score
        """
        total_ev = 0.0
        
        # Calculate EV from stats
        for stat in stat_values:
            stat_name = stat['stat_name']
            stat_value = stat['value']
            stat_ev = self.calculate_stat_ev(stat_name, stat_value)
            total_ev += stat_ev
        
        # Calculate EV from sockets
        if socket_summary:
            socket_ev = self.calculate_socket_ev(socket_summary)
            total_ev += socket_ev
        
        return total_ev 