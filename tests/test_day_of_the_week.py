from assignment2 import get_day_of_week

def test_get_day_of_week():
    assert get_day_of_week('04/08/2024 3:00') == 2 #2 will be Monday, 1 is considered Sunday
