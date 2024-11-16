# TABLA-PRESTAMOS

En base al diseño del sistema, estas serían las funciones **Lambda** que manejarían las relaciones entre las tablas y su propósito. También se detalla cuántas funciones son necesarias y cómo se vinculan entre las tablas:

---

### **1. Tabla `solicitud-prestamo`**

Esta tabla está encargada de gestionar las solicitudes de préstamos de los usuarios.

#### **Funciones Lambda relacionadas:**
1. **Crear Solicitud**:
   - **Relación:** 
     - Crea un registro en `solicitud-prestamo` con estado `pendiente`.
     - Sin relación directa con otras tablas.
   - **Propósito:** Permitir que los usuarios creen solicitudes de préstamo.

2. **Listar Solicitudes**:
   - **Relación:** Lista todas las solicitudes (por usuario o todas en general).
   - **Propósito:** Administrar solicitudes para revisarlas o filtrar por estado.

3. **Revisar Solicitud (Aceptar/Rechazar)**:
   - **Relación:**
     - Si **aceptada**, genera un registro en la tabla `prestamo` (ver detalles en la sección de préstamos).
     - Si **rechazada**, actualiza el estado en la tabla `solicitud-prestamo` a `rechazado`.
   - **Propósito:** Determina el flujo de una solicitud (rechazar o aprobar).

#### **Total de funciones Lambda para `solicitud-prestamo`:**
- **3 funciones Lambda.**

---

### **2. Tabla `prestamo`**

Esta tabla gestiona los préstamos aprobados.

#### **Funciones Lambda relacionadas:**
4. **Crear Préstamo** (automático al aceptar una solicitud):
   - **Relación:**
     - Crea un registro en la tabla `prestamo` a partir de una solicitud aceptada.
     - Actualiza el saldo en la tabla `cuenta`.
     - Registra un ingreso en la tabla `movimientos`.
     - Genera una deuda en la tabla `pagos`.
   - **Propósito:** Manejar el proceso de creación del préstamo una vez aceptada la solicitud.

5. **Listar Préstamos**:
   - **Relación:** Muestra todos los préstamos relacionados a un usuario o todos los préstamos existentes.
   - **Propósito:** Administrar o visualizar los préstamos activos.

6. **Ver Deuda del Préstamo**:
   - **Relación:**
     - Consulta la deuda actual (en la tabla `pagos`) para un préstamo específico.
     - Calcula intereses basados en el tiempo transcurrido desde la fecha de vencimiento.
   - **Propósito:** Permitir que los usuarios vean el estado de su deuda.

7. **Actualizar Estado del Préstamo**:
   - **Relación:**
     - Cambia el estado del préstamo en `prestamo` a `pagado` cuando la deuda asociada (en `pagos`) se liquida.
   - **Propósito:** Mantener la coherencia entre el estado del préstamo y los pagos realizados.

#### **Total de funciones Lambda para `prestamo`:**
- **4 funciones Lambda.**

---

### **3. Relación con la Tabla `cuenta`**

#### **Funciones Lambda relacionadas:**
8. **Actualizar Saldo de Cuenta (al aprobar un préstamo):**
   - **Relación:**
     - Cuando un préstamo es aprobado, el monto es sumado al saldo de la cuenta asociada en `cuenta`.
   - **Propósito:** Reflejar el impacto del préstamo aprobado en la cuenta del usuario.

---

### **4. Relación con la Tabla `movimientos`**

#### **Funciones Lambda relacionadas:**
9. **Registrar Movimiento al Aprobar Préstamo:**
   - **Relación:**
     - Registra un movimiento en `movimientos` con tipo `ingreso` y descripción "Préstamo aprobado".
   - **Propósito:** Mantener un historial financiero del ingreso generado por el préstamo.

10. **Registrar Movimiento al Pagar Deuda:**
    - **Relación:**
      - Registra un movimiento en `movimientos` con tipo `egreso` y descripción "Pago del préstamo".
    - **Propósito:** Rastrear los egresos relacionados con los pagos de préstamos.

---

### **5. Relación con la Tabla `pagos`**

#### **Funciones Lambda relacionadas:**
11. **Crear Deuda al Aprobar Préstamo**:
    - **Relación:**
      - Al aprobar un préstamo, se genera una deuda en la tabla `pagos` con los detalles del monto, intereses y fecha límite.
    - **Propósito:** Manejar las deudas asociadas a los préstamos aprobados.

12. **Realizar Pago**:
    - **Relación:**
      - Cambia el estado en `pagos` a `pagado` cuando el usuario realiza el pago.
      - Calcula intereses adicionales si el pago es tardío.
      - Actualiza el estado del préstamo en `prestamo` a `pagado` si la deuda queda saldada.
    - **Propósito:** Gestionar los pagos asociados a los préstamos.

---

### **Resumen de las Funciones Lambda y Relaciones**

| **Función Lambda**                  | **Tabla Principal**       | **Relación con otras tablas**                              |
|-------------------------------------|---------------------------|-----------------------------------------------------------|
| Crear Solicitud                     | `solicitud-prestamo`      | Sin relación directa.                                     |
| Listar Solicitudes                  | `solicitud-prestamo`      | Sin relación directa.                                     |
| Revisar Solicitud                   | `solicitud-prestamo`      | Relacionada con `prestamo` (si aceptada).                 |
| Crear Préstamo                      | `prestamo`                | Relacionada con `solicitud-prestamo`, `cuenta`, `pagos`, `movimientos`. |
| Listar Préstamos                    | `prestamo`                | Sin relación directa.                                     |
| Ver Deuda del Préstamo              | `prestamo`                | Relacionada con `pagos`.                                  |
| Actualizar Estado del Préstamo      | `prestamo`                | Relacionada con `pagos`.                                  |
| Actualizar Saldo de Cuenta          | `cuenta`                  | Relacionada con `prestamo`.                               |
| Registrar Movimiento al Aprobar     | `movimientos`             | Relacionada con `prestamo`.                               |
| Registrar Movimiento al Pagar       | `movimientos`             | Relacionada con `pagos`.                                  |
| Crear Deuda al Aprobar Préstamo     | `pagos`                   | Relacionada con `prestamo`.                               |
| Realizar Pago                       | `pagos`                   | Relacionada con `prestamo`, `movimientos`, `cuenta`.      |

---

### **Total de funciones Lambda necesarias:**
- **12 funciones Lambda.**

Cada función Lambda gestiona un aspecto clave del sistema, asegurando que las relaciones entre las tablas se manejen correctamente y que el flujo de datos sea consistente.
