#!/bin/bash
clear
echo -e "\e[4;31m krishna !!! \e[0m"
echo -e "\e[1;34m Presents \e[0m"
echo -e "\e[1;32m Krishna_Bomb \e[0m"
echo "Press Enter To Continue"
read a1
if [[ -s update.krishna ]];then
echo "All Requirements Found...."
else
echo 'Installing Requirements....'
echo .
echo .
apt install figlet toilet python curl -y
apt install python3-pip
pip install -r requirements.txt
echo This script is written by krishna >update.krishna
echo Requirements Installed....
echo Press Enter To Continue...
read upd
fi
while :
do
rm *.xxx >/dev/null 2>&1
clear
echo -e "\e[1;31m"
figlet TBomb
echo -e "\e[1;34m Created By \e[1;32m"
toilet -f mono12 -F border krishna
echo -e "\e[4;34m This Bomber Was Created By krishna \e[0m"
echo -e "\e[1;34m For Any Queries Mail Me!!!\e[0m"
echo -e "\e[1;32m           Mail: krishnasingh62000@gmail.com \e[0m"
echo " "
echo -e "\e[4;31m Please Read Instuction given below !!! \e[0m"
echo " "
echo "Press 1 To  Gearup SMS Bomber "
echo "Press 2 To  Gearup Call Bomber "
echo "Press 3 To  Start Update (Works On Linux And Linux Emulators) "
echo "Press 4 To  View Features "
echo "Press 5 To  Exit "
read ch
if [ $ch -eq 1 ];then
clear
echo -e "\e[1;32m"
rm *.xxx >/dev/null 2>&1
python3 krishnabomb.py
rm *.xxx >/dev/null 2>&1
exit 0
elif [ $ch -eq 2 ];then
clear
echo -e "\e[1;32m"
echo 'Call Bomb By krishna'> call.xxx
python3 krishnabomb.py call
rm *.xxx >/dev/null 2>&1
exit 0
elif [ $ch -eq 3 ];then
clear
apt install git -y
echo -e "\e[1;34m Downloading Latest Files..."
git clone https://github.com/krishna-india/krishna.git
if [[ -s krishnabomb/krishnabomb.sh ]];then
cd krishnabomb
cp -r -f * .. > temp
cd ..
rm -rf  TBomb >> temp
rm update.krishna >> temp
rm temp
chmod +x krishnabomb.sh
fi
echo -e "\e[1;32m krishnabomb Will Restart Now..."
echo -e "\e[1;32m All The Required Packages Will Be Installed..."
echo -e "\e[1;34m Press Enter To Proceed To Restart..."
read a6
./krishnabomb.sh
exit
elif [ $ch -eq 4 ];then
clear
echo -e "\e[1;33m"
figlet krishnabomb
echo -e "\e[1;34mCreated By \e[1;34m"
toilet -f mono12 -F border krishna
echo  " "
echo -e "\e[1;32m                   Features\e[1;34m"
echo "  [+] Unlimited And Super-Fast Bombing"
echo "  [+] International Bombing"
echo "  [+] Call Bombing "
echo "  [+] Add Protection List"
echo "  [+] Automated Future Updates"
echo -e "\e[1;32m                   Contributors\e[1;33m"
echo -e "\e[1;33m      [*]  krishna   \e[1;31m"
echo "         [-] Mail At: krishnasingh62000@gmail.com"
echo ""
echo ""
echo -e "\e[1;31m This Script is Only For Educational Purposes or To Prank.\e[0m"
echo -e "\e[1;31m Do not Use This To Harm Others. \e[0m"
echo -e "\e[1;31m I Am Not Responsible For The Misuse Of The Script. \e[0m"
echo -e "\e[1;32m Make Sure To Update it If It Does not Work.\e[0m"
echo  " "
echo -e "\e[4;31m That's All About KRISHNA_B0MB ;-) !!!\e[0m"
echo -e "\e[1;34m For Any Queries Mail Me!!!\e[0m"
echo -e "\e[1;32m           Mail: krishnasingh62000@gmail.com \e[0m"
echo "Press Enter To Go Home"
read a3
clear
elif [ $ch -eq 5 ];then
clear
echo -e "\e[1;31m"
figlet TBomb
echo -e "\e[1;34m Created By \e[1;32m"
toilet -f mono12 -F border krishna
echo -e "\e[1;34m For Any Queries Mail Me!!!\e[0m"
echo -e "\e[1;32m           Mail: krishnasingh62000@gmail.com \e[0m"
echo " "
exit 0
else
echo -e "\e[4;32m Invalid Input !!! \e[0m"
echo "Press Enter To Go Home"
read a3
clear
fi
done
