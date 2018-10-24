echo ---------------------
echo "  LiquiTrader Setup"
echo ---------------------

if [[ ! -d "/usr/local/include/ta-lib" ]]
then
    echo
    echo Downloading and installing TA-Lib...
    
    timeout 2
    sudo apt-get update
    sudo apt-get install gcc, make
    
    mkdir talib-pkg
    cd talib-pkg
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib
    ./configure
    make
    sudo make install
    
    cd ../..
    rm -r talib-pkg
fi


# If user is on Ubuntu 14, make sure they have a compatible version of OpenSSH installed
linux_version="$(lsb_release -rs)"
openssl_version="$(openssl version)"
if [[ $linux_version = 14* && $openssl_version != OpenSSL\ 1.0.2* ]]
then
    echo
	echo "Ubuntu 14 ships with OpenSSL v1.01, but LiquiTrader requires OpenSSL v1.02"
	echo "In order to install OpenSSL v1.02, we need to add the Debian Jessie backport source to your sources.list"
	echo "Is this okay? If not, LiquiTrader will not be able to run."
	
	select yn in "Yes" "No"; do
		case $yn in
            Yes ) break;;
			No ) exit;;
		esac
	done

	echo "deb http://ftp.debian.org/debian jessie-backports main" >> sudo tee -a /etc/apt/sources.list
        sudo apt-get update
	sudo apt-get install openssl
fi


echo
echo Setup complete!
echo 
