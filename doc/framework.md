# ECG Delineation Framework
>> Date: 2016-8-27
## Levels
1. Random Rounds: randomly select records from QTdb to test & save result.
2. Warpper: given test & training records, output the trained model & test result.
3. ECG Random forest delineator: 
    * Training: given ECG waveform& labels
    * Testing: given ECG waveform
4. Evaluation: evaluation for paper: std, mean error, P+, Se
