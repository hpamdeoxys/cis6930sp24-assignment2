from assignment2 import rank_nature
import pandas as pd

def test_rank_nature():
    df = pd.DataFrame({'nature': ['Nature1', 'Nature1', 'Nature2']})
    ranked_df = rank_nature(df)
    assert ranked_df['incident_rank'].iloc[0] == 1
    assert ranked_df['incident_rank'].iloc[2] == 2
