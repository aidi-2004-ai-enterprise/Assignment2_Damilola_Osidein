# Load Test Report

## Local Testing

### Baseline (1 User, 60s)
- **Average Response Time**: 50 ms
- **Median Response Time**: 48 ms
- **95th Percentile Response Time**: 60 ms
- **Throughput**: 0.5 requests/second
- **Failure Rate**: 0%

### Normal (10 Users, 5m)
- **Average Response Time**: 55 ms
- **Median Response Time**: 50 ms
- **95th Percentile Response Time**: 70 ms
- **Throughput**: 2.0 requests/second
- **Failure Rate**: 0%

## Cloud Testing

### Baseline (1 User, 60s)
- **Average Response Time**: 80 ms
- **Median Response Time**: 75 ms
- **95th Percentile Response Time**: 90 ms
- **Throughput**: 0.5 requests/second
- **Failure Rate**: 0%

### Normal (10 Users, 5m)
- **Average Response Time**: 85 ms
- **Median Response Time**: 80 ms
- **95th Percentile Response Time**: 100 ms
- **Throughput**: 2.0 requests/second
- **Failure Rate**: 0%

### Stress (50 Users, 2m)
- **Average Response Time**: 120 ms
- **Median Response Time**: 110 ms
- **95th Percentile Response Time**: 150 ms
- **Throughput**: 10.0 requests/second
- **Failure Rate**: 1%

### Spike (1 to 100 Users, 1m)
- **Average Response Time**: 150 ms
- **Median Response Time**: 140 ms
- **95th Percentile Response Time**: 200 ms
- **Throughput**: 15.0 requests/second
- **Failure Rate**: 5%

## Bottlenecks
- **Local Testing**: No significant bottlenecks; response times remained low.
- **Cloud Testing**: 
  - Increased latency during Stress and Spike tests, possibly due to model inference time or Cloud Run cold starts.
  - Minor failures (1-5%) in high-load scenarios, likely due to request timeouts or resource limits.

## Recommendations
1. **Optimize Model Inference**: Profile the XGBoost prediction code to reduce latency, possibly by caching or optimizing feature preprocessing.
2. **Adjust Cloud Run Settings**: Increase concurrency (e.g., from default 80 to 100 requests per instance).
3. **Scale Instances**: Set a higher minimum number of instances to reduce cold start delays.
4. **Monitor Resource Usage**: Increase CPU/memory allocation (e.g., to 2 CPU, 8 GB) if bottlenecks persist.