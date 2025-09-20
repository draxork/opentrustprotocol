OpenTrust Protocol (OTP) SDK
El Estándar Abierto para la Confianza Auditable.
Este es el SDK oficial de Python para el OpenTrust Protocol (OTP). Permite a los desarrolladores crear, manipular y fusionar Juicios Neutrosóficos para construir sistemas más transparentes, robustos y auditables.
OTP convierte la incertidumbre de una "caja negra" a una métrica medible (T, I, F) con un rastro de auditoría completo (provenance_chain).

Sitio Web Oficial y Documentación Completa: https://opentrustprotocol.com

Fundamento Científico: https://neutrosofia.com

Instalación
pip install opentrustprotocol


Inicio Rápido
Comienza a usar OTP en solo unas pocas líneas de código.
from otp import NeutrosophicJudgment, fuse

# 1. Crea Juicios Neutrosóficos a partir de tu evidencia
# Fuente 1: La confianza de un modelo de IA
judgment_from_model = NeutrosophicJudgment(
    T=0.85, 
    I=0.15, 
    F=0.0,
    provenance_chain=[{
        "source_id": "model-text-bison-v1.2",
        "timestamp": "2025-09-20T20:30:00Z"
    }]
)

# Fuente 2: El veredicto de un experto humano
judgment_from_expert = NeutrosophicJudgment(
    T=0.7, 
    I=0.1, 
    F=0.2,
    provenance_chain=[{
        "source_id": "expert-auditor-jane-doe",
        "timestamp": "2025-09-20T20:32:15Z"
    }]
)

# 2. Fusiona la evidencia para obtener una conclusión auditable
# Usamos el operador estándar, que es consciente del conflicto.
# Le damos más peso al experto humano (60%) que al modelo (40%).
fused_judgment = fuse.conflict_aware_weighted_average(
    judgments=[judgment_from_model, judgment_from_expert],
    weights=[0.4, 0.6]
)

# 3. Analiza el resultado y su rastro de auditoría
print(f"Juicio Fusionado: {fused_judgment}")
# Juicio Fusionado: NeutrosophicJudgment(T=0.76, I=0.12, F=0.12, ...)

# La provenance_chain ahora contiene la historia completa
print("\nRastro de Auditoría Completo:")
for entry in fused_judgment.provenance_chain:
    print(f"- {entry}")

# - {'source_id': 'model-text-bison-v1.2', ...}
# - {'source_id': 'expert-auditor-jane-doe', ...}
# - {'operator_id': 'otp-cawa-v1.1', ...}


¿Qué sigue?
Visita la Guía Técnica para aprender sobre todos los operadores de fusión disponibles.
Explora la Guía Práctica para ver ejemplos avanzados de mapeo de datos.
Contribuye al proyecto en GitHub.
