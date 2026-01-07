from cleanse_library_data import calculate_date_difference

def test_date_difference():
    assert calculate_date_difference("01/01/2024", "05/01/2024") == 4