# OTP Mapper - Guía Completa

## 🎯 **Visión General**

El **OTP Mapper** es el componente fundamental del ecosistema OpenTrust Protocol que transforma **datos crudos** en **Juicios Neutrosóficos** (T, I, F) de manera estandarizada, auditable y matemáticamente correcta.

### **¿Qué es el Mapper?**

El Mapper implementa la **"Geometría del Juicio"** - un método universal que transforma cualquier número en un juicio rico y contextual, basado únicamente en la definición de tres puntos de referencia:

- **Punto de Falsedad** (F=1.0)
- **Punto de Indeterminación** (I=1.0)  
- **Punto de Verdad** (T=1.0)

## 🏗️ **Arquitectura del Sistema**

### **Componentes Principales**

```
otp.mapper/
├── __init__.py          # Módulo principal
├── types.py             # Tipos de datos y validación
├── numerical.py         # Mapper numérico
├── categorical.py       # Mapper categórico
├── boolean.py           # Mapper booleano
├── registry.py          # Registro centralizado
└── validation.py        # Validación JSON Schema
```

### **Tipos de Mappers**

1. **NumericalMapper**: Transforma valores numéricos continuos
2. **CategoricalMapper**: Transforma categorías/cadenas
3. **BooleanMapper**: Transforma valores booleanos

## 📊 **Mapper Numérico - El Corazón del Sistema**

### **Concepto: Interpolación por Zonas de Transición**

El mapper numérico crea dos zonas de transición:

```
Falsity Point ←→ Indeterminacy Point ←→ Truth Point
     (F=1.0)           (I=1.0)           (T=1.0)
```

### **Ejemplo Práctico: DeFi Health Factor**

```python
from otp.mapper import NumericalMapper

# Crear mapper para Health Factor
health_mapper = NumericalMapper(
    id="defi-health-factor",
    falsity_point=1.0,    # Liquidación inminente
    indeterminacy_point=1.5,  # Zona de riesgo
    truth_point=3.0       # Posición segura
)

# Transformar valores
judgment_1 = health_mapper.apply(1.25)  # 50% falsedad, 50% incertidumbre
judgment_2 = health_mapper.apply(2.25)  # 50% incertidumbre, 50% verdad

print(f"HF 1.25: T={judgment_1.T:.2f}, I={judgment_1.I:.2f}, F={judgment_1.F:.2f}")
print(f"HF 2.25: T={judgment_2.T:.2f}, I={judgment_2.I:.2f}, F={judgment_2.F:.2f}")
```

### **Algoritmo de Interpolación**

```python
def apply_numerical(input_value, params):
    p_f = params.falsity_point
    p_i = params.indeterminacy_point  
    p_t = params.truth_point
    
    if p_f <= input_value <= p_i:
        # Zona Falsedad → Indeterminación
        ratio = (input_value - p_f) / (p_i - p_f)
        I = ratio
        F = 1.0 - ratio
        T = 0.0
    elif p_i <= input_value <= p_t:
        # Zona Indeterminación → Verdad
        ratio = (input_value - p_i) / (p_t - p_i)
        T = ratio
        I = 1.0 - ratio
        F = 0.0
    
    return (T, I, F)
```

## 🏷️ **Mapper Categórico**

### **Uso para Mapeo Directo**

```python
from otp.mapper import CategoricalMapper

# Crear mapper para estados KYC
kyc_mapper = CategoricalMapper(
    id="kyc-status",
    mappings={
        "VERIFIED": (1.0, 0.0, 0.0),    # Confianza total
        "PENDING": (0.0, 1.0, 0.0),    # Incertidumbre total
        "REJECTED": (0.0, 0.0, 1.0),   # Falsedad total
        "PARTIAL": (0.6, 0.3, 0.1)     # Juicio mixto
    },
    default_judgment=(0.0, 0.0, 1.0)   # Desconocido = falsedad
)

# Usar el mapper
judgment = kyc_mapper.apply("VERIFIED")
print(f"KYC VERIFIED: T={judgment.T:.2f}, I={judgment.I:.2f}, F={judgment.F:.2f}")
```

## ✅ **Mapper Booleano**

### **Uso para Decisiones Binarias**

```python
from otp.mapper import BooleanMapper

# Crear mapper para certificado SSL
ssl_mapper = BooleanMapper(
    id="ssl-certificate",
    true_map=(0.9, 0.1, 0.0),   # Certificado válido = alta confianza
    false_map=(0.0, 0.0, 1.0)  # Certificado inválido = falsedad total
)

# Usar el mapper
judgment_valid = ssl_mapper.apply(True)
judgment_invalid = ssl_mapper.apply(False)

print(f"SSL Valid: T={judgment_valid.T:.2f}")
print(f"SSL Invalid: F={judgment_invalid.F:.2f}")
```

## 📋 **Registro de Mappers**

### **Gestión Centralizada**

