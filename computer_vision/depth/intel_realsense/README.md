## Instalation

```
sudo apt update && sudo apt upgrade -y
sudo apt upgrade cmake

sudo apt-get install libcurl4-openssl-dev

sudo apt-get install python-opengl
sudo python3 -m pip install pyopengl
sudo python3 -m pip install pyopengl_accelerate

git clone https://github.com/IntelRealSense/librealsense
cd ~/librealsense
mkdir  build  && cd build
cmake .. -DBUILD_PYTHON_BINDINGS=bool:true -DPYTHON_EXECUTABLE=$(which python3) -DBUILD_EXAMPLES=true -DCMAKE_BUILD_TYPE=Release -DFORCE_LIBUVC=true
make -j4
sudo make install
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
