# Perfil de datos publicado

Perfil ejecutado el 9 de septiembre de 2026 sobre los dispositivos 94, 113,
216 y 256. Las credenciales y números de serie no forman parte del resultado.

| Código | Cobertura comprobada | Frecuencia reciente aproximada | Observaciones |
|---|---|---|---|
| AGUA-01 | octubre 2025–septiembre 2026 | 61 minutos | pH 0/14, EC 0 y temperatura -999 identificados como centinelas |
| AGUA-02 | septiembre 2025–septiembre 2026 | 61 minutos | mismos centinelas de la plataforma ENV-20 |
| AGUA-03 | febrero–septiembre 2026, con interrupciones | 180 minutos | incluye oxígeno disuelto; sensor en validación |
| URA-01 | septiembre 2026 | 60 minutos | pH constante en 6,9 durante el período perfilado; validar variabilidad |

## Decisión por variable

| Variable | Decisión | Limpieza y presentación |
|---|---|---|
| pH | Publicar | Excluir 0 y 14; referencia NCh 1333 para riego |
| Conductividad | Publicar | Excluir 0; referencia NCh 1333 para riego |
| Temperatura del agua | Publicar | Excluir -999 y valores no plausibles por modelo |
| Oxígeno disuelto | Publicar con advertencia | AGUA-03 solamente; sensor en validación |
| Temperatura del sistema | Publicar como diagnóstico | No mezclar con temperatura del agua |
| Voltaje | Publicar como diagnóstico | Valores fuera del rango técnico se reservan |
| Señal celular | Publicar como diagnóstico | Escala CSQ 0–31 |

La publicación comienza el 1 de enero de 2025 para excluir registros antiguos
con fechas evidentemente incorrectas. Los meses sin observaciones válidas no se
incluyen en el manifiesto.
