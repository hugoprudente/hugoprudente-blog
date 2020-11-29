---
categories:
# - Protocol
- Cloud Computing & Virtualization
# - Storage
- Networking
# - Monitoring
# - Support Software
# - Essentials
# - Messaging 
# - Automation
# - Programming
- OS

tags:
## - Protocol
# - IMAP/POP3
- HTTP
- UDP
- TCP
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

##OS
- Linux
# - Unix
# - Windows
# - FreeBSD
# - GentooBSD
# - Ubuntu
# - Debian
# - Amazon Linux
# - Kali Linux

slug: using-aws-network-acls-with-natgateway
title: "Using AWS Network ACLs With NAT Gateway"
date: 2020-07-11T13:09:21+02:00
draft: true
toc: true
---

It’s quite common the mistakes made when using the AWS Network ACLs for adding that extra layer of security in your VPC.

Given the fact that Network ACLs are **stateless**, meaning that the Inbound (Ingress) should have a matching rule for Outbound (Egress).

With this post, you will learn how to identify such particularities using an AWS ElasticBeanstalk environment as an example, due to its sensitivity regarding network access requirements.

## Common Issues

* Fail to access any HTTPS/TLS endpoint resulting in timeout
* Fail to sync NTP servers

## Difference between Security Group and Network ACL (NACL)

The main difference between the Security Group and the Network ACL (NACL) is the
the context where they are applied and the type of rules they provided.

* A Security Group:
  Stateful: Therefore you don't need a rule that allows response traffic for inbound requests.
  Local: Therefore it applies only to the instance or service to which the security group is attached to. 

* A Network ACL:
  Stateless: Therefore this rule is required to allow response traffic for inbound requests on the outbound rules.
  Global: Therefore it applies to all services that are placed on the subnet that is attached to.

![itlandscape.png](/2020/11/nacl-example-diagram.png)

## Scenario 1 - (Web Tier) Public Subnet with Network ACL without AWS NAT Gateway.

Using the diagram below as an example to configure the Network ACL's for an ElasticBeanstalk environment.

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

As presented on the common issues, the simplified flow for UDP and HTTPS TCPDump packet below displays the return of 2 (two) actions from the EC2 belonging to the ElasticBeanstalk test environment.

```bash
UDP 172.31.0.31:123 > 0.amazon.pool.ntp.org
UDP 0.amazon.pool.ntp.org > 172.31.0.31:2000
 
TCP 172.31.0.31:443 > aws.amazon.com
TCP aws.amazon.com > 172.31.0.31:3000
```
As we notice from the packet analysis the returning port is ephemeral and as we already know that Network ACL are stateless we need to account for that during the rules creation. Due to the Security Group being stateful, the above behavior will work properly. 

### Solution

The solution, in this case, is a mix between the Security Group (SG-001) and the Network ACLs (ACL-001) where we can see:

***Security Group*** presents inbound traffic for TCP/HTTP, TCP/HTTPS for standard ports 80 and 443 from everywhere and outbound traffic from the instance to everywhere.


#### Security Group Inbound Rule (SG-001)
```
Type  |Protocol |Port Range |Source
--------|-----------|-----------|------
HTTP  |TCP  |80 |0.0.0.0/0
HTTPS |TCP  |443  |0.0.0.0/0
```
#### Security Group Outbound Rule (SG-001)
```
Type  |Protocol |Port Range |Source
--------|-----------|-----------|------
All |Traffic  |ALL  |ALL  |0.0.0.0/0
```


#### Network ACL Inbound (ACL-001)
```
Rule #  Type  Protocol  Port Range  Destination Allow / Deny
102 HTTP (80) TCP (6) 80  0.0.0.0/0 ALLOW
103 HTTPS (443) TCP (6) 443 0.0.0.0/0 ALLOW
201 Custom TCP Rule TCP (6) 1024-65535  0.0.0.0/0 ALLOW
202 Custom UDP Rule UDP (17)  123 0.0.0.0/0 ALLOW
* ALL Traffic ALL ALL 0.0.0.0/0 DENY
```
#### Network ACL Outbond (ACL-001)
```
Rule #  Type  Protocol  Port Range  Destination Allow / Deny
101 HTTP (80) TCP (6) 80  0.0.0.0/0 ALLOW
202 HTTPS (443) TCP (6) 443 0.0.0.0/0 ALLOW
102 Custom TCP Rule TCP (6) 1024-65535  0.0.0.0/0 ALLOW
103 Custom UDP Rule)  UDP (17)  1024-65535  0.0.0.0/0 ALLOW
* ALL Traffic ALL ALL 0.0.0.0/0 DENY
```

As we know that ElasticBeanstalk does more than serve traffic but also has agents that connect to AWS API's we notice two different sets of configurations in the Network ACL's.

* Rules 102 and 103 allow inbound traffic for ports 80 and 443 following by its outbound pair, the 102 and 103 that are responsible to allow ephemeral port out to answer the requests.
* Rules 202 and 203 are using in the reverse order, an agent will post from the EC2 to AWS API, we analyze it inverting the tables. In this case, outbound requires 80 and 443 for the request, and the response will return in an ephemeral port on the inbound rules.

