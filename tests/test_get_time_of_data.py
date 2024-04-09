from assignment2 import get_time_of_data

def test_get_time_of_data():
    # Assuming the hour for '04/08/2024 15:30' is 15
    assert get_time_of_data('04/08/2024 15:30') == 15
