from assignment2 import rank_locations
import pandas as pd

def test_rank_locations():
    df = pd.DataFrame({'incident_location': ['Location1', 'Location1', 'Location2']})
    ranked_df = rank_locations(df)
    assert ranked_df['location_rank'].iloc[0] == 1
    assert ranked_df['location_rank'].iloc[2] == 2
