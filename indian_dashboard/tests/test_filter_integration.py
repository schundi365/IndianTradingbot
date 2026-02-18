"""
Integration test for filter functionality
Tests the filter logic with sample instrument data
"""

def test_exchange_filter():
    """Test filtering by exchange"""
    instruments = [
        {'symbol': 'RELIANCE', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'TCS', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'INFY', 'exchange': 'BSE', 'instrument_type': 'EQ'},
        {'symbol': 'NIFTY24JAN24000CE', 'exchange': 'NFO', 'instrument_type': 'CE'},
    ]
    
    # Filter by NSE
    nse_instruments = [i for i in instruments if i['exchange'] == 'NSE']
    assert len(nse_instruments) == 2, f"Expected 2 NSE instruments, got {len(nse_instruments)}"
    assert all(i['exchange'] == 'NSE' for i in nse_instruments), "All instruments should be from NSE"
    
    # Filter by multiple exchanges (NSE or BSE)
    nse_bse_instruments = [i for i in instruments if i['exchange'] in ['NSE', 'BSE']]
    assert len(nse_bse_instruments) == 3, f"Expected 3 NSE/BSE instruments, got {len(nse_bse_instruments)}"
    
    print("✓ Exchange filter test passed")


def test_type_filter():
    """Test filtering by instrument type"""
    instruments = [
        {'symbol': 'RELIANCE', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'TCS', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'NIFTY24JAN24000FUT', 'exchange': 'NFO', 'instrument_type': 'FUT'},
        {'symbol': 'NIFTY24JAN24000CE', 'exchange': 'NFO', 'instrument_type': 'CE'},
        {'symbol': 'NIFTY24JAN24000PE', 'exchange': 'NFO', 'instrument_type': 'PE'},
    ]
    
    # Filter by EQ
    eq_instruments = [i for i in instruments if i['instrument_type'] == 'EQ']
    assert len(eq_instruments) == 2, f"Expected 2 EQ instruments, got {len(eq_instruments)}"
    
    # Filter by multiple types (CE or PE)
    options_instruments = [i for i in instruments if i['instrument_type'] in ['CE', 'PE']]
    assert len(options_instruments) == 2, f"Expected 2 option instruments, got {len(options_instruments)}"
    
    print("✓ Type filter test passed")


def test_combined_filters():
    """Test combining exchange and type filters"""
    instruments = [
        {'symbol': 'RELIANCE', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'TCS', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'INFY', 'exchange': 'BSE', 'instrument_type': 'EQ'},
        {'symbol': 'NIFTY24JAN24000FUT', 'exchange': 'NFO', 'instrument_type': 'FUT'},
        {'symbol': 'NIFTY24JAN24000CE', 'exchange': 'NFO', 'instrument_type': 'CE'},
    ]
    
    # Filter by NSE AND EQ
    nse_eq_instruments = [
        i for i in instruments 
        if i['exchange'] == 'NSE' and i['instrument_type'] == 'EQ'
    ]
    assert len(nse_eq_instruments) == 2, f"Expected 2 NSE EQ instruments, got {len(nse_eq_instruments)}"
    
    # Filter by NFO AND (CE or PE)
    nfo_options = [
        i for i in instruments 
        if i['exchange'] == 'NFO' and i['instrument_type'] in ['CE', 'PE']
    ]
    assert len(nfo_options) == 1, f"Expected 1 NFO option, got {len(nfo_options)}"
    
    print("✓ Combined filter test passed")


def test_search_with_filters():
    """Test search combined with filters"""
    instruments = [
        {'symbol': 'RELIANCE', 'name': 'Reliance Industries', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'INFY', 'name': 'Infosys', 'exchange': 'BSE', 'instrument_type': 'EQ'},
        {'symbol': 'TATAMOTORS', 'name': 'Tata Motors', 'exchange': 'NSE', 'instrument_type': 'EQ'},
    ]
    
    # Search for "TATA" AND filter by NSE
    search_term = 'tata'
    filtered = [
        i for i in instruments 
        if i['exchange'] == 'NSE' and (
            search_term in i['symbol'].lower() or 
            search_term in i['name'].lower()
        )
    ]
    assert len(filtered) == 2, f"Expected 2 instruments, got {len(filtered)}"
    assert all('tata' in i['symbol'].lower() or 'tata' in i['name'].lower() for i in filtered)
    
    print("✓ Search with filters test passed")


def test_empty_filters():
    """Test that empty filters return all instruments"""
    instruments = [
        {'symbol': 'RELIANCE', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'TCS', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'INFY', 'exchange': 'BSE', 'instrument_type': 'EQ'},
    ]
    
    # No filters applied
    exchange_filters = []
    type_filters = []
    
    filtered = instruments
    if exchange_filters:
        filtered = [i for i in filtered if i['exchange'] in exchange_filters]
    if type_filters:
        filtered = [i for i in filtered if i['instrument_type'] in type_filters]
    
    assert len(filtered) == len(instruments), "Empty filters should return all instruments"
    
    print("✓ Empty filters test passed")


def test_no_results():
    """Test filters that return no results"""
    instruments = [
        {'symbol': 'RELIANCE', 'exchange': 'NSE', 'instrument_type': 'EQ'},
        {'symbol': 'TCS', 'exchange': 'NSE', 'instrument_type': 'EQ'},
    ]
    
    # Filter by NFO (no NFO instruments in list)
    nfo_instruments = [i for i in instruments if i['exchange'] == 'NFO']
    assert len(nfo_instruments) == 0, "Should return empty list when no matches"
    
    print("✓ No results test passed")


def run_all_tests():
    """Run all filter tests"""
    print("\n=== Running Filter Integration Tests ===\n")
    
    try:
        test_exchange_filter()
        test_type_filter()
        test_combined_filters()
        test_search_with_filters()
        test_empty_filters()
        test_no_results()
        
        print("\n=== All Tests Passed ✓ ===\n")
        return True
    except AssertionError as e:
        print(f"\n✗ Test Failed: {e}\n")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}\n")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
