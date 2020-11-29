---
categories:
# - Protocol
# - Cloud Computing & Virtualization
# - Storage
# - Monitoring
# - Support Software
# - Essentials
# - Messaging 
# - Automation
# - Programming
# - OS

tags:
## - Protocol
# - IMAP/POP3
# - HTTP
# - SMTP
# - DNS
# - LDAP
# - SSH
# - VPN

## Cloud Computing 
# - Computing
# - Orchestration
# - Storage
# - Virtualization
# - Containers

## Storage
# - Cloning
# - Backups
# - Distributed Filesystem
# - NOSQL
# - RDBMS


## - Monitoring
# - Statistics
# - Metric & Metric Collection
# - Monitoring 


## Support Software
# - Control Panel
# - Web Emails
# - News Letter
# - Project Management
# - Ticketing System
# - IT Asset Management
# - Wikis
# - Code Review
# - Collaborative Software
# - Communication

## Essentials
# - Editors
# - Repositories
# - Security
# - Version Control
# - Packaging
# - Troubleshoot
# - Books

## - Messaging 
# - Log Management
# - Queueing

## Automation
# - Configuration Management
# - Configuration Management Database
# - Service Discovery
# - Network Configuration Management
# - Continuous Integration & Continuous Deployment (CICD)

## Programming
# - Java
# - GoLang
# - Python
# - Rust
# - C++
# - C
# - JavaScript
# - NodeJS
# - DotNet
# - Ruby
# - PHP
# - Bash

## OS
# - Linux
# - Unix
# - Windows
# - FreeBSD
# - GentooBSD
# - Ubuntu
# - Debian
# - Amazon Linux
# - Kali Linux
# - 

slug: using-aws-network-acls-with-natgateway
title: "Using AWS Network ACLs With NAT Gateway"
date: 2020-07-11T13:09:21+02:00
draft: true
toc: false
---

It’s quite common the mistakes made when using the AWS Network ACLs for adding that extra layer of security in your VPC.

This is given to the fact that Network ACLs are **stateless**, meaning that the Inbound (Ingress) should have a matching rule for Outbound (Egress).

With this post, you will learn how to identify such particularities using an AWS ElasticBeanstalk environment, as you can easily break it due to the internal AWS agents running internally.

## Common Issues

* Fail to access any HTTPS/TLS endpoint resulting in timeout
* Fail to sync NTP servers

## Scenario 1 - (Web Tier) Public Subnet with Network ACL

Using the diagram bellow as example to configure the Network ACL's for an ElasticBeanstalk environment.

Diagram:

```
+------------------+
|                  |
|   +----------+   |
|   | INSTANCE |   |
|   +----------+   |
|   |  SG-001  |   |
|   +----------+   |
+------------------+
|    Subnet Pub    |
+------------------+
         +   +--------------+
         |---| ACL-001      |
         v   +--------------+
+------------------+
|       IGW        |
+------------------+
```

As told on the common issues the simplified network flow for UDP and HTTPS bellow displays the return of the 2 (two) common actions performed by an EC2 that belongs to an ElasticBeanstalk group.

```bash
UDP 172.31.0.31:123 > 0.amazon.pool.ntp.org
UDP 0.amazon.pool.ntp.org > 172.31.0.31:2000
 
TCP 172.31.0.31:443 > aws.amazon.com
TCP aws.amazon.com > 172.31.0.31:3000
```

As we notice on the TCP dump snippet above, that the returning port is ephemeral and as the Network ACL are stateless we need to keep in mind this flow when creating the Network ACL.

## Solution

The solution on this case is a mix between the Security Group (SG-001) and the Network ACLs (ACL-001) were we can see

***Security Group*** presents an inbound traffic for TCP/HTTP, TCP/HTTPS for standard ports 80 and 443 from everyhere and outbound traffic from the instance to everywhere.

### Security Group Inbound Rule (SG-001)
Type	|Protocol	|Port Range	|Source
--------|-----------|-----------|------
HTTP	|TCP	|80	|0.0.0.0/0
HTTPS	|TCP	|443	|0.0.0.0/0

### Security Group Outbond Rule (SG-001)

Type	|Protocol	|Port Range	|Source
--------|-----------|-----------|------
All |Traffic	|ALL	|ALL	|0.0.0.0/0



### Network ACL Inbound (ACL-001)
Rule #	Type	Protocol	Port Range	Destination	Allow / Deny
100	SSH (22)	TCP (6)	22	0.0.0.0/0	ALLOW
102	HTTP (80)	TCP (6)	80	0.0.0.0/0	ALLOW
103	HTTPS (443)	TCP (6)	443	0.0.0.0/0	ALLOW
104	Custom TCP Rule	TCP (6)	1024-65535	0.0.0.0/0	ALLOW
200	Custom UDP Rule	UDP (17)	123	0.0.0.0/0	ALLOW
*	ALL Traffic	ALL	ALL	0.0.0.0/0	DENY
### Network ACL Outbond (ACL-001)
```
Rule #	Type	Protocol	Port Range	Destination	Allow / Deny
100	SSH (22)	TCP (6)	22	0.0.0.0/0	ALLOW
102	HTTP (80)	TCP (6)	80	0.0.0.0/0	ALLOW
103	HTTPS (443)	TCP (6)	443	0.0.0.0/0	ALLOW
104	Custom TCP Rule	TCP (6)	1024-65535	0.0.0.0/0	ALLOW
200	Custom UDP Rule)	UDP (17)	1024-65535	0.0.0.0/0	ALLOW
*	ALL Traffic	ALL	ALL	0.0.0.0/0	DENY
```


