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

slug: usando-aws-network-acls-com-natgateway
title: "Usando AWS Network ACLs com NAT Gateway"
date: 2020-07-11T13:09:21+02:00
draft: false
toc: true
---

É muito comum os erros feitos durante configurações de AWS Network ACLs quando adicionando a camada extra de segurança na VPC.

Dado o fato da Network ACL ser **stateless**, que significa que a regra de Entrada (Inbound), precisa bater com a de Saída (Oubound).

Com este post, você aprenderá identificar tais particularides usando o ambiente do AWS ElasticBeanstalk como exemplo, devido sua sensibilidade quanto aos requisitos de acesso a rede.

## Problemas Comuns

* Falha do acesso a qualquer endereço HTTPS/TLS  resultando em timeout.
* Falha para sincronizar servidores NTP

## Diferença entre Security Groups e Network ACL (NACL)

A diferença principal entre o Security Group e a Network ACL (NACL) é o contexto que eles são aplicados e os tipo de regras.

* Security Group:
  Stateful: Não necessita regra que permita a resposta para uma requisição de entrada.
  Local: É aplicado somente na instância ou serviço que o Security Group é anexado diretamente.

* Network ACL:
  Stateless: Necessita de regra que permita a resposta para uma requisição de entrada.
  Global: É aplicado a todos os serviços que utilizam a subnet que a NACL é anexado diretamente.

![itlandscape.png](/2020/11/nacl-example-diagram.png)

## Cenário 1 - (Web Tier) Subnet publica com Network ACL sem AWS NAT Gateway.

Usando o diagrama abaixo como exemplo para a configuraçãp da Network ACL para nosso ambiente AWS ElasticBeanstalk.

Diagrama:

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

Como apresentado nos erros comuns, o fluxo simplificado UDP e HTTPS da analise de pacotes do TCPDUmp mostra 2 (dois) retornos de uma EC2 que pertence ao nosso ambiente.

```bash
UDP 172.31.0.31:123 > 0.amazon.pool.ntp.org
UDP 0.amazon.pool.ntp.org > 172.31.0.31:2000
 
TCP 172.31.0.31:443 > aws.amazon.com
TCP aws.amazon.com > 172.31.0.31:3000
```

Na analise do pacote analisamos que a porta de retorno é efemera, e como sabemos que as Network ACL são stateless nós precisamos levar isso em consideração na criação de nossas regras.

### Solução

A solução, neste caso, é a mistura de regras de Security Group (SG-001) e Network ACLs (ACL-001):

***Security Group*** apresenta regras de entrada para TCP/HTTP, TCP/HTTPS nas portas 80 e 443 de todo lugar e regra de saida para todo protocolo todo destino partindo da instância.


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

Nós sabemos que o ElasticBeanstalk faz muito mais que servir tráfego, os agentes que conectam com as APIs AWS precisam de liberação também, com isso notamos um padrão extra nas Network ACLs.

* Regras 102 e 103 permitem entrada nas portas 80 e 443 seguidos de regras de saida também nomeadas 103 e 104 porém agora com portas efêmeras, já que sabemos que a porta muda na resposta.
* Regras 202 e 203 são usadas na ordem reversa apra permitir saida da EC2 para APIs AWS, onde trataremos o Outbound como Entrada e o Inbound como Saída pois a ACL está nos trancando dentro dela.

## Cenário 2 - (Worker Tier) Subnet Privada com Network ACL e AWS NAT Gateway.

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

Como antes apresentado nos problemas comuns, o trafego UDP e HTTPS do TCPDump é analisado e agora ele mostra as mesmas 2 (duas) ações da EC2 que pertencem ao ambiente AWS ElasticBeanstalk.

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

Como antes apresentado nos problemas comuns, o trafego UDP e HTTPS do TCPDump é analisado e agora ele mostra 4 (quatro) pares com um nó extra retornando da mesma ação, com diferente portas.

Isso acontece por um comportamento particular do AWS NAT Gateway que encapsula os pacotes novamente para atingir uma performance superior, causando a mudança extra de porta no cabeçalho do pacote durante seu ciclo de vida.

It happens due to a particular behavior of the AWS NAT Gateway. AWS Nat Gateway encapsulates packets to achieve higher performance, causing the change on the packet header for the port of destination during its life cycle. 

### Solução

A solução, neste caso, in this case, é a mistura de regras de Security Group (SG-002) e Network ACLs (ACL-002) agora incluindo também a ACL-003 dedicada para o NAT Gateway. 

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

Novamente podemos ver o par de regras Network ACL, porém temos um par extra para o NAT Gateway.

* Regras 102 e 103 permitem entrada nas portas 80 e 443 seguidos de regras de saida também nomeadas 103 e 104 porém agora com portas efêmeras, já que sabemos que a porta muda na resposta.
* Regras 202 e 203 são usadas na ordem reversa apra permitir saida da EC2 para APIs AWS, onde trataremos o Outbound como Entrada e o Inbound como Saída pois a ACL está nos trancando dentro dela.
* Esperaríamos somente trafego de saida para NAT Gateway, mas devido a encapsulação, NAT Gateway abre uma nova conexão TCP com o backend causando as portas mudarem novamente.

Esses problemas só acontecem com NAT Gateway se você aumentar a segurança na Network ACL, a NACL padrão da AWS permite trafego de entrada e saida para todo lugar por padrão.

Referências:
* [AWS User Guide for VPC ACLs](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_ACLs.html)
* [AWS User Guide for VPC NAT Gateway](http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/vpc-nat-gateway.html)

