#!/usr/bin/env python3
"""
Debug script to check EV values and color distribution.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker  
from database.config import get_database_url
from database.models.item import EquipmentItem
from web.api.services.ev_calculator import EVCalculator

def debug_ev_values():
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        calculator = EVCalculator(db)
        items = db.query(EquipmentItem).limit(20).all()
        
        print('EV values for first 20 items:')
        ev_values = []
        
        for item in items:
            stat_values = []
            for stat in item.stats:
                stat_values.append({
                    'stat_name': stat.stat_name, 
                    'value': stat.get_value(item.base_ilvl)
                })
            ev = calculator.calculate_equipment_ev(stat_values, item.socket_summary)
            ev_values.append(ev)
            print(f'{item.name[:30]:30} - EV: {ev:.2f}')
        
        # Analyze the distribution
        ev_values.sort()
        print(f'\nEV Distribution Analysis:')
        print(f'Min EV: {min(ev_values):.2f}')
        print(f'Max EV: {max(ev_values):.2f}')
        print(f'Range: {max(ev_values) - min(ev_values):.2f}')
        print(f'Average: {sum(ev_values)/len(ev_values):.2f}')
        
        # Test color classification
        print(f'\nColor Classification Test:')
        for i, ev in enumerate(ev_values):
            rank = sum(1 for value in ev_values if value <= ev)
            percentile = rank / len(ev_values)
            
            if percentile <= 0.25:
                color = 'RED'
            elif percentile <= 0.50:
                color = 'YELLOW'
            elif percentile <= 0.75:
                color = 'GREEN'
            else:
                color = 'TEAL'
            
            print(f'EV {ev:.2f} - Percentile: {percentile:.1%} - Color: {color}')

if __name__ == "__main__":
    debug_ev_values() 