# Monitoreo de calidad y nivel de agua C+

Sitio público del Centro C+ de la Universidad del Desarrollo para consultar,
visualizar y descargar mediciones de calidad y nivel de agua.

El proyecto se encuentra en preparación. La documentación inicial de
dispositivos, variables, ubicaciones e identidad visual está en
[`documentacion/`](documentacion/).

## Licenciamiento propuesto — en revisión

El esquema descrito en
[`LICENCIAMIENTO_PROPUESTO.md`](LICENCIAMIENTO_PROPUESTO.md) es una **propuesta
en revisión**. Todavía no constituye una política institucional aprobada ni una
concesión definitiva de licencia. Debe ser validado por las unidades jurídica
y de transferencia tecnológica de la Universidad del Desarrollo antes de su
adopción.

Mientras esa revisión no termine, no debe asumirse que los logos, marcas,
código, documentación o datos de este repositorio pueden reutilizarse bajo las
licencias propuestas.

## Datos y funcionamiento

- Ocho estaciones: AGUA-01, AGUA-02, AGUA-03, URA-01 y LVAG-02 a LVAG-05.
- Cinco lugares en el mapa: Batuco, Carén, Trapiche, Acúleo y Mantagua. Las
  estaciones del mismo lugar comparten marcador y fotografía.
- Histórico público en CSV mensuales desde 2025.
- `data/manifest.json` describe estaciones, variables y archivos disponibles.
- `data/latest.csv` conserva la última lectura publicada por estación.
- El navegador revisa la API en vivo cada diez minutos.
- El publicador local reconstruye el mes vigente y publica cambios una vez por
  hora.
- La descarga total entrega un ZIP con un CSV separado y nombrado por estación.

Las variables de nivel incluyen distancia al agua, profundidad, temperatura y
humedad del aire. Los valores son mediciones preliminares de cada sensor; no
representan por sí solos una cota de nivel comparable entre lugares.

Los períodos de 24 horas y 7 días muestran las mediciones individuales. En 30
días y en todo el histórico, la línea corresponde al promedio diario y la banda
representa el mínimo y máximo de cada día.

## Exportación manual

```bash
/var/www/api_sensores/venv/bin/python scripts/export_monthly_csv.py
```

Para reconstruir todo el histórico publicado:

```bash
/var/www/api_sensores/venv/bin/python scripts/export_monthly_csv.py --all
```

Las credenciales se leen por defecto desde `/var/www/api_sensores/.env` y
nunca se incorporan al repositorio.

## Automatización

El servidor ejecuta `scripts/update_data.sh` dentro de un clon exclusivo para
publicación. La tarea debe protegerse con `flock` y programarse una vez por
hora. La interfaz en vivo funciona de manera separada y consulta sólo una
lectura reciente por estación cada diez minutos.
