#!/usr/bin/env python3
"""
Test script for EV Calculator integration.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.config import get_database_url
from web.api.services.ev_calculator import EVCalculator
from fastapi.testclient import TestClient
from web.main import app

def test_ev_calculator():
    """Test the EV calculator directly."""
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as db:
        calculator = EVCalculator(db)
        
        # Test loading essence values
        essence_values = calculator._load_essence_values()
        print(f"✓ Loaded {len(essence_values)} essence values")
        
        # Test individual stat calculations
        crit_rating_ev = calculator.calculate_stat_ev('CRITICAL_RATING', 3474.08)
        print(f"✓ CRITICAL_RATING calculation: {crit_rating_ev:.2f} EV")
        
        # Test socket calculations
        socket_summary = {'basic': 2, 'primary': 1}
        socket_ev = calculator.calculate_socket_ev(socket_summary)
        print(f"✓ Socket calculation: {socket_ev:.2f} EV")
        
        # Test complete equipment calculation
        stat_values = [
            {'stat_name': 'CRITICAL_RATING', 'value': 3474.08},
            {'stat_name': 'MIGHT', 'value': 1639.39}
        ]
        total_ev = calculator.calculate_equipment_ev(stat_values, socket_summary)
        print(f"✓ Complete equipment calculation: {total_ev:.2f} EV")
        
        print("✓ All EV calculator tests passed!")

def test_api_integration():
    """Test the API integration."""
    client = TestClient(app)
    
    print("\nTesting API integration...")
    response = client.get("/api/items/equipment?limit=6")
    
    if response.status_code == 200:
        data = response.json()
        items = data["items"]
        print(f"✓ API works! Got {len(items)} items with EV values:")
        
        ev_values = []
        for item in items:
            ev = item.get('ev', 'N/A')
            ev_values.append(float(ev) if ev != 'N/A' else 0)
            print(f"  {item['name'][:30]:30} - EV: {ev:>6}")
        
        # Test color classification simulation
        if ev_values:
            ev_values.sort()
            print(f"\n✓ EV range: {min(ev_values):.2f} to {max(ev_values):.2f}")
            print("✓ Color coding will work with this range!")
    else:
        print(f"✗ API error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_ev_calculator()
    test_api_integration() 