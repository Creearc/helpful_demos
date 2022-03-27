## Instalation

```
sudo apt update && sudo apt upgrade -y
sudo apt upgrade cmake

sudo apt-get install git libssl-dev libusb-1.0-0-dev pkg-config libgtk-3-dev
sudo apt-get install libcurl4-openssl-dev

sudo apt-get install gcc-5 g++-5

sudo apt-get install python-opengl
sudo python3 -m pip install pyopengl
sudo python3 -m pip install pyopengl_accelerate

git clone https://github.com/IntelRealSense/librealsense
cd ~/librealsense
mkdir  build  && cd build
cmake ../ -DBUILD_EXAMPLES=true -DBUILD_GRAPHICAL_EXAMPLES=false -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3)
sudo make uninstall && make clean && make && sudo make install
```

```
sudo nano ~/.zshrc
```

```
export PYTHONPATH=$PYTHONPATH:/usr/local/lib
```

```
source ~/.zshrc
```
