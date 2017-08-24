# How this work?

1. server-info-collect collects raw stdout's of few commands to gather data about system such as network interfaces, cpus, disks, memory, etc in an tarball. It usually doesn't used manually.
2. server-info show - run server-info-collect and show you a YAML output based on collected data.
3. server-info rate - rate collected data in scale from 1 (poor performance) to 10 (excelent performance)
