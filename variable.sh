#!/bin/bash

aa_echo="aaaaa"
bb_echo="bbbbb"
cc_echo="ccccc"
dd_echo="ddddd"
var_list="aa bb cc dd"

for var in ${var_list[@]}; do
  var_name="${var}_echo"
  echo "name of var_name: $var_name"
  echo "value of var_name: ${!var_name}"
  echo "=================================="
done
