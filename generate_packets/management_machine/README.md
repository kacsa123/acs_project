Replace line 122 in `SUMMER2017/apps/benchmark/run.sh` with

```bash
if [[ ! "$role" == "moongen/client" ]]; then
    run "ssh $USERNAME@$management_ip '$dname/setup_ip.sh $interface_ip'"
fi
```

and line 143 with
```bash
if [[ ! "$role" == "moongen/client" ]]; then
    run "ssh $USERNAME@$management_ip '$dname/setup_ip.sh $interface_ip'"
fi
```
