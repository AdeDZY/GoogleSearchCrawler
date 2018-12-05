#!/bin/bash
MYIP=$(dig +short +time=1 myip.opendns.com @resolver1.opendns.com)

source activate mlnd-dl
git clone https://github.com/AdeDZY/GoogleSearchCrawler.git
cd GoogleSearchCrawler/data
mkdir "$MYIP"
cd ../
pwd

python ./gsearch.py data/aol-100K.txt data/$MYIP/crawled -r -m 5 > data/$MYIP/log 
python ./gather_url.py data/$MYIP/crawled data/$MYIP/id2url -s 0 -p google-2017-$MYIP 
python ./download_webpage.py data/$MYIP/id2url data/user_agents data/$MYIP/crawled
python ./parse_html.py data/$MYIP/crawled data/$MYIP/parsed 

HOST_IP=$(dig +short +time=1 myip.opendns.com @resolver1.opendns.com)
REMOTE_IP="128.2.204.55"  
#SCP\_PASSWORD\_E="Ade_10232"  
#SCP_PASSWORD=`echo "$SCP_PASSWORD_E" `
SCP_PASSWORD="PASSWORD"
echo $SCP_PASSWORD


#And now transfer the file over
expect -c "  
   set timeout 1
   spawn scp -r ./GoogleSearchCrawler/data/$HOST_IP/ zhuyund@$REMOTE_IP:/bos/tmp11/zhuyund/Google-Crawled/
   expect yes/no { send yes\r ; exp_continue }
   expect Password: { send $SCP_PASSWORD\r }
   expect 100%
   sleep 1
   exit
"  

