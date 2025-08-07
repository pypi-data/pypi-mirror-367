# Kubernetes-Restarter

Kubernetes-Restarter (`kres`) is a CLI tool for safely restarting Kubernetes resources (pods, deployments, statefulsets) based on secret or configmap changes.

## Features

- Restart pods, deployments, or statefulsets referencing specific secrets/configmaps
- Check access permissions for Kubernetes resources
- Modular, extensible CLI structure
- Colorful logging with multiple log levels

## Installation

1. **Clone the repository:**
   ```
   git clone https://github.com/ShashankPalla2002/Kubernetes-Restarter.git
   cd Kubernetes-Restarter
   ```

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the CLI tool:
```
python -m kres.main <command> [options]
```

### Commands

- **init**  
  Initialize with a kubeconfig and start the Kres API.
  ```
  python -m kres.main init --kubeconfig ~/.kube/config --port 5454 --log INFO
  ```

- **logout**  
  Logout and clear session data.
  ```
  python -m kres.main logout --log INFO
  ```

- **api**  
  Check status of Kres API or Kubernetes API.
  ```
  python -m kres.main api --type kres --log INFO
  python -m kres.main api --type kubernetes --log INFO
  ```

- **access**  
  Check if kres can access a resource in a namespace.
  ```
  python -m kres.main access --namespace default --resource pods --verb get --log INFO
  ```

- **restart**  
  Restart resources referencing a secret/configmap.
  ```
  python -m kres.main restart --namespace default --resource deployments --all --secret mysecret --reason "Secret updated" --log INFO
  python -m kres.main restart --namespace default --resource pods --name mypod --log INFO
  ```

## Configuration

- **Kubeconfig:**  
  By default, kres uses `~/.kube/config`. You can specify a different path with `--kubeconfig`.
- **Port:**  
  Kres API runs on port `5454` by default. Use `--port` to change.

## Logging

- Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- Color-coded output for better readability

## Project Structure

```
kres/
  api/
    apiHandler.py
    kresApi.py
    kresApiLauncher.py
  config/
    extractConfig.py
    loadConfig.py
  encryption/
    tokenEncryption.py
  subparsers/
    accessParser.py
    apiParser.py
    logoutParser.py
    restartParser.py
  utils/
    extractResourceNames.py
    logger.py
    parser.py
  main.py
README.md
requirements.txt
```

## Contributing

Pull requests and issues are welcome! Please open an issue to discuss major changes.