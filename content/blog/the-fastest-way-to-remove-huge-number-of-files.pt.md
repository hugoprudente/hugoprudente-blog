---
title: "A maneira mais rápida de deletar um grande número arquivos"
slug: a-maneira-mais-rapida-de-deletar-um-grande-numero-de-arquivos
date: 2020-01-10T10:38:03Z
draft: false
toc: true
images:
categories:
  - SysAdmin
tags:
  - Linux
  - Tools
  - SysAdmin
---

Muitos anos atrás, devido a um erro no código da aplicação que trabalhavamos acabamos gerando aproximadamente 10 milhões de arquivos, acabando com os `inodes` do sistema. Devido aquele servidor não ter alta disponibilidade no momento fui a procura do ganso dos ovos de ouro e achei isso aqui.

Infelizmente o artigo original não está mais disponível, mas desse em dia em diante `rsync` é minha ferramenta principal de destruição em massa!

---

## Benchmark

Alguns dias atrás,  [Keith-Winstein](https://www.quora.com/profile/Keith-Winstein) respondeu o [Quora Posts](https://www.quora.com/How-can-someone-rapidly-delete-400-000-files), informando que meu benchmark não poderia ser reproduzido e que os tempos de delecção estavam muito lentos. Para ficar mais claro, pois naquele momento me computador poderia estar sobre carga, e poderia conter alguns erros eu refiz. Agora com uma nova máquina de rack, usando o  `/usr/bin/time` para um resultado mais refinado.


(O número de arquivos é 1000000. E cada um contém 0 de tamanho.)


| Command                                     | Elapsed  | System Time  | %CPU  | cs (Vol/Invol)  |
|---------------------------------------------|----------|--------------|-------|------------------|
| rsync -a –delete empty/ a                   | 10.60	   | 1.31	        | 95    | 106/22           |
| find b/ -type f -delete	                    | 28.51	   | 14.46        |	52    | 14849/11         |
| find c/ -type f \| xargs -L 100 rm          | 41.69	   | 20.60	      | 54    | 37048/15074      |
| find d/ -type f \| xargs -L 100 -P 100 rm   | 34.32	   | 27.82	      | 89    | 929897/21720     |
| rm -rf f                                    | 31.29	   | 14.80	      | 47    | 15134/11         |

### Saída Original

```
# method 1
~/test $ /usr/bin/time -v  rsync -a --delete empty/ a/
        Command being timed: "rsync -a --delete empty/ a/"
        User time (seconds): 1.31
        System time (seconds): 10.60
        Percent of CPU this job got: 95%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:12.42
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 0
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 24378
        Voluntary context switches: 106
        Involuntary context switches: 22
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0

# method 2
        Command being timed: "find b/ -type f -delete"
        User time (seconds): 0.41
        System time (seconds): 14.46
        Percent of CPU this job got: 52%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:28.51
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 0
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 11749
        Voluntary context switches: 14849
        Involuntary context switches: 11
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0
# method 3
find c/ -type f | xargs -L 100 rm
~/test $ /usr/bin/time -v ./delete.sh
        Command being timed: "./delete.sh"
        User time (seconds): 2.06
        System time (seconds): 20.60
        Percent of CPU this job got: 54%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:41.69
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 0
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 1764225
        Voluntary context switches: 37048
        Involuntary context switches: 15074
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0

# method 4
find d/ -type f | xargs -L 100 -P 100 rm
~/test $ /usr/bin/time -v ./delete.sh
        Command being timed: "./delete.sh"
        User time (seconds): 2.86
        System time (seconds): 27.82
        Percent of CPU this job got: 89%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:34.32
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 0
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 1764278
        Voluntary context switches: 929897
        Involuntary context switches: 21720
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0

# method 5
~/test $ /usr/bin/time -v rm -rf f
        Command being timed: "rm -rf f"
        User time (seconds): 0.20
        System time (seconds): 14.80
        Percent of CPU this job got: 47%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:31.29
        Average shared text size (kbytes): 0
        Average unshared data size (kbytes): 0
        Average stack size (kbytes): 0
        Average total size (kbytes): 0
        Maximum resident set size (kbytes): 0
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 176
        Voluntary context switches: 15134
        Involuntary context switches: 11
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0
```

### Especificação do Hardware

```
Summary:        HP DL360 G7, 2 x Xeon E5620 2.40GHz, 23.5GB / 24GB 1333MHz
Processors:     2 (of 16) x Xeon E5620 2.40GHz (16 cores)
Memory:         23.5GB
Disk:           cciss/c0d0 (cciss0): 300GB (4%) RAID-10
Disk-Control:   cciss0: Hewlett-Packard Company Smart Array G6 controllers, FW 3.66
OS:             RHEL Server 5.4 (Tikanga), Linux 2.6.18-164.el5 x86_64, 64-bit
```

## Benchmark Inicial

Ontem eu vi um post muito interessante sobre métodos de deletar arquivos em um único diretório. O metodo foi enviado por Zhenyu Lee no http://www.quora.com/How-can-someone-rapidly-delete-400-000-files e invez de utilizar xargs, Lee engenhosamente usou rsync com o --delete para sincronizar com um diretorio vazio. Após isso eu fiz uma comparacao de metodos e para minha surpresa o método de Lee era muito, mais muito, mais rápido que os outros.
 

| Command                                      | # of files  | Elapsed    |
|----------------------------------------------|-------------|------------|
| rsync -a –delete empty/ s1                   | 1000000	    | 6m50.638s  |
| find s2/ -type f -delete	                   | 1000000	    | 87m38.826s |
| find s3/ -type f \| xargs -L 100 rm          | 1000000	    | 83m36.851s |
| find s4/ -type f \| xargs -L 100 -P 100 rm   | 1000000      | 78m4.658s  |
| rm -rf s5                                    | 1000000	    | 80m33.434s |

### Especificação do Hardware

```
CPU: Intel(R) Core(TM)2 Duo CPU E8400 @ 3.00GHz
MEM: 4G
HD: ST3250318AS: 250G/7200RPM
```

## Notas de Rodapé
[1]: Voluntary Context Switches e Involuntary Context Switches são do /usr/bin/time

[2]: Como há uma pipeline, para o resultado ser o mais ácuro possivel ele foi envolto num bash script.



Original Post: http://linuxnote.net/jianingy/en/linux/a-fast-way-to-remove-huge-number-of-files.html 