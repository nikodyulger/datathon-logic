# Datathon - Log(ic)

## Descripción

Este repositorio contiene nuestra solución al reto de visualización propuesto por la competición [**Datathon Cajamar UniversityHack 2022**](https://www.cajamardatalab.com/datathon-cajamar-universityhack-2022) 

## Objetivo

Nuestro objetivo como equipo ha sido llevar a cabo un proceso de minería de datos sobre los conjuntos de datos que se nos han proporcionado. A esto debemos añadir la creación de un dashboard en forma de aplicación web para la ayuda a la toma de decisiones por parte de la empresa **MiFarma**.

## Estructura del proyecto

El repositorio cuenta con una serie de carpetas, en cada unna contiene los archivs correspondientes a las distintas fases del proyecto. A modo de resumen:

- `Data`. Los datos proporcionados por la organización de la competición.
- `EDA`. Abarca todos los cuadernos Jupyter en los que se ha realizado el análisis exploratorio en profundidad.
- `Clean Data`. Contiene tantos los conjuntos de datos limpios y arreglados, como también los cuadernos Jupyter en los que detalla el proceso para obtenerlos.
- `Dash`. Incluye todos los *scripts* referentes a la aplicación del dashboard
- `Docs`. Contiene la documentación de todo el trabajo que es ecigida como entrega para la competición.

## Puesta en marcha

En caso de clonar el repositorio y querar ejecutar la aplicación y los cuadernos, lo primero que debes hacer es:

```
$ pip install -r requirements.txt
```

En caso de querer ejecutar los cuadernos, debes tener Jupyter instalado en tu ordenador o la extensión de Jupyter para VSCode.

En caso de querer ejecutar la aplicación en un servidor local, debes ejecutar los siguientes comandos:

```
$ cd dash
$ python app.py
```

De esta manera se iniciará el servidor automáticamente y podrás acudir al navegador para ver el **dashboard**

## Demo

La aplicación está disponible en este [enlace](https://datathon-logic-yv66bn7uua-ew.a.run.app)

![Alt Text](./docs/demo.gif)

## Autores

Somos tres estudiantes de máster de la Universidad de Castilla La-Mancha apasionados por la minería de datos y el desarrollo de aplicaciones.

- Antonio Beltrán Navarro
- Kristiyan Stanimirov Petrov
- Nikola Svetlozarov Dyulgerov


