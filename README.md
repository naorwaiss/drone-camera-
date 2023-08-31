# drone-camera-

# python3.9.12 instalation


sudo apt update
sudo apt upgrade
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev
wget https://www.python.org/ftp/python/3.9.12/Python-3.9.12.tgz

# take all this line together 
tar -xf Python-3.9.12.tgz
cd Python-3.9.12
./configure --enable-optimizations
make -j4  # You can change the number after -j to match the number of CPU cores for faster compilation.
sudo make altinstall

# after the instalation finish - make the python as defount (python and python3)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.9 1
sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.9 1

alternativ - check if the instalation finish - python --version /python3 --version.


# let install cmake 

cmake --version  #check you defoult camke version


sudo apt-get install libcurl4-openssl-dev
sudo apt install wget
mkdir ~/cmake-source
cd ~/cmake-source
curl -LO https://cmake.org/files/v3.27/cmake-3.27.4.tar.gz
tar -xzvf cmake-3.27.4.tar.gz

#build and inastall cmake 

cd cmake-3.27.4
./bootstrap
make -j2  # You can change the number after -j to match the number of CPU cores for faster compilation.
sudo make install


#check the version again 
cmake --version



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

#installation
make -j2
sudo make install

vim ~/.bashrc
# use i to insert data
#to exit use esc and then :wq

# put this - mabey need to fix it - lets see what at my jetson but 

export PATH=$PATH:/usr/local/bin
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.9/site-packages
export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.9
export PYTHONPATH=$PYTHONPATH:/home/drone/naorp/cam/librealsense-2.48.0/build/wrappers/python

#after exit 
source ~/.bashrc





#at this point we can install 





