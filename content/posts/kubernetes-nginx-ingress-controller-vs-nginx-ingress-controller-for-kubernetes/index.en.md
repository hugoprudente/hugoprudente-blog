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

Quite often I'm seeing people having trouble using the **Kubernetes Ingress Controller** featuring **Nginx**.

The principal issue reported by the community is the annotation `nginx.ingress.kubernetes.io/rewrite-target: /` not working.

The cause of the not working *tag* is the the `ingres-controller` being used. Let me clarify!

Commonly we go to `google.com` and search for the key works "kuberentes ingress controller", this will return two **oficial** projects, by different companies.

* [NGINX Ingress Controller for Kubernetes](https://docs.nginx.com/nginx-ingress-controller/) by NGINX
* [Kubernetes Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/) by Kubernetes (Google)

During the troubleshoot the first thing that we must define is which `ingress-controller` for **Nginx** is being used: 

With **helm** we can check from the repository that it was installed from:

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

Alternatively if the solution was not deployed using **Helm** you can define the origin of the `ingres-controller` project by check the container image using the following command:

```bash
○ → kubectl describe deployment  | grep Image
    Image:       quay.io/kubernetes-ingress-controller/nginx-ingress-controller:0.27.1
    Image:       nginx/nginx-ingress:1.6.1
```

From the [NGINX Ingress Controller for Kubernetes](https://github.com/nginxinc/kubernetes-ingress/), GitHub page we can confirm the ownership of the image **nginx-ingress:1.6.1**.

From the [Kubernetes Nginx Ingress Controller](https://github.com/kubernetes/ingress-nginx/), GitHub page we can also confirm that the ownership of image **nginx-ingress-controller:0.27.1**.


Now that we defined the used project we can move forward with it's configuration:


# NGINX Ingress Controller for Kubernetes

Maintained by NGINX the documentation can be found here on [Nginx Ingress Controller for Kubernetes](https://docs.nginx.com/nginx-ingress-controller/):

The tags for the this projects are `nginx.org` and `nginx.com` for the paid extra features.

Examples exploring the features of this project can be found here on the [GitHub](https://github.com/nginxinc/kubernetes-ingress/tree/v1.6.1/examples)

Example for rewrite feature:

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

Maintained by the Kubernetes community, the documentation can be found her on [Kubernetes Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/):

The tags for this project is `nginx.ingress.kubernetes.io/` and has no extra features.

Examples exploring the features of this project can be found here on the [GitHub](https://github.com/kubernetes/ingress-nginx/tree/master/docs/examples)

Example for rewrite feature:

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

The projects are a couple months difference from each other and there's no clear explanation on why the Kuberenetes Ingress Controller had chosen that exactly name as the NGINX one were already being maintained. 

On summary the names are quite similar and on a Bag of Words they could be even considered the same, so we need to be alert to not deploy *bananas* thinking that they are *apples*