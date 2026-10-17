# 🦅 Golden Eagle: Development & Testing Workflow

## 1. Write & Update Code
Edit the Python files locally (`golden_eagle.py`, `core`, `lang`).

## 2. Push to GitHub
```bash
git add .
git commit -m "Update description"
git push
```
*(Wait ~2 minutes for GitHub Actions to build the `.exe`)*

## 3. Download the `.exe`
Use GitHub CLI to download the latest build:
```bash
gh run download --name GoldenEagle-Executable
mv GoldenEagle-Executable/GoldenEagle.exe ./win_test/
```

## 4. Run & Test in Docker (Windows Simulator)
Navigate to the `win_test` folder containing the `.exe`, then run:
```bash
xhost +local:docker
sudo docker run -it --rm \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -e DISPLAY=$DISPLAY \
  -v $(pwd):/app \
  wine-test wine /app/GoldenEagle.exe
```
