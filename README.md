# Sonic-Cipher: Spoof-Aware Speaker Verification System

**Sonic-Cipher** is a Python package for robust speaker verification with integrated spoof detection. It combines automatic speaker verification (ASV) with countermeasure (CM) models to identify and reject spoofed audio inputs. Perfect for secure authentication systems using voice biometrics.

# Installation and Configuration

1. Install the package

- From Pypi

``` bash
pip install sonic-cipher
```

- Build from Scratch
  
``` bash
git clone https://github.com/SonicCypher/Speaker-Verification-Application.git
cd Speaker-Verification-Application
pip install build
python -m build
pip install -e .
```

2. Create a virtual environment and install the dependencies

``` bash
pip install -r requirements.txt
```

4. Export the below envrionment variables

``` bash
DB_NAME=<your_database>
DB_USER=<your_username>
DB_PASSWORD=<your_password>
DB_HOST=<your_database_host>
DB_PORT=<your_database_port>
```

> Note: Currently `sonic-cipher` supports only Postgres databases

# Usage Example

## 📝 Register a Speaker

``` python
from sonic_cipher import register_user

register_user(username, path1, path2, path3)
```

- In the registration process, `register_user` accepts paths of 3 audio clips of the user

## 🔍 Verify a Speaker

``` python
from sonic_cipher import predict_verification

is_verified, confidence_score = register_user(username, path_of_test_audio, device="cpu", threshold=0.1994701042959457)
```
- Required parameters: username, path of the test audio

