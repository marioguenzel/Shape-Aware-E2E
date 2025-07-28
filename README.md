# Shape-Aware-E2E
Shape-Aware Analysis of End-to-End Latency


## Note for development

There is a working pipeline for debugging. 
Just run 
```
python generate.py chains/tests.jsonl
python analysis.py ???
```

To generate some cause-effect chains using WATERS, store them in ```test/test.jsonl``` and print analysis results


## What I observed so far:
- no difference between minimum and average values for RT and DA


## To test
- hopefully there is a difference in (m,k) and longest exceedance for chains/example.jsonl ID 992