## Scenario 2 - (Worker Tier) Private Subnet with Network ACL and AWS NAT Gateway.

Again using the diagram below as an example to configure the Network ACL's for an ElasticBeanstalk environment.


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
|   |  SG-002  |   |
|   +----------+   |
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

Same as before as presented on the common issues, the simplified flow for UDP and HTTPS TCPDump packet below displays the return of 2 (two) actions from the EC2 belonging to the ElasticBeanstalk test environment.

```
UDP 172.31.0.31:123 > 172.31.0.34:2000
UDP 172.31.0.34:2000 > 0.amazon.pool.ntp.org
UDP 0.amazon.pool.ntp.org > 172.31.0.34:2000
UDP 172.31.0.34:2000 > 172.31.0.31:3000
 
TCP 172.31.0.31:443 > 172.31.0.33:2000
TCP 172.31.0.33:2000 > aws.amazon.com
TCP aws.amazon.com > 172.31.0.33:3000
TCP 172.31.0.33:3000 > 172.31.0.31:3000
```

We can see that this is a little bit different than before, now 4 (four) pairs of packets with a extra jump returning different ports for each pair.  

It happens due to a particular behavior of the AWS NAT Gateway. AWS Nat Gateway encapsulates packets to achieve higher performance, causing the change on the packet header during its life cycle. 

### Solution

The solution, in this case, is a also a mix between the Security Group (SG-002) and the Network ACLs but this case ACL-002 and ACL-003 where we can see:

#### Security Group Inbound Rule (SG-002)
```
Type  Protocol  Port Range  Source
HTTP  TCP 80  0.0.0.0/0
Custom UDP  UDP 123 0.0.0.0/0
Custom UDP  UDP 1024-65535  0.0.0.0/0
Security Group Outbond Rule (SG-002)
Type  Protocol  Port Range  Source
All Traffic ALL ALL 0.0.0.0/0
```
#### Network ACL Inbound - Private Subnet (ACL-002)
```
Rule #  Type  Protocol  Port Range  Destination Allow / Deny
102 HTTP (80) TCP (6) 80  0.0.0.0/0 ALLOW
103 HTTPS (443) TCP (6) 443 0.0.0.0/0 ALLOW
202 Custom TCP Rule TCP (6) 1024-65535  0.0.0.0/0 ALLOW
203 Custom UDP Rule UDP (17)  123 0.0.0.0/0 ALLOW
* ALL Traffic ALL ALL 0.0.0.0/0 DENY
```
#### Network ACL Outbond - Private Subnet (ACL-002)
```
Rule #  Type  Protocol  Port Range  Destination Allow / Deny
202 HTTP (80) TCP (6) 80  0.0.0.0/0 ALLOW
203 HTTPS (443) TCP (6) 443 0.0.0.0/0 ALLOW
102 Custom TCP Rule TCP (6) 1024-65535  0.0.0.0/0 ALLOW
103 Custom UDP Rule)  UDP (17)  1024-65535  0.0.0.0/0 ALLOW
* ALL Traffic ALL ALL 0.0.0.0/0 DENY
```
#### Network ACL Inbound - Public Subnet (ACL-003)
```
Rule #  Type  Protocol  Port Range  Destination Allow / Deny
102 HTTP (80) TCP (6) 80  0.0.0.0/0 ALLOW
103 HTTPS (443) TCP (6) 443 0.0.0.0/0 ALLOW
202 Custom TCP Rule TCP (6) 1024-65535  0.0.0.0/0 ALLOW
203 Custom UDP Rule UDP (17)  123 0.0.0.0/0 ALLOW
* ALL Traffic ALL ALL 0.0.0.0/0 DENY
```
#### Network ACL Outbond - Public Subnet (ACL-003)
```
Rule #  Type  Protocol  Port Range  Destination Allow / Deny
202 HTTP (80) TCP (6) 80  0.0.0.0/0 ALLOW
203 HTTPS (443) TCP (6) 443 0.0.0.0/0 ALLOW
102 Custom TCP Rule TCP (6) 1024-65535  0.0.0.0/0 ALLOW
103 Custom UDP Rule)  UDP (17)  1024-65535  0.0.0.0/0 ALLOW
* ALL Traffic ALL ALL 0.0.0.0/0 DENY
```

Again we have the rule set for the Network ACL where.

* ACL-002 Rules 102 and 103 allow inbound traffic for ports 80 and 443 following by its outbound pair, the 102 and 103 that are responsible to allow ephemeral port out to answer the requests.
* ACL-002 Rules 202 and 203 are using in the reverse order, an agent will post from the EC2 to AWS API, we analyze it inverting the tables. In this case, outbound requires 80 and 443 for the request, and the response will return in an ephemeral port on the inbound rules.
* We would expect only outbound traffic for the NAT Gateway, but due to the encapsulation, NAT Gateway is opening a new TCP connection with the backend using the new port requiring the same set as before.

These problems only happen if you tight the security on the Network ACL used by the AWS Natgateway, as the AWS default NACL that allows all the traffic inbound and outbound.

References:
* [AWS User Guide for VPC ACLs](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_ACLs.html)
* [AWS User Guide for VPC NAT Gateway](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-nat-gateway.html)