# Agente de publicación de datos de calidad y nivel de agua

Este archivo describe cómo mantener el publicador horario de
[`cmasudd/calidadAgua`](https://github.com/cmasudd/calidadAgua). La guía general
está en [`cmasudd/buenas_practicas`](https://github.com/cmasudd/buenas_practicas),
especialmente en
[`04_AUTOMATIZACION_LOCAL.md`](https://github.com/cmasudd/buenas_practicas/blob/main/docs/GUIA_SITIO_GITHUB_SENSORES/04_AUTOMATIZACION_LOCAL.md),
[`05_OPERACION_Y_RECUPERACION.md`](https://github.com/cmasudd/buenas_practicas/blob/main/docs/GUIA_SITIO_GITHUB_SENSORES/05_OPERACION_Y_RECUPERACION.md)
y el [registro de esta plataforma](https://github.com/cmasudd/buenas_practicas/blob/main/cambios/2026-09-09-calidad-agua-plataforma.md).

## Estado verificado el 25 de septiembre de 2026

- [x] ~~Incorporar AGUA-01, AGUA-02, AGUA-03, URA-01 y LVAG-02 a LVAG-05
  al contrato de publicación.~~
- [x] ~~Ejecutar y publicar el backfill histórico inicial de las cuatro
  estaciones LVAG.~~
- [x] ~~Validar el exportador y el contrato publicado: tres pruebas aprobadas.~~
- [x] ~~Aplicar la versión nueva al clon exclusivo y comprobar una ejecución
  con el resultado `Exportación lista: 8 estaciones`.~~
- [x] ~~Comprobar que existe una sola tarea horaria, protegida con `flock`, y
  que el servicio `cron` está activo.~~
- [x] ~~Verificar el despliegue de GitHub Pages, las ocho estaciones en el
  manifiesto público y la igualdad de un CSV LVAG público con su copia local.~~
- [x] ~~Respaldar en Git la entrada segura de cron, sin credenciales, en
  `config/calidadAgua.cron`.~~

La revisión del log, la antigüedad de las mediciones, el tamaño de los CSV y el
estado de GitHub Pages sigue siendo una tarea operativa periódica; no se
considera cerrada de forma permanente por esta verificación.

## Circuito instalado

1. MariaDB almacena las mediciones. `config/stations.json` define los
   dispositivos publicados y `scripts/export_monthly_csv.py` traduce sus
   sensores a CSV mensuales, `data/latest.csv` y `data/manifest.json`.
2. El clon exclusivo `/home/cmas/Documentos/calidadAgua-publisher` ejecuta
   `scripts/update_data.sh`. El script sincroniza `main` con `git pull
   --ff-only`, exporta el mes vigente, crea un commit solo si cambió `data/`
   y lo envía a `cmasudd/calidadAgua`.
3. Cron lo invoca al minuto 27 de cada hora con el lock
   `/tmp/calidadAgua-update.lock`. El log local `data-update.log` está ignorado
   por Git. Una copia segura de la entrada instalada se conserva en
   `config/calidadAgua.cron`. GitHub Pages sirve los CSV y la web desde `main`.
4. El navegador consulta la API para una lectura reciente por estación cada
   diez minutos. El histórico y las descargas provienen de los CSV publicados.

`readmeagent.md` documenta el procedimiento; no cambia por sí solo un proceso
en ejecución. La siguiente ejecución horaria sincroniza el código nuevo. Para
aplicarlo antes, ejecutar una vez el wrapper bajo el mismo lock y verificar el
resultado.

## Contrato de estaciones

| Código | Lugar | Proyecto | Dispositivo | Tipo |
| --- | --- | ---: | ---: | --- |
| AGUA-01 | Carén | 13 | 94 | Calidad |
| AGUA-02 | Trapiche | 13 | 113 | Calidad |
| AGUA-03 | Mantagua | 13 | 216 | Calidad |
| URA-01 | Mantagua | 22 | 256 | Calidad |
| LVAG-02 | Batuco | 14 | 86 | Nivel |
| LVAG-03 | Carén | 14 | 87 | Nivel |
| LVAG-04 | Trapiche | 14 | 88 | Nivel |
| LVAG-05 | Acúleo | 14 | 89 | Nivel |

Para LVAG, el exportador publica distancia al agua (A01NYUB, variable 22),
profundidad (LIQ-136, variable 23), temperatura y humedad del aire (SHT40,
variables 3 y 6), temperatura del sistema, voltaje y señal. `app.js` contiene
los nombres de campos de la API en vivo. Los marcadores y fotografías se
agrupan por lugar. No inferir una cota de nivel común a partir de distancia y
profundidad sin definir antes el punto de referencia de cada sensor.

## Cambiar el contrato o agregar estaciones

1. Comprobar en MariaDB el ID del dispositivo, modelos, IDs de variables,
   unidades, fechas y valores inválidos. No basarse solo en una planilla.
2. Editar `config/stations.json`, `MODELS`, `PUBLIC_VARS`, `HEADER` y `clean()`
   en `scripts/export_monthly_csv.py`; agregar la variable y el campo en vivo
   en `app.js`. Revisar nombre, lugar, coordenadas e imagen.
3. Probar el exportador y sus contratos con el mismo Python del servidor:

   ```bash
   /var/www/api_sensores/venv/bin/python -m unittest discover -s tests -v
   ```

4. Hacer un backfill inicial supervisado con `--all`, usando el mismo lock del
   daemon. Revisar muestras, tamaños, fechas, manifiesto y CSV antes de
   publicar. La tarea horaria solo reconstruye el mes vigente: no reemplaza
   el backfill de una estación nueva.
5. Publicar el cambio en `main`, esperar el build de Pages y verificar los
   gráficos y descargas de cada estación desde la URL pública.

## Aplicar una versión nueva al publicador

Primero verificar que el clon automático está limpio y que solo existe la
agenda prevista:

```bash
git -C /home/cmas/Documentos/calidadAgua-publisher status -sb
crontab -l | rg 'calidadAgua-update.lock'
```

Si el clon está limpio y el trabajo horario no está en curso, ejecutar el mismo
comando que cron. `flock -n` evita dos exportaciones simultáneas:

```bash
/usr/bin/flock -n /tmp/calidadAgua-update.lock \
  /home/cmas/Documentos/calidadAgua-publisher/scripts/update_data.sh
```

Comprobar el resultado sin asumir que debe existir un commit nuevo: si no
entraron mediciones, una ejecución correcta puede no modificar `data/`.

```bash
git -C /home/cmas/Documentos/calidadAgua-publisher status -sb
git -C /home/cmas/Documentos/calidadAgua-publisher log -1 --oneline
tail -30 /home/cmas/Documentos/calidadAgua-publisher/data-update.log
```

Verificar además que `data/manifest.json` público lista las ocho estaciones,
que un CSV LVAG público coincide con el local y que GitHub Pages terminó el
build del commit esperado. Una estación sin lecturas recientes no implica por
sí sola que el daemon falló: distinguir fecha de ejecución exitosa y fecha de
última medición.

## Respaldo y restauración del cron

`config/calidadAgua.cron` contiene solamente el fragmento de esta plataforma,
sin credenciales. Para restaurarlo, revisar primero `crontab -l` y agregar la
entrada al crontab existente. No ejecutar `crontab config/calidadAgua.cron`,
porque eso reemplazaría todas las demás tareas del usuario. Después comprobar
que exista una sola entrada para `calidadAgua-update.lock` y que el servicio
`cron` esté activo.

## Fallos y límites

- Si el clon tiene cambios ajenos a `data/`, detener la actualización y
  diagnosticar su origen; no forzar un `git reset` en el clon productivo.
- Si MariaDB, la validación o GitHub fallan, conservar la última publicación
  válida y revisar el log antes de repetir. No ejecutar dos agendas a la vez.
- No guardar claves, tokens ni valores de `/var/www/api_sensores/.env` en Git,
  cron, documentación o logs. El clon del daemon debe tener acceso de escritura
  solo al repositorio que publica.
- Antes de cambiar cron, credenciales o el wrapper, guardar un respaldo fuera
  de Git y dejar una ruta de reversión. Seguir la guía operativa de
  `buenas_practicas` para la comprobación de extremo a extremo.
