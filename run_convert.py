import pytest
import os
if __name__=="__main__":

    os.system(r"hrp convert --from-har .\har\debug_data_20240311.har  --to-pytest --output-dir .\testcases\debug")