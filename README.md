# drone-camera-forproject

# python3.9.12 installation


sudo apt update
sudo apt upgrade
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev
wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tgz

# python3.9.12 installation 
tar -xf Python-3.9.12.tgz
cd Python-3.9.12
./configure --enable-optimizations
make -j4  # You can change the number after -j to match the number of CPU cores for faster compilation.
sudo make altinstall

# after the installation finish - make the python as defount (python and python3)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.9 1
sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.9 1

alternativ - check if the instalation finish - python --version /python3 --version.

#pip problem 
sudo apt update
sudo apt install python3.9-distutils
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.9 get-pip.py
sudo python3.9 -m pip install --upgrade pip


# let install cmake 

cmake --version  #check you defoult camke version

sudo apt-get install libcurl4-openssl-dev
sudo apt install wget
mkdir ~/cmake-source
cd ~/cmake-source
curl -LO https://cmake.org/files/v3.27/cmake-3.27.4.tar.gz
tar -xzvf cmake-3.27.4.tar.gz

# build and inastall cmake 

cd cmake-3.27.4
./bootstrap
make -j2  # You can change the number after -j to match the number of CPU cores for faster compilation.
sudo make install


#check the version again 
cmake --version


# intelrealsense
#now go to intelreal sense git downlad and take some source file to install the sdk
#from here:  https://github.com/IntelRealSense/librealsense/releases/

unzip librealsense-2.48.0.zip -d /home/drone/naorp/cam

#got to this cd
mkdir build 
cd build 
sudo apt-get install libxinerama-dev
sudo apt-get install libxcursor-dev
#run this line to use the cmake
cmake ../ -DFORCE_RSUSB_BACKEND=ON -DBUILD_PYTHON_BINDINGS:bool=true -DPYTHON_EXECUTABLE=/usr/local/bin/python3.9 -DCMAKE_BUILD_TYPE=release -DBUILD_EXAMPLES=true -DBUILD_GRAPHICAL_EXAMPLES=true -DBUILD_WITH_CUDA:bool=false

# installation
make -j2
sudo make install

# bashrc
vim ~/.bashrc
#use i to insert data
#to exit use esc and then :wq

#put this at bashrc - mabey need to fix it - lets see what at my jetson but 

export PATH=$PATH:/usr/local/bin
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.9/site-packages
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.9
export PYTHONPATH=$PYTHONPATH:/home/drone/naorp/cam/librealsense-2.48.0/build/wrappers/python

#after exit 
source ~/.bashrc

#import problem- at the script need to import pymavlink as:import pyrealsense2.pyrealsense2 as rs

#helps: 
1)https://github.com/IntelRealSense/librealsense/issues/12137 #me ask for help 
2)https://github.com/IntelRealSense/librealsense/issues/6964#issuecomment-707501049 #install intelrealsense
3) https://github.com/IntelRealSense/librealsense/issues/6980#issuecomment-666858977 #update the cmake 


# mavlink instalation 
#at this point we can install the mavproxy 
#can see this here also https://www.youtube.com/watch?v=nIuoCYauW3s

sudo apt-get update
sudo apt-get install python-pip python3-pip
sudo apt-get install python3-dev python3-opencv python3-wxgtk4.0  python3-matplotlib python3-lxml libxml2-dev libxslt-dev
sudo pip install PyYAML mavproxy
sudo mavproxy.py --master=/dev/ttyTHS1
#at this point the mavproxy activate 


#to get premition - need to fix it ask tal
sudo chmod a+rw /dev/ttyTHS1
Sudo mavproxy.py –master=/dev/ttyTHS1


#install package the asential to read qr code 
pip install pyzbar
pip install opencv-python-headless

-----------------------------------------------------

# run simulation 
run drone simulation with gazibo
cd PX4-Autopilot/Tools/setup
./ubuntu.sh


cd ~/PX4-Autopilot
make px4_sitl gazebo #this make regular dji drone 
-------------------------------------------------------
sudo apt-get install gz-garden 
s

------------------------------------------------------
#make jsim simulator 
make px4_sitl_default jmavsim



