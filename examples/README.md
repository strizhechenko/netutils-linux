# How to add your success story/example?

## You are programmer similar with git(hub).

Fork this repo and clone it to your host. 

Next you should create directory describing your system.

You need to look at `lscpu` output of tuned system to see socket count and cpu per socket values (you're probably already know it).

mkdir netutils-linux/examples/sockets_${socket_count}_cpus_${cpu_per_socket}_nic_${netdevs_count}.

If directory already exists and your scenario differs - add `_1` or `_2` suffix.

For example: netutils-linux/examples/sockets_2_cpus_8_nic_4/

Add a README.md based on [README.tmplt.md](https://github.com/strizhechenko/netutils-linux/tree/master/examples)

```
git status
git add -p
git commit -m "Added(examples): success story of $your_or_your_company_name"
git push origin master
```

Open pull request to this repo.
