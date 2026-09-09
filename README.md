# Monitoreo de Calidad de Agua C+

Sitio público del Centro C+ de la Universidad del Desarrollo para consultar,
visualizar y descargar mediciones de calidad de agua.

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

- Cuatro estaciones: AGUA-01, AGUA-02, AGUA-03 y URA-01.
- Histórico público en CSV mensuales desde 2025.
- `data/manifest.json` describe estaciones, variables y archivos disponibles.
- `data/latest.csv` conserva la última lectura publicada por estación.
- El navegador revisa la API en vivo cada diez minutos.
- El publicador local reconstruye el mes vigente y publica cambios una vez por
  hora.

Los gráficos de pH y conductividad muestran una referencia orientativa de la
NCh 1333 para agua de riego. No representan una certificación sanitaria ni una
evaluación oficial de cumplimiento ambiental.

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
