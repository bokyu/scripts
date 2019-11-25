#!/bin/bash
parent_id=$1
for i in $(docker images -q); do
    docker history $i | grep -q  $parent_id && { echo $i; echo $(docker images | grep $i); }
done | sort -u
