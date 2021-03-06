---
categories:
  - Cloud Computing & Virtualization
  - Essentials

tags:
  - Containers
  - Security
  - Docker
  - Credentials
  - Secrets
  - Vault

slug: managing-secrets-during-docker-build
title: "Managing Secrets During Docker Build"
date: 2021-03-04T22:46:31Z
draft: true
toc: true
---

What would be the best way to manage my secrets during a docker build?

Checking official and unofficial projects available in [hub.docker.com](https://hub.docker.com),
I have collected the 4 (four) most common cases on how users are storing and managing their secrets.

There are cases that during the build you would use a token or secret file for fetch information from a 
repo or other application to setup a configuration that will not be possible during runtime.

Some of those cases also doesn't fit the multistage building as fetching a package from pip.

## Scenarios

I need to install a `python` using a private pip that I created for this lab.

To achieve that you only need to add `pip.conf` file as below to `/root/.pip/pip.conf`.

```ini
[global]
index-url = https://hugo.prudente:My$3cr3tP4$$@private.pip/playlist
timeout=60
extra-index-url = https://pypi.python.org/simple
```

Looks simple, let's see how we manage it.

### Method 1

Here we copy the `pip.conf` to the container and don't remove it on the end.

```Dockerfile
FROM python:latest

COPY pip.conf /root/.pip/pip.conf

RUN pip install playlist
```

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker build -t secret:v1 .

on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker history secret:v1
IMAGE          CREATED              CREATED BY                                      SIZE      COMMENT
0d6589d4b95f   About a minute ago   RUN /bin/sh -c pip install playlist # bui…   14.1MB    buildkit.dockerfile.v0
<missing>      4 minutes ago        COPY pip.conf /root/.pip/pip.conf # buildkit    200B      buildkit.dockerfile.v0
<missing>      10 days ago          /bin/sh -c #(nop)  CMD ["python3"]              0B
```

Let's check if the file on the end of the build is present and it was leaked.

```
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
❯ docker run -it secret:v1 cat /root/.pip/pip.conf
[global]
index-url = https://hugo.prudente:My$3cr3tP4$$@private.pip/playlist
timeout=60
extra-index-url = https://pypi.python.org/simple
```

### Method 2

Here we copy the `pip.conf` to the container and remove it with a `RUN` statement on the end.

```Dockerfile
FROM python:latest

COPY pip.conf /root/.pip/pip.conf

RUN pip install playlist
RUN rm /root/.pip/pip.conf
```

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker build -t secret:v2 .

on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker history secret:v2
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
42f04cdc6577   6 seconds ago   RUN /bin/sh -c rm /root/.pip/pip.conf # buil…   0B        buildkit.dockerfile.v0
<missing>      4 minutes ago   RUN /bin/sh -c pip install playlist # bui…   14.1MB    buildkit.dockerfile.v0
<missing>      7 minutes ago   COPY pip.conf /root/.pip/pip.conf # buildkit    200B      buildkit.dockerfile.v0
<missing>      10 days ago     /bin/sh -c #(nop)  CMD ["python3"]              0B
```

Let's check again if the file was present.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker run -it secret:v2 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: No such file or directory
```

### Method 3

Here we copy the `pip.conf` to the container and remove it in the same `RUN` statement as the `pip install`

```Dockerfile
FROM python:latest

COPY pip.conf /root/.pip/pip.conf

RUN pip install playlist && rm /root/.pip/pip.conf
```

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker build -t secret:v3 .

on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker history secret:v3
IMAGE          CREATED              CREATED BY                                      SIZE      COMMENT
a2bf2672abaf   About a minute ago   RUN /bin/sh -c pip install playlist && rm…   14.1MB    buildkit.dockerfile.v0
<missing>      17 minutes ago       COPY pip.conf /root/.pip/pip.conf # buildkit    200B      buildkit.dockerfile.v0
<missing>      10 days ago          /bin/sh -c #(nop)  CMD ["python3"]              0B
```

Let's check once more if the file was present.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker run -it secret:v3 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: No such file or directory
```

### Method 4

Here we create the `pip.conf` using the `generate.sh` script that receive the
`SECRET` as `ARG` with the `--build-arg` options and we remove it on the same `RUN` statement.

```bash
#!/bin/sh

SECRET=$1

mkdir -p /root/.pip
cat > /root/.pip/pip.conf << EOF
[global]
index-url = https://hugo.prudente:${SECRET}@private.pip/playlist
timeout=60
extra-index-url = https://pypi.python.org/simple
EOF
```

```Dockerfile
FROM python:latest

ARG SECRET

COPY generate.sh /generate.sh

RUN /generate.sh ${SECRET} && pip install playlist && rm /root/.pip/pip.conf
```

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker build -t secret:v4 --progress plain --build-arg SECRET=My$3cr3tP4$$ .

➜ on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker history -H secret:v4
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
d2ca3623139f   2 minutes ago   RUN |1 SECRET=My$3cr3tP4$$ /b…   14.1MB    buildkit.dockerfile.v0
<missing>      2 minutes ago   COPY generate.sh /generate.sh # buildkit        261B      buildkit.dockerfile.v0
<missing>      2 minutes ago   ARG SECRET                                      0B        buildkit.dockerfile.v0
<missing>      10 days ago     /bin/sh -c #(nop)  CMD ["python3"]              0B
```

Last but not least, let's check the presece of the file.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
❯ docker run -it secret:v4 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: No such file or directory
```

The credential is not on the `pip.conf` file but it's visible during the `docker history`.

### Preliminary Results

Here is a matrix on where our secrets have been leaked.


| Method        | Runtime                              |Inspection                           |
| ------------- |:------------------------------------:| -----------------------------------:|
| secret:v1     | <span style="color:red">Yes</span>   | <span style="color:green">No</span> |
| secret:v2     | <span style="color:green">No</span>  | <span style="color:green">No</span> |
| secret:v3     | <span style="color:green">No</span>  | <span style="color:green">No</span> |
| secret:v4     | <span style="color:green">No</span>  | <span style="color:red">Yes</span>  |

With the preliminary results we can already exclude methods 1 and 4 as we can
consider them insecure due to the credentials being visible at some point. 

The method 4, I also used `--build-args SECRET=${SECRET}` and the secrets
leaks on the same way.

## Dive Deep

### OverlayFS

Is the kernel implementation for a union-filesystem, an overlay-filesystem tries
to present a filesystem which is the result over overlaying one filesystem on
top of the other.

![overlayfs.png](/2021/03/overlayfs.png)

In short taking the example of the image above imagine you have 2 directories
the **lower** and **upper** where the **lower** is a read-only directory for the
consumer, but they are still read-write from the Linux Operational system.

When a file is modified on the **upper** the change happens normally but if a
change is made on a file of the **lower** directory a copy of it is created on the
**upper** to become accessible, once the modification is complete another
process is responsible to fetch the modification and write on the **lower**
directory.

So this union of directories merged together as one unique block limited by the
cgroups is what docker and it's storage driver uses on our example.

The AUFS that's also a union-filesystem also presents the same behaviour,
although some of locations may be slightly different.

### Checking the Filesystem

Now that I know how OverlayFS works let's isolate the directories (layers) used
by the `python:latest` so we can filter out only the ones that we are interested
on, the ones that have `pip.conf` file.

Inspect the containers I can find the directories used on the OverlayFS.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker inspect python:latest | grep Dir | grep -Eo "([a-z0-9]{25,64})"
9e7c768dda91c4fa7ed6a57c7cb784834033bff92bd11ff6d062d4de11c0f898
17bf53c98685ae36487eb55f0d2256d168f210a688ef51deef760de1a699cbdf
4cb1dbbf58a2b1ca8df6d9d977a66fe918aee21434fcd656f1a68f1f412d75ff
358dd0944f115e2a273c5259dd1432b44e36908cf223f8ce0d9f74550430f577
c034592b1a26552525742ed81e7fbce2139817b634d48db8349dbebf15a45914
19d471e0407c0f1ca14eb1cb8c46aaef9357037cad5dc170cb6a4af3c1feab40
e005796f193e62e9db78de1df20999daca1a96a0bebed19c1dd906b1b4da8542
badc6aa65b2d3f10b0cdff3fc04bf3a64b551af1dd9e01b6ecd38ed71abdc3da
8d6ff96b718838005288a94cdc9fd408d1f70d7e9cbab678ebeb4521d11b366d

on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker inspect python:latest | grep Dir | grep -Eo "([a-z0-9]{25,64})" > layers.python
```

With the layers saved in the file `layers.python` I can use a similar command to
exclude the know python layers and get only the ones added by our build. 

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker inspect secret:v1 | grep Dir | grep -Eo "([a-z0-9]{25,64})" | grep -v -f layers.python  | uniq
e1kq2j71b7clcwtn0lbmqa1g9
v6zy2xgzrow2mgpyq9d0vch6l

➜ docker inspect secret:v2 | grep Dir | grep -Eo "([a-z0-9]{25,64})" | grep -v -f layers.python  | uniq
v6zy2xgzrow2mgpyq9d0vch6l
e1kq2j71b7clcwtn0lbmqa1g9
oudofb9c0iaqog9sff81f8053

on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker inspect secret:v3 | grep Dir | grep -Eo "([a-z0-9]{25,64})" | grep -v -f layers.python  | uniq
e1kq2j71b7clcwtn0lbmqa1g9
hqsrze873a2uz7tjsgbqdo3sd

on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker inspect secret:v4 | grep Dir | grep -Eo "([a-z0-9]{25,64})" | grep -v -f layers.python  | uniq
78gz619okusgrq4jo4ek863ug
oq22x88p26hzqmr1w1qpf8mm4
```

Now that we have the layers I have created a list just to make it simpler to
find it when we check the directory. 


#### Accessing the OverlayFS directories

Using one of the commands below as root you will find the entry point where
Docker Storage driver creates the file-system hierarchy used by the whole
eco-system. 

**Linux**

```bash
cd /var/lib/docker/
```

**MacOS**
```bash
docker run -it --rm --privileged --pid=host justincormack/nsenter1
cd /var/lib/docker/
```

Once in the `/var/lib/docker` directory using a simple `ls` and filtering the
layers previous stored in the temporary file and expanding it I could find the
specific layers that have the `pip.conf`

```bash
/var/lib/docker/overlay2 
# ls | grep -f /tmp/layers | xargs find | grep pip.conf
e1kq2j71b7clcwtn0lbmqa1g9/diff/root/.pip/pip.conf
hqsrze873a2uz7tjsgbqdo3sd/diff/root/.pip/pip.conf
oudofb9c0iaqog9sff81f8053/diff/root/.pip/pip.conf
```
So I accessed each of of those to confirm if the file was present or if was just
its shadow left by the directory union. 

```bash
/var/lib/docker/overlay2 
# cat e1kq2j71b7clcwtn0lbmqa1g9/diff/root/.pip/pip.conf
[global]
index-url = https://hugo.prudente:My$3cr3tP4$$@private.pip/playlist
timeout=60
extra-index-url = https://pypi.python.org/simpl

/var/lib/docker/overlay2 
# cat hqsrze873a2uz7tjsgbqdo3sd/diff/root/.pip/pip.conf
cat: can\'t open 'hqsrze873a2uz7tjsgbqdo3sd/diff/root/.pip/pip.conf': No such device or address

/var/lib/docker/overlay2 
# cat oudofb9c0iaqog9sff81f8053/diff/root/.pip/pip.conf
cat: can\'t open 'oudofb9c0iaqog9sff81f8053/diff/root/.pip/pip.conf': No such device or address
```

So 1 of 3 layers have the file present so I have checked from which container
that layer belong to and here's the surprise.

That 1 layer is shared with 3 of 4 builds that we have created, meaning that
during a `docker pull` three diferente containers could leak my `pip.conf`
secret.

## Results

The updated matrix consolidating the results on where our secrets have leaked.

| Method        | Runtime       |Inspection  | OverlayFS |
| ------------- |:-------------:| ----------:|----------:|
| secret:v1     | Yes           | No         |Yes        |
| secret:v2     | No            | No         |Yes        |
| secret:v3     | No            | No         |Yes        |
| secret:v4     | NO            | Yes        |No         |

So even knowing that the file is not acessible from the container directly if
you have access to pull the container on a full read-write system you would be
able to retreive the secrets.

But now what's the best way to build the container and do not have such issue?

## Solution

From 18.09 or newer Docker have introduced the Docker BuildKit that brings some
extra funcionality to the Docker builds. 

The builds using BuildKit different from the legacy allows the usage of the
`--secret` that allows the capacity of binding a file during build runtime
similar to the tradicional runtime that we achieve with `-v` option.

It's usage is quite simple let's build a container and run our tests again.

```Dockerfile
FROM python:latest

RUN --mount=type=secret,id=pip.conf,dst=/root/.pip/pip.conf \
      pip install playlist
```

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker build --file Dockerfile  --secret id=pip.conf,src=pip.conf -t secret:v5 .
```

Now that we have the `secret:v5` build lets confirm.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker history secret:v5
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
266a21bb36ae   36 seconds ago   RUN /bin/sh -c pip install playlist # bui…   14.1MB    buildkit.dockerfile.v0
<missing>      11 days ago      /bin/sh -c #(nop)  CMD ["python3"]              0Bi
```

The history in this case is clean, not even mention the mount for `pip.conf`

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
❯ docker run -it secret:v5 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: No such file or directory
```

The file is also not present on the system.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
❯ docker inspect secret:v5 | grep Dir | grep -Eo "([a-z0-9]{25,64})" | grep -v -f layers.python  | uniq
cnpw0dw9o05lmdz3j9j62jzpt

on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
/var/lib/docker/overlay2 # 
ls cnpw0dw9o05lmdz3j9j62jzpt | xargs find | grep pip.conf
find: committed: No such file or directory
find: diff: No such file or directory
find: link: No such file or directory
find: lower: No such file or directory
find: work: No such file or directory
```

And the most important one the file doesn't exist on the layer/directory that we just
created meaning that if we use in a base image our scretes are safe. 

## References

* https://docs.docker.com/develop/develop-images/build_enhancements/
* https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html
* https://docs.docker.com/storage/storagedriver/overlayfs-driver/
