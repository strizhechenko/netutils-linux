These "bugs" will never be fixed:

- No `bridge` util in CentOS 6.4 (`iproute-2.6.32-23.el6.x86_64`). Solution: `yum -y install iproute`
- If you try to run it on CentOS 7 with python2.7 you may get tracebacks with YAML. Solution is to install dependencies via Yum: `yum install PyYAML.x86_64 python2-pyyaml.noarch python-prettytable.noarch`
