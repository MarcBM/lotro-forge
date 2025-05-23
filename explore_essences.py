#!/usr/bin/env python3
"""
Script to explore essence data for EV calculation setup.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.config import get_database_url
from database.models.item import Essence

def main():
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        # Get all essences at ilvl 532 (Vivid)
        essences_532 = db.query(Essence).filter(Essence.base_ilvl == 532).all()
        print(f"Found {len(essences_532)} essences at ilvl 532:")
        
        # Group by stat name to see what stats are available
        stats_map = {}
        for essence in essences_532:
            for stat in essence.stats:
                stat_name = stat.stat_name
                stat_value = stat.get_value(532)
                if stat_name not in stats_map:
                    stats_map[stat_name] = []
                stats_map[stat_name].append({
                    'essence_name': essence.name,
                    'essence_type': essence.essence_type,
                    'value': stat_value
                })
        
        print(f"\nStats available at ilvl 532:")
        for stat_name, essences in stats_map.items():
            print(f"  {stat_name}:")
            for essence_info in essences:
                print(f"    {essence_info['essence_name']} (type {essence_info['essence_type']}): {essence_info['value']}")
        
        # Get essences at ilvl 508 for supplemental vitality/fate
        essences_508 = db.query(Essence).filter(Essence.base_ilvl == 508).all()
        print(f"\nFound {len(essences_508)} essences at ilvl 508:")
        
        vitality_508 = []
        fate_508 = []
        for essence in essences_508:
            for stat in essence.stats:
                if stat.stat_name == 'VITALITY':
                    vitality_508.append({
                        'essence_name': essence.name,
                        'value': stat.get_value(508)
                    })
                elif stat.stat_name == 'FATE':
                    fate_508.append({
                        'essence_name': essence.name,
                        'value': stat.get_value(508)
                    })
        
        if vitality_508:
            print(f"\nVitality essences at ilvl 508:")
            for essence_info in vitality_508:
                print(f"  {essence_info['essence_name']}: {essence_info['value']}")
                
        if fate_508:
            print(f"\nFate essences at ilvl 508:")
            for essence_info in fate_508:
                print(f"  {essence_info['essence_name']}: {essence_info['value']}")

if __name__ == "__main__":
    main() 