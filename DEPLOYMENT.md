# Deployment Process

## Building and Pushing the Image

1. **Built the Docker Image**:
   ```powershell
   docker build --platform linux/amd64 -t penguin-api .