```python
from otp.mapper import MapperRegistry

# Obtener registro global
registry = MapperRegistry()

# Crear y registrar mappers
health_mapper = registry.create_numerical_mapper(
    mapper_id="defi-health-factor",
    falsity_point=1.0,
    indeterminacy_point=1.5,
    truth_point=3.0
)

kyc_mapper = registry.create_categorical_mapper(
    mapper_id="kyc-status",
    mappings={
        "VERIFIED": (1.0, 0.0, 0.0),
        "PENDING": (0.0, 1.0, 0.0),
        "REJECTED": (0.0, 0.0, 1.0)
    }
)

# Usar mappers registrados
judgment = registry.get("defi-health-factor").apply(1.8)
print(f"Health Factor 1.8: T={judgment.T:.3f}")

# Listar todos los mappers
print(f"Mappers registrados: {registry.list_mappers()}")
```

## 🔍 **Validación y Conformidad**

### **Validación JSON Schema**

```python
from otp.mapper import MapperValidator

# Validar mapper
mapper = NumericalMapper(id="test", falsity_point=1.0, indeterminacy_point=2.0, truth_point=3.0)
errors = MapperValidator.validate_mapper(mapper)

if errors:
    print(f"Errores de validación: {errors}")
else:
    print("✅ Mapper válido")

# Validar JSON
json_str = mapper.to_json()
is_valid = MapperValidator.is_json_valid(json_str)
print(f"JSON válido: {is_valid}")
```

### **Esquema JSON del Mapper**

```json
{
  "version": "2.0",
  "id": "defi-health-factor",
  "type": "numerical",
  "parameters": {
    "falsity_point": 1.0,
    "indeterminacy_point": 1.5,
    "truth_point": 3.0,
    "clamp_to_range": true
  },
  "metadata": {
    "domain": "defi",
    "description": "Health factor mapper for DeFi protocols"
  }
}
```

## 🔗 **Fusión con Mappers**

### **Combinar Múltiples Fuentes**

```python
from otp import conflict_aware_weighted_average

# Crear múltiples mappers
health_mapper = NumericalMapper(id="health", falsity_point=1.0, indeterminacy_point=1.5, truth_point=3.0)
credit_mapper = NumericalMapper(id="credit", falsity_point=300, indeterminacy_point=650, truth_point=850)
kyc_mapper = CategoricalMapper(id="kyc", mappings={"VERIFIED": (1.0, 0.0, 0.0)})

# Generar juicios
health_judgment = health_mapper.apply(1.8)
credit_judgment = credit_mapper.apply(720)
kyc_judgment = kyc_mapper.apply("VERIFIED")

# Fusionar con pesos
weights = [0.3, 0.5, 0.2]  # health, credit, kyc
fused_judgment = conflict_aware_weighted_average(
    [health_judgment, credit_judgment, kyc_judgment],
    weights
)

print(f"Juicio fusionado: T={fused_judgment.T:.3f}, I={fused_judgment.I:.3f}, F={fused_judgment.F:.3f}")
```

## 🎯 **Casos de Uso Reales**

### **1. DeFi - Evaluación de Riesgo**

```python
# Health Factor
health_mapper = NumericalMapper(
    id="health-factor",
    falsity_point=1.0,    # Liquidación
    indeterminacy_point=1.5,  # Riesgo
    truth_point=3.0       # Seguro
)

# Loan-to-Value Ratio
ltv_mapper = NumericalMapper(
    id="ltv-ratio",
    falsity_point=0.9,    # Alto riesgo
    indeterminacy_point=0.7,  # Riesgo moderado
    truth_point=0.5       # Bajo riesgo
)
```

### **2. KYC/AML - Verificación de Identidad**

```python
kyc_mapper = CategoricalMapper(
    id="kyc-verification",
    mappings={
        "VERIFIED": (1.0, 0.0, 0.0),
        "PENDING": (0.0, 1.0, 0.0),
        "REJECTED": (0.0, 0.0, 1.0),
        "EXPIRED": (0.2, 0.6, 0.2)
    }
)
```

### **3. IoT - Monitoreo de Sensores**

```python
# Temperatura del servidor
temp_mapper = NumericalMapper(
    id="server-temp",
    falsity_point=35.0,   # Demasiado caliente
    indeterminacy_point=22.0,  # Rango óptimo
    truth_point=18.0      # Demasiado frío
)

# Presión del sistema
pressure_mapper = NumericalMapper(
    id="system-pressure",
    falsity_point=100.0,  # Presión peligrosa
    indeterminacy_point=50.0,  # Presión normal
    truth_point=25.0      # Presión óptima
)
```

### **4. Supply Chain - Estado del Producto**

```python
status_mapper = CategoricalMapper(
    id="product-status",
    mappings={
        "DELIVERED": (1.0, 0.0, 0.0),
        "IN_TRANSIT": (0.7, 0.3, 0.0),
        "DELAYED": (0.3, 0.5, 0.2),
        "LOST": (0.0, 0.0, 1.0)
    }
)
```

## 🔧 **API Completa**