## Scenario 2 - (Worker Tier) Private Subnet with Network ACL
Diagram:
```
+------------------+
|                  |
|   +----------+   |
|   | INSTANCE |   |
|   +----------+   |
|   |  SG-002  |   |
|   +----------+   |
+------------------+
|  Subnet Private  |
+------------------+
          +
          |   +--------------+
          |---| ACL-002      |
          v   +--------------+
+------------------+
|                  |
|   +----------+   |
|   |  NAT GW  |   |
|   +----------+   |
|                  |
+------------------+
|    Subnet Pub    |
+------------------+
         +   +--------------+
         |---| ACL-003      |
         v   +--------------+
+------------------+
|       IGW        |
+------------------+
```
As told on the common issues the simplified network flow for UDP and HTTPS bellow displays the return of the 2 (two) common actions performed by an EC2 that belongs to an ElasticBeanstalk group on a private subnet that uses NAT Gateway to access the internet.

UDP 172.31.0.31:123 > 172.31.0.34:2000
UDP 172.31.0.34:2000 > 0.amazon.pool.ntp.org
UDP 0.amazon.pool.ntp.org > 172.31.0.34:2000
UDP 172.31.0.34:2000 > 172.31.0.31:3000
 
TCP 172.31.0.31:443 > 172.31.0.33:2000
TCP 172.31.0.33:2000 > aws.amazon.com
TCP aws.amazon.com > 172.31.0.33:3000
TCP 172.31.0.33:3000 > 172.31.0.31:3000
What happens in this case is that the NAT Gateway re-encapsulate the package to achieve max performance, causing an change of ports during the traffic making needing an cu

Solution
Security Group Inbound Rule (SG-002)
Type	Protocol	Port Range	Source
HTTP	TCP	80	0.0.0.0/0
Custom UDP	UDP	123	0.0.0.0/0
Custom UDP	UDP	1024-65535	0.0.0.0/0
Security Group Outbond Rule (SG-002)
Type	Protocol	Port Range	Source
All Traffic	ALL	ALL	0.0.0.0/0
Network ACL Inbound - Private Subnet (ACL-002)
Rule #	Type	Protocol	Port Range	Destination	Allow / Deny
100	SSH (22)	TCP (6)	22	0.0.0.0/0	ALLOW
102	HTTP (80)	TCP (6)	80	0.0.0.0/0	ALLOW
103	HTTPS (443)	TCP (6)	443	0.0.0.0/0	ALLOW
104	Custom TCP Rule	TCP (6)	1024-65535	0.0.0.0/0	ALLOW
200	Custom UDP Rule	UDP (17)	123	0.0.0.0/0	ALLOW
*	ALL Traffic	ALL	ALL	0.0.0.0/0	DENY
Network ACL Outbond - Private Subnet (ACL-002)
Rule #	Type	Protocol	Port Range	Destination	Allow / Deny
100	SSH (22)	TCP (6)	22	0.0.0.0/0	ALLOW
102	HTTP (80)	TCP (6)	80	0.0.0.0/0	ALLOW
103	HTTPS (443)	TCP (6)	443	0.0.0.0/0	ALLOW
104	Custom TCP Rule	TCP (6)	1024-65535	0.0.0.0/0	ALLOW
200	Custom UDP Rule)	UDP (17)	1024-65535	0.0.0.0/0	ALLOW
*	ALL Traffic	ALL	ALL	0.0.0.0/0	DENY
Network ACL Inbound - Public Subnet (ACL-003)
Rule #	Type	Protocol	Port Range	Destination	Allow / Deny
102	HTTP (80)	TCP (6)	80	0.0.0.0/0	ALLOW
103	HTTPS (443)	TCP (6)	443	0.0.0.0/0	ALLOW
104	Custom TCP Rule	TCP (6)	1024-65535	0.0.0.0/0	ALLOW
200	Custom UDP Rule	UDP (17)	123	0.0.0.0/0	ALLOW
201	Custom TCP Rule	UDP (17)	1024-65535	0.0.0.0/0	ALLOW
*	ALL Traffic	ALL	ALL	0.0.0.0/0	DENY
Network ACL Outbond - Public Subnet (ACL-003)
Rule #	Type	Protocol	Port Range	Destination	Allow / Deny
102	HTTP (80)	TCP (6)	80	0.0.0.0/0	ALLOW
103	HTTPS (443)	TCP (6)	443	0.0.0.0/0	ALLOW
104	Custom TCP Rule	TCP (6)	1024-65535	0.0.0.0/0	ALLOW
200	Custom UDP Rule)	UDP (17)	123	0.0.0.0/0	ALLOW
201	Custom TCP Rule	UDP (17)	1024-65535	0.0.0.0/0	ALLOW
*	ALL Traffic	ALL	ALL	0.0.0.0/0	DENY

References:
* [AWS User Guide for VPC ACLs](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_ACLs.html)
* [AWS User Guide for VPC NAT Gateway](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-nat-gateway.html)