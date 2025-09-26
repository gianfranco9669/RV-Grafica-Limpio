# Sistema RV Gráfica

Proyecto Django que centraliza la producción, administración y contabilidad de RV Gráfica.

## Características
- Órdenes de producción con seguimiento de estado, materiales y adjuntos.
- Presupuestos convertibles en órdenes con cálculo por m².
- Facturación con IVA automático, percepciones e integración contable.
- Gestión de clientes y proveedores compartida por todos los módulos.
- Finanzas: cobros y pagos en cuenta corriente vinculados a facturas.
- Contabilidad: plan de cuentas, asientos automáticos y reportes.
- Stock de insumos y planilla de gastos conectados al mayor contable.
- Tablero de reportes ejecutivos con indicadores clave.

## Estructura
El código se organiza en aplicaciones Django bajo `rv_grafica/`:

| App | Descripción |
| --- | --- |
| `users` | Usuarios y roles (operarios, administrativos, admin). |
| `production` | Órdenes, ítems, materiales y fotos. |
| `budgets` | Presupuestos y conversión a órdenes. |
| `invoicing` | Facturas, remitos y notas de crédito. |
| `contacts` | Clientes y proveedores centralizados. |
| `finance` | Cobros/pagos en cuenta corriente. |
| `accounting` | Plan de cuentas y asientos automáticos. |
| `inventory` | Stock de materiales y ajustes. |
| `expenses` | Planilla de gastos integrada a contabilidad. |
| `reports` | Panel ejecutivo de indicadores. |

## Puesta en marcha
1. Crear y activar un entorno virtual.
2. Instalar dependencias: `pip install -r requirements.txt`.
3. Configurar variables de entorno (por defecto se usa SQLite en `db.sqlite3`).
4. Ejecutar migraciones: `python manage.py migrate`.
5. Crear un superusuario: `python manage.py createsuperuser`.
6. Levantar el servidor: `python manage.py runserver`.

## Distribución como .exe
Para generar un ejecutable de escritorio puede utilizarse [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --name rv-grafica --onefile manage.py
```

El ejecutable debe configurarse para apuntar a un servidor (por ejemplo Gunicorn + PostgreSQL) accesible por las máquinas de oficina.

## Estilo visual
Las plantillas usan Bootstrap 5 con componentes personalizados (`static/css/app.css`) para asegurar una interfaz moderna.
