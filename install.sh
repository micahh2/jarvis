#! /bin/bash

# Determine OS platform
UNAME=$(uname | tr "[:upper:]" "[:lower:]")
# If Linux, try to determine specific distribution
if [ "$UNAME" == "linux" ]; then
    # If available, use LSB to identify distribution
    if [ -f /etc/lsb-release -o -d /etc/lsb-release.d ]; then
        export DISTRO=$(lsb_release -i | cut -d: -f2 | sed s/'^\t'//)
        # Otherwise, use release info file
    else
        export DISTRO=$(ls -d /etc/[A-Za-z]*[_-][rv]e[lr]* | grep -v "lsb" | cut -d'/' -f3 | cut -d'-' -f1 | cut -d'_' -f1)
    fi
fi
# For everything else (or if above failed), just use generic identifier
[ "$DISTRO" == "" ] && export DISTRO=$UNAME
 
unset UNAME

DISTRO=$(echo $DISTRO | tr "[:upper:]" "[:lower:]")

if [[ $DISTRO != *ubuntu* ]] && [[ $DISTRO != *mint* ]] && [[ $DISTRO != *debian* ]]; then
    echo "Unable to detemine usable GNU/Linux version."
    echo "Going ahead with the install, but you will need"
    echo "to install dependencies manually (unless already installed):"
    echo -e "\t\t concalc \n\t\t gnuplot \n\t\t python3.2 \n\t\t python3-tk \n\t\t xsel"

else
    gksudo "apt-get install -y concalc gnuplot python3.2 python3-tk xsel"
fi

    sudo mkdir $HOME/.jarvis
    sudo cp * $HOME/.jarvis

    #Setup run thingy
        #Should probably change this so it can be used 
        #on multiperson/account systems
    echo -e -n "#!/bin/bash\ncd $HOME/.jarvis\npython3.2 $HOME/.jarvis/jarvis.py" > jarvis
    
    echo -e -n "[Desktop Entry]
Encoding=UTF-8 
Version=0.0.1 
Name=Jarvis
Type=Application 
Comment=A simple math engine 
Exec=jarvis 
Icon=$HOME/.jarvis/logo.png 
Categories=Application;Math;School;Education;Search; " > jarvis.desktop

    sudo chmod a+x jarvis
    
    sudo cp jarvis /usr/bin/
    sudo cp jarvis.desktop /usr/share/applications/

    sudo chown -c -R $USER:$USER $HOME/.jarvis
    chmod u+rw -R $HOME/.jarvis

    echo "Installed at $HOME/.jarvis"
