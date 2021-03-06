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

slug: gerenciando-segredos-durante-docker-build
title: "Gerenciando Segredos Durante Docker Build"
date: 2021-03-04T22:46:31Z
draft: false
toc: true
---

Qual seria a melhor maneira de gerenciar meus segredos durante uma compilação do docker?

Verificando projetos oficiais e não oficiais disponíveis em [hub.docker.com] (https://hub.docker.com),
Reuni os 4 (quatro) casos mais comuns de como os usuários armazenam e gerenciam seus segredos.

Há casos em que durante a construção você usaria um token ou arquivo secreto para buscar informações de um
repositório ou outro aplicativo para definir uma configuração que não será possível durante o tempo de execução.

Alguns desses casos também não se encaixam na compilação multistage como obter um pacote do pip.

## Cenários

Preciso instalar um `python` usando um pip privado que criei para este laboratório.

Para conseguir isso, você só precisa adicionar o arquivo `pip.conf` conforme abaixo em` / root / .pip / pip.conf`.

```ini
[global]
index-url = https: //hugo.prudente: My$3cr3tP4$$@private.pip/playlist
tempo limite = 60
extra-index-url = https://pypi.python.org/simple
```

Parece simples, vamos ver como o administramos.

### Método 1

Aqui, copiamos o `pip.conf` para o contêiner e não o removemos no final.

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

Vamos verificar se o arquivo no final da compilação está presente e não.

```
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
❯ docker run -it secret:v1 cat /root/.pip/pip.conf
[global]
index-url = https://hugo.prudente:My$3cr3tP4$$@private.pip/playlist
timeout=60
extra-index-url = https://pypi.python.org/simple
```

### Método 2

Aqui, copiamos o `pip.conf` para o contêiner e o removemos com uma instrução` RUN` no final.

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

Vamos verificar novamente se o arquivo estava presente.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker run -it secret:v2 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: No such file or directory
```

### Método 3

Aqui, copiamos o `pip.conf` para o contêiner e o removemos na mesma instrução` RUN` do `pip install`

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

Vamos verificar mais uma vez se o arquivo estava presente.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker run -it secret:v3 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: No such file or directory
```

### Método 4

Aqui criamos o `pip.conf` usando o script` generate.sh` que recebe o
`SECRET` como` ARG` com as opções `--build-arg` e o removemos na mesma instrução` RUN`.

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

Por último, mas não menos importante, vamos verificar a presença do arquivo.

```bash
no ⛵ k3s (nerdweek) ~ / postar via 🐍 v3.9.1 (osx)
❯ docker run -it secret: v4 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: Esse arquivo ou diretório não existe
```

A credencial não está no arquivo `pip.conf`, mas é visível durante o` histórico do docker`.

### Resultados preliminares

Aqui está uma matriz de onde nossos segredos foram revelados.

| Método | Tempo de execução | Inspeção |
| ------------- |:------------------------------------:| -----------------------------------:|
| secret:v1     | <span style="color:red">Yes</span>   | <span style="color:green">No</span> |
| secret:v2     | <span style="color:green">No</span>  | <span style="color:green">No</span> |
| secret:v3     | <span style="color:green">No</span>  | <span style="color:green">No</span> |
| secret:v4     | <span style="color:green">No</span>  | <span style="color:red">Yes</span>  |

Com os resultados preliminares, já podemos excluir os métodos 1 e 4, pois podemos
considerá-los inseguros devido às credenciais serem visíveis em algum ponto.

O método 4, eu também usei `--build-args SECRET=${SECRET}` e os segredos foram revelados da mesma maneira.

## Mergulho profundo

### OverlayFS

É a implementação do kernel para um sistema de arquivos de união, um sistema de arquivos de sobreposição tenta
para apresentar um sistema de arquivos que é o resultado sobrepondo um sistema de arquivos em
em cima do outro.

![overlayfs.png](/2021/03/overlayfs.png)

Resumindo, pegando o exemplo da imagem acima, imagine que você tem 2 diretórios
o **inferior** e **superior**, onde o ** inferior ** é um diretório somente leitura para o
consumidor, mas eles ainda são de leitura e gravação do sistema operacional Linux.

Quando um arquivo é modificado no **superior**, a mudança acontece normalmente, mas se um
a mudança é feita em um arquivo do diretório **inferior**, uma cópia dele é criada no
**superior** para se tornar acessível, uma vez que a modificação seja concluída em outro
processo é responsável por buscar a modificação e escrever no ** inferior **
diretório.

Portanto, esta união de diretórios fundidos em um único bloco limitado pelo
cgroups é o que o docker e seu driver de armazenamento usa em nosso exemplo.

O AUFS que também é um sistema de arquivos de união também apresenta o mesmo comportamento,
embora alguns dos locais possam ser ligeiramente diferentes.

### Verificando o sistema de arquivos

Agora que sei como o OverlayFS funciona, vamos isolar os diretórios (camadas) usados
pelo `python: latest` para que possamos filtrar apenas aqueles que estamos interessados
on, aqueles que possuem o arquivo `pip.conf`.

Inspecione os contêineres, posso encontrar os diretórios usados ​​no OverlayFS.

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

Com as camadas salvas no arquivo `layers.python`, posso usar um comando semelhante para
exclua as camadas conhecidas do python e obtenha apenas aquelas adicionadas por nossa construção.

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

Agora que temos as camadas, criei uma lista apenas para torná-la mais simples
encontrá-lo quando verificarmos o diretório.


#### Acessando os diretórios OverlayFS

Usando um dos comandos abaixo como root, você encontrará o ponto de entrada onde
O driver Docker Storage cria a hierarquia do sistema de arquivos usada por todo
eco-sistema.

**Linux**

```bash
cd /var/lib/docker/
```

**MacOS**

```bash
docker run -it --rm --privileged --pid=host justincormack/nsenter1
cd /var/lib/docker/
```

Uma vez no diretório `/var/lib/docker` usando um simples` ls` e filtrando o
camadas anteriores armazenadas no arquivo temporário e expandindo-o eu poderia encontrar o
camadas específicas que têm o `pip.conf`

```bash
/var/lib/docker/overlay2 
# ls | grep -f /tmp/layers | xargs find | grep pip.conf
e1kq2j71b7clcwtn0lbmqa1g9/diff/root/.pip/pip.conf
hqsrze873a2uz7tjsgbqdo3sd/diff/root/.pip/pip.conf
oudofb9c0iaqog9sff81f8053/diff/root/.pip/pip.conf
```
Então, acessei cada um deles para confirmar se o arquivo estava presente ou apenas
sua sombra deixada pela união do diretório.

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

Portanto, 1 de 3 camadas tem o arquivo presente, então verifiquei de qual contêiner
essa camada pertence e aqui está a surpresa.

Essa 1 camada é compartilhada com 3 de 4 construções que criamos, o que significa que
durante um `docker pull`, três recipientes diferentes podem vazar meu` pip.conf`
segredo.

## Resultados

A matriz atualizada consolidando os resultados sobre onde nossos segredos vazaram.

| Método       | Tempo de execução| Inspeção   | OverlayFS |
| -------------|:---------------:|----------:|----------:|
| secret:v1    | Yes              | No         |Yes        |
| secret:v2    | No               | No         |Yes        |
| secret:v3    | No               | No         |Yes        |
| secret:v4    | NO               | Yes        |No         |

Portanto, mesmo sabendo que o arquivo não pode ser acessado diretamente do contêiner se
você tem acesso para puxar o contêiner em um sistema completo de leitura e gravação, você seria
capaz de recuperar os segredos.

Mas agora qual é a melhor maneira de construir o container e não ter esse problema?

## Solução

A partir de 18.09 ou mais recente, o Docker introduziu o Docker BuildKit que traz alguns
funcionalidade extra para as compilações do Docker.

As compilações usando BuildKit diferentes do legado permitem o uso do
`--secret` que permite a capacidade de vincular um arquivo durante o tempo de execução de compilação
semelhante ao tempo de execução tradicional que alcançamos com a opção `-v`.

Seu uso é bastante simples, vamos construir um contêiner e executar nossos testes novamente.

```Dockerfile
FROM python:latest

RUN --mount=type=secret,id=pip.conf,dst=/root/.pip/pip.conf \
      pip install playlist
```

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker build --file Dockerfile  --secret id=pip.conf,src=pip.conf -t secret:v5 .
```

Agora que temos a compilação `secret:v5`, vamos confirmar.

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
➜ docker history secret:v5
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
266a21bb36ae   36 seconds ago   RUN /bin/sh -c pip install playlist # bui…   14.1MB    buildkit.dockerfile.v0
<missing>      11 days ago      /bin/sh -c #(nop)  CMD ["python3"]              0Bi
```

O histórico neste caso é limpo, sem nem mencionar a montagem para `pip.conf`

```bash
on ⛵ k3s (nerdweek) ~/post via 🐍 v3.9.1 (osx)
❯ docker run -it secret:v5 cat /root/.pip/pip.conf
cat: /root/.pip/pip.conf: No such file or directory
```

O arquivo também não está presente no sistema.

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

E o mais importante, o arquivo não existe na camada / diretório que acabamos de
criado, o que significa que se usarmos em uma imagem de base, nossos scretes estão seguros.

## Referências

* https://docs.docker.com/develop/develop-images/build_enhancements/
* https://www.kernel.org/doc/html/latest/filesystems/overlayfs.html
* https://docs.docker.com/storage/storagedriver/overlayfs-driver/