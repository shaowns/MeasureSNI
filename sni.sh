#!/bin/bash
url=$1
echo | openssl s_client -connect www.$url:443 -servername www.$url 2>&1 | sed -n '/BEGIN CERTIFICATE/,/END CERTIFICATE/p'
