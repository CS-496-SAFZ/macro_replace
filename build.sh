#!/bin/sh
# same as the one in the tractor repo, and is meant to run in the container specified by the image there

# download Boost
BOOST_VER="1_82_0"
BOOST_INSTALL_URL="https://archives.boost.io/release/1.82.0/source/boost_${BOOST_VER}.tar.bz2"
BOOST_DIR="/usr/local/boost_${BOOST_VER}"

echo "downloading Boost"
curl -L "$BOOST_INSTALL_URL" -o /tmp/boost_${BOOST_VER}.tar.bz2
mkdir -p "$BOOST_DIR" && tar --bzip2 -xf /tmp/boost_${BOOST_VER}.tar.bz2 -C "$BOOST_DIR" --strip-components=1

# build Boost and install wave
echo "building Boost"
cd "$BOOST_DIR"

ARCH=`uname -m` 
if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    ARCHITECTURE="arm"
else
    ARCHITECTURE="x86"
fi

./bootstrap.sh
# on arm chips architecture needs to specify it's arm for b2 to work
./b2 toolset=clang architecture="$ARCHITECTURE" address-model=64 cxxflags="-std=c++11" libs/wave/tool/build/

echo "finished building wave"

# should always build to this path, can use find later if this isn't the case
WAVE_EXEC_PATH="/usr/local/boost_1_82_0/bin.v2/libs/wave/tool/build/clang-linux-18/release/threadapi-pthread/threading-multi/wavetool-on"
echo "WAVE_EXEC_PATH = $WAVE_EXEC_PATH"