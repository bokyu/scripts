#!/bin/bash
export sample="Hello Yaml!"
export nats_machines="10.2.3.4"
export nats_username="nats"
export nats_password="password"

rm -f final.yml temp.yml  
( echo "cat << EOF > final.yml";
  cat template.yml;
  echo "EOF";
) >temp.yml
. temp.yml
cat final.yml