### **NumericalMapper**

```python
# Crear mapper
mapper = NumericalMapper(
    id="unique-id",
    falsity_point=1.0,
    indeterminacy_point=2.0,
    truth_point=3.0,
    clamp_to_range=True,
    metadata={"domain": "example"}
)

# Aplicar transformación
judgment = mapper.apply(1.5)

# Métodos utilitarios
valid_range = mapper.get_valid_range()
is_valid = mapper.is_in_valid_range(1.5)
points = mapper.get_reference_points()

# Serialización
json_str = mapper.to_json()
restored = Mapper.from_json(json_str)
```

### **CategoricalMapper**

```python
# Crear mapper
mapper = CategoricalMapper(
    id="categories",
    mappings={"GOOD": (1.0, 0.0, 0.0), "BAD": (0.0, 0.0, 1.0)},
    default_judgment=(0.5, 0.5, 0.0)
)

# Aplicar transformación
judgment = mapper.apply("GOOD")

# Métodos utilitarios
categories = mapper.get_categories()
has_category = mapper.has_category("GOOD")
judgment_for_cat = mapper.get_judgment_for_category("GOOD")

# Modificar mapper
new_mapper = mapper.add_category("MEDIUM", (0.5, 0.3, 0.2))
```

### **BooleanMapper**

```python
# Crear mapper
mapper = BooleanMapper(
    id="boolean-check",
    true_map=(0.9, 0.1, 0.0),
    false_map=(0.0, 0.0, 1.0)
)

# Aplicar transformación (acepta bool, int, str)
judgment_true = mapper.apply(True)
judgment_false = mapper.apply("false")
judgment_one = mapper.apply(1)

# Obtener mapeos
true_judgment = mapper.get_true_judgment()
false_judgment = mapper.get_false_judgment()
```

## 🧪 **Testing y Validación**

### **Ejecutar Tests**

```bash
# Tests del mapper numérico
python -m pytest tests/test_mapper_numerical.py -v

# Tests del mapper categórico
python -m pytest tests/test_mapper_categorical.py -v

# Tests del mapper booleano
python -m pytest tests/test_mapper_boolean.py -v

# Todos los tests
python -m pytest tests/ -v
```

### **Ejecutar Ejemplos**

```bash
# Ejemplos completos
python examples/mapper_examples.py

# Ejemplo específico
python -c "
from examples.mapper_examples import defi_health_factor_example
defi_health_factor_example()
"
```

## 🚀 **Mejores Prácticas**

### **1. Diseño de Mappers**

- **Usar IDs descriptivos**: `defi-health-factor`, `kyc-verification`
- **Documentar puntos de referencia**: Explicar por qué se eligieron los valores
- **Incluir metadata**: Dominio, versión, descripción
- **Validar exhaustivamente**: Usar `MapperValidator` antes de producción

### **2. Gestión de Mappers**

- **Usar el registro**: Centralizar mappers en `MapperRegistry`
- **Versionado**: Mantener versiones de mappers para compatibilidad
- **Serialización**: Guardar mappers como JSON para reutilización
- **Testing**: Probar todos los casos edge y valores límite

### **3. Integración con Fusion**

- **Pesos apropiados**: Asignar pesos según importancia de cada fuente
- **Provenance tracking**: Mantener trazabilidad completa
- **Validación de resultados**: Verificar conservación T + I + F = 1.0
- **Interpretación clara**: Definir umbrales para decisiones

## 📈 **Roadmap y Futuro**

### **Próximas Características**

1. **Mappers Temporales**: Para series de tiempo y datos temporales
2. **Mappers Espaciales**: Para datos geográficos y de ubicación
3. **Mappers de Red**: Para análisis de grafos y redes
4. **Mappers de ML**: Integración con modelos de machine learning
5. **Mappers Adaptativos**: Que aprenden y se ajustan automáticamente

### **Integración con Otros SDKs**

- **JavaScript**: Implementación completa en TypeScript
- **Rust**: Versión de alto rendimiento
- **Go**: Para sistemas de microservicios
- **Java**: Para aplicaciones empresariales

## 🤝 **Contribución**

### **Cómo Contribuir**

1. **Fork** el repositorio
2. **Crear** una rama para tu feature
3. **Implementar** con tests exhaustivos
4. **Validar** con `MapperValidator`
5. **Documentar** con ejemplos
6. **Submit** pull request

### **Estándares de Código**

- **Type hints** completos
- **Docstrings** detallados
- **Tests** con >90% cobertura
- **Validación** JSON Schema
- **Ejemplos** prácticos

---

## 🎉 **Conclusión**

El **OTP Mapper** representa un avance fundamental en la transformación de datos del mundo real en juicios de confianza estructurados. Su implementación de la "Geometría del Juicio" proporciona una base matemáticamente sólida y auditivamente completa para sistemas de toma de decisiones sofisticados.

**¡Comienza a transformar tus datos en juicios de confianza hoy mismo!** 🚀


