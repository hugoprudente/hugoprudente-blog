---
categories:
- Cloud Computing & Virtualization

tags:
- Containers
- Nginx
- Google
- Kuberentes

slug: kubernetes-nginx-ingress-controller-vs-nginx-ingress-controller-for-kubernetes
title: "Kubernetes Nginx Ingress Controller vs Nginx Ingress Controller for Kubernetes"
date: 2020-01-21T21:23:25Z
draft: false
---

Vejo sempre pessoas com problemas utilizando o **Kubernetes Ingress Controller** tipo **Nginx**.

O principal problema reportado na comunidade é na anotação `nginx.ingress.kubernetes.io/rewrite-target: /` não funcionando.

A causa da *tag* não funcionando é do `ingres-controller` sendo utilizado. Vamos clarificar!

Geralmente vamos ao `google.com` e procuramos pelas seguintes palavras "kuberentes ingress controller", isso retornara 2 projetos **Oficiais**, por duas companhias diferentes.

* [NGINX Ingress Controller for Kubernetes](https://docs.nginx.com/nginx-ingress-controller/) by NGINX
* [Kubernetes Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/) by Kubernetes (Google)

Durante o troubleshoot o primeiro passo é definir qual `ingress-controller` do **Nginx** está sendo utilizado:

Com o **helm** podemos checar o repositorio do qual foi instalado:

Provided by NGINX
```bash
○ → helm repo add nginx-stable https://helm.nginx.com/stable
○ → helm search hub nginx-ingress
URL                                                     CHART VERSION   APP VERSION     DESCRIPTION                                       
https://hub.helm.sh/charts/nginx/nginx-ingress          0.4.1           1.6.1           NGINX Ingress Controller                          
```

Provided by Kubernetes
```bash
○ → helm repo add stable https://kubernetes-charts.storage.googleapis.com
○ → helm search hub nginx-ingress
URL                                                     CHART VERSION   APP VERSION     DESCRIPTION                                       
https://hub.helm.sh/charts/stable/nginx-ingress         1.29.3          0.27.1          An nginx Ingress controller that uses ConfigMap...
```

Alternativamente se a solucao nao foi instalada pelo **helm** podemos checar a origem da imagem do `ingres-controller` com o comando:

```bash
○ → kubectl describe deployment  | grep Image
    Image:       quay.io/kubernetes-ingress-controller/nginx-ingress-controller:0.27.1
    Image:       nginx/nginx-ingress:1.6.1
```

Do [NGINX Ingress Controller for Kubernetes](https://github.com/nginxinc/kubernetes-ingress/), GitHub confirmamos a propriadade da imagem **nginx-ingress:1.6.1**.

Do [Kubernetes Nginx Ingress Controller](https://github.com/kubernetes/ingress-nginx/), GitHub confirmamos a propriadade da imagem **nginx-ingress-controller:0.27.1**.

Agora que definimos o projeto que esta sendo utilizado vamos as configurações:

# NGINX Ingress Controller for Kubernetes

Mantido pela NGINX a documentação pode ser encontrada em [Nginx Ingress Controller for Kubernetes](https://docs.nginx.com/nginx-ingress-controller/):

As tags para este projeto são `nginx.org` e `nginx.com` para as funções pagas.

Exemplos explorando as funções deste projeto podem ser encontradas no [GitHub](https://github.com/nginxinc/kubernetes-ingress/tree/v1.6.1/examples)

Exemplo para funções rewrite:

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: cafe-ingress
  annotations:
    nginx.org/rewrites: "serviceName=tea-svc rewrite=/"
spec:
  rules:
  - host: cafe.example.com
    http:
      paths:
      - path: /tea/
        backend:
          serviceName: tea-svc
          servicePort: 80
```


# Kubernetes NGINX Ingress Controller

Mantido pela comunidade do Kubernetes a documentação pode ser encontrada em[Kubernetes Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/):

As tags para este projeto é `nginx.ingress.kubernetes.io/` e não possui funções extras.

Exemplos explorando as funções deste projeto podem ser encontradas no [GitHub](https://github.com/kubernetes/ingress-nginx/tree/master/docs/examples)

Exemplo para funções rewrite:

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: cafe-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - http:
      paths:
      - path: /tea
        backend:
          serviceName: tea-svc
          servicePort: 80
```

---

Estes projetos são alguns meses de diferença e não há uma explicação clara do porque o Kubernetes Ingress Controller escolheu exatamente o nesmo nome do projeto do NGINX que já estava sendo mantido.

Em resumo, os nomes são muito similares e em um "Bag of Words" eles poderiam ser considerado os mesmos, então fica esse alerta para não fazer deploy de *bananas* pensando que são *maças*.