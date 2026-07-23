import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import requests
import time  # 🔑 Añadido para evitar caché
from datetime import datetime

# ==============================================================================
# SECCIÓN 1: CONFIGURACIÓN
# ==============================================================================
API_ID = 35552520
API_HASH = "5eda0ce7ccc5228d007dd3bb00e69572"
BOT_TOKEN = "8937193409:AAEyc628t2h416UFTC7veY7Gnr2Y4vvt4y4"
CODE_BOT = "@ProvenetDoxBot"
MAIN_ACCOUNT = "@gartuoe733"
BOT_USERNAME = "@axel_vipBOT"

# 🔑 CREDENCIALES DE CLOUDFLARE (REEMPLAZA ESTOS VALORES)
CLOUDFLARE_API_TOKEN = "cfut_sruesuhFPrG94b2GTq5AeTylCQu2fYDULE3A28FE24ccebaa"
CLOUDFLARE_ACCOUNT_ID = "1b2513b14e072cb0c924f0bd4a5d091c"
KV_NAMESPACE_ID = "32aac7daa4e04d76ad32974cb65658bc"

# ==============================================================================
# SECCIÓN 2: CLIENTES
# ==============================================================================
user_client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

# ==============================================================================
# SECCIÓN 3: VARIABLES GLOBALES
# ==============================================================================
bot_id = None
main_account_id = None
processing_messages = {}
pending_media = {}
resultados_enviados = {}

# ==============================================================================
# FUNCIÓN PARA VERIFICAR ACCESO EN CLOUDFLARE KV (CORREGIDA)
# ==============================================================================
def verificar_acceso(user_id):
    """Verifica si el usuario tiene acceso en Cloudflare KV"""
    try:
        # 🔑 CORRECCIÓN: Añadido timestamp para evitar caché y forzar lectura fresca
        timestamp = int(time.time())
        url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/storage/kv/namespaces/{KV_NAMESPACE_ID}/values/user:{user_id}?t={timestamp}"
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
            # 🔑 Añadido para evitar caché en el cliente
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        # DEBUG: Ver qué responde Cloudflare
        print(f"🔍 Cloudflare Status: {response.status_code}")
        print(f"🔍 Cloudflare Respuesta: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"🔍 Datos parseados: {data}")
                
                # Buscar 'expiracion' o 'expiration'
                clave_fecha = None
                if 'expiracion' in data:
                    clave_fecha = 'expiracion'
                elif 'expiration' in data:
                    clave_fecha = 'expiration'
                
                if clave_fecha and isinstance(data, dict):
                    fecha_exp_str = data[clave_fecha].replace('Z', '+00:00')
                    fecha_exp = datetime.fromisoformat(fecha_exp_str)
                    ahora = datetime.now(fecha_exp.tzinfo)
                    
                    if fecha_exp > ahora:
                        print(f"✅ Usuario {user_id} tiene acceso válido hasta {fecha_exp}")
                        return True
                    else:
                        print(f"️ Usuario {user_id} acceso expiró el {fecha_exp}")
                        return False
                else:
                    print(f"⚠️ No se encontró 'expiracion' en los datos: {data}")
                    return False
            except Exception as json_error:
                print(f" Error al parsear JSON: {json_error}")
                return False
        else:
            print(f"⚠️ Cloudflare devolvió status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar acceso: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==============================================================================
# SECCIÓN 4: BASE DE DATOS DE COMANDOS POR CATEGORÍA
# ==============================================================================
COMANDOS_CATEGORIAS = {
    
    # ========================================
    # RENIEC
    # ========================================
    'reniec': {
        'titulo': '📄 RENIEC',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': '📍 FOTO Y DATOS DE UNA PERSONA', 'tag': '[NOOB EN ADELANTE]', 'formato': 'dni 44441111', 'estado': 'ACTIVO ✅', 'creditos': 2},
                {'titulo': '📍 BUSQUEDA POR NOMBRES Y APELLIDOS', 'tag': '[NOOB EN ADELANTE]', 'formato': 'nm JUAN CARLOS RAMIREZ ESPINOZA', 'estado': 'ACTIVO ✅', 'creditos': 1}
            ]
        }
    },
    
    # ========================================
    # METADATA
    # ========================================
    'metadata': {
        'titulo': ' METADATA',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': ' METADATA COMPLETA [DNI + PDF]', 'tag': '[NOOB EN ADELANTE]', 'formato': 'metadata 44445555', 'estado': 'ACTIVO ✅', 'creditos': 20},
                {'titulo': '📍 SEEKER MÓDULO 1 PDF [NÚMERO]', 'tag': '[DOXER EN ADELANTE]', 'formato': 'metanum 987654321', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': '📍 SEEKER MÓDULO 2 [DNI]', 'tag': '[VIP EN ADELANTE]', 'formato': 'seekerdni 44445555', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': ' SEEKER MÓDULO 2 [NÚMERO]', 'tag': '[HACKER EN ADELANTE]', 'formato': 'seekernum 987654321', 'estado': 'ACTIVO ✅', 'creditos': 30}
            ]
        }
    },
    
    # ========================================
    # TELEFONIA (5 páginas)
    # ========================================
    'telefonia': {
        'titulo': ' TELEFONIA',
        'total_paginas': 5,
        'paginas': {
            1: [
                {'titulo': '📍 TELÉFONOS POR DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'fonos 44445555', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 TITULAR POR NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'fono 986699757', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 LÍNEAS POR DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'lineas 44445555', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 TITULAR DETALLADO POR NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'titular 951568168', 'estado': 'ACTIVO ✅', 'creditos': 5}
            ],
            2: [
                {'titulo': ' CONSULTA MOVISTAR POR NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'movistar 967245095', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 CONSULTA BITEL POR NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'bitel 910884863', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 CONSULTA CLARO POR NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'claro 923990901', 'estado': 'ACTIVO ✅', 'creditos': 7},
                {'titulo': ' CONSULTA OPERADOR DE NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'valnum 987654321', 'estado': 'ACTIVO ✅', 'creditos': 3}
            ],
            3: [
                {'titulo': ' TELEFONÍA POR NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'cel 987654321', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 TELEFONÍA POR DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'tel 44445555', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': ' LÍNEAS CLARO POR DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'clardni 44445555', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': ' BUSQUEDA TITULAR CLARO, BITEL Y MOVISTAR EN TIEMPO REAL', 'tag': '[VIP EN ADELANTE]', 'formato': 'cel 987654321', 'estado': 'ACTIVO ✅', 'creditos': 7}
            ],
            4: [
                {'titulo': ' BUSQUEDA DE TITULAR POR TELEFONO O DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'telp 987654321', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 TELEFONÍA GENERAL POR DNI O NÚMERO', 'tag': '[VIP EN ADELANTE]', 'formato': 'telx 44445555 o /telx 987654321', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': ' BITEL - EN TIEMPO REAL', 'tag': '[VIP EN ADELANTE]', 'formato': 'bitel 987654321', 'estado': 'ACTIVO ✅', 'creditos': 7},
                {'titulo': ' CLARO - EN TIEMPO REAL', 'tag': '[VIP EN ADELANTE]', 'formato': 'claro 987654321', 'estado': 'ACTIVO ✅', 'creditos': 7}
            ],
            5: [
                {'titulo': '📍 MOVISTAR - EN TIEMPO REAL', 'tag': '[VIP EN ADELANTE]', 'formato': 'movistar 987654321', 'estado': 'ACTIVO ✅', 'creditos': 7}
            ]
        }
    },
    
    # ========================================
    # FACIAL
    # ========================================
    'facial': {
        'titulo': ' FACIAL',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': ' IA | RECONOCIMIENTO FACIAL MASIVO', 'tag': '[NOOB EN ADELANTE]', 'formato': 'facial [foto]', 'estado': 'ACTIVO ✅', 'creditos': 45}
            ]
        }
    },
    
    # ========================================
    # PERSONAS (2 páginas)
    # ========================================
    'personas': {
        'titulo': ' PERSONAS',
        'total_paginas': 2,
        'paginas': {
            1: [
                {'titulo': ' SEEKER COMPLETO POR DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'seekerdni 44445555', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': ' SEEKER COMPLETO PDF', 'tag': '[VIP EN ADELANTE]', 'formato': 'metadni 44445555', 'estado': 'ACTIVO ✅', 'creditos': 25},
                {'titulo': ' SEEKER COMPLETO v2.0', 'tag': '[VIP EN ADELANTE]', 'formato': 'seeker 45454545', 'estado': 'ACTIVO ✅', 'creditos': 15},
                {'titulo': '📍 SEEKER v1.0', 'tag': '[VIP EN ADELANTE]', 'formato': 'seeker 44445555', 'estado': 'ACTIVO ✅', 'creditos': 10}
            ],
            2: [
                {'titulo': ' CORREOS de una persona', 'tag': '[VIP EN ADELANTE]', 'formato': 'co 44445555', 'estado': 'ACTIVO ✅', 'creditos': 5}
            ]
        }
    },
    
    # ========================================
    # VEHICULOS (3 páginas)
    # ========================================
    'vehiculos': {
        'titulo': ' VEHICULOS',
        'total_paginas': 3,
        'paginas': {
            1: [
                {'titulo': '📍 INSCRIPCIÓN VEHICULAR [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'insve ABC123', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': '📍 DATOS DE UN VEHICULO POR PLACA', 'tag': '[VIP EN ADELANTE]', 'formato': 'pla ABC123', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': ' SUNARP | ASIENTOS [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'placapdf ABC123', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': ' TIVE ONLINE SUNARP [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'tiv BFA908', 'estado': 'ACTIVO ✅', 'creditos': 15}
            ],
            2: [
                {'titulo': ' TIVE ORIGINAL SUNARP [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'tive BFA908', 'estado': 'ACTIVO ✅', 'creditos': 15},
                {'titulo': '📍 TIVE GENERADO SUNARP [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'tiveg ABC123', 'estado': 'ACTIVO ✅', 'creditos': 15},
                {'titulo': ' TARJETA DE PROPIEDAD FISICA [GENERADO]', 'tag': '[VIP EN ADELANTE]', 'formato': 'tarjeta ABC-123', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': '📍 DATOS PLACA IMAGEN', 'tag': '[VIP EN ADELANTE]', 'formato': 'pla2 ABC123', 'estado': 'ACTIVO ✅', 'creditos': 2}
            ],
            3: [
                {'titulo': ' REVISIÓN TÉCNICA VEHICULAR [TXT]', 'tag': '[VIP EN ADELANTE]', 'formato': 'citv ABC123', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' SOAT VEHÍCULAR TEXTO', 'tag': '[VIP EN ADELANTE]', 'formato': 'soat ABC123', 'estado': 'ACTIVO ✅', 'creditos': 7},
                {'titulo': ' SOAT VEHÍCULAR PDF', 'tag': '[VIP EN ADELANTE]', 'formato': 'soatpdf ABC123', 'estado': 'ACTIVO ✅', 'creditos': 7},
                {'titulo': '📍 BOLETA INFORMATIVA VEHICULAR [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'boleta ABC123', 'estado': 'ACTIVO ✅', 'creditos': 10}
            ]
        }
    },
    
    # ========================================
    # DELITOS
    # ========================================
    'delitos': {
        'titulo': ' DELITOS',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': ' ANTECEDENTES PERSONALES [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'anteper 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' REQUISITORIA DE PERSONA [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'rqper 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' DENUNCIAS POLICIALES - DOXER', 'tag': '[DOXER EN ADELANTE]', 'formato': 'denuncias 44445555', 'estado': 'ACTIVO ✅', 'creditos': 20},
                {'titulo': '📍 SIDPOL PDF - HACKER', 'tag': '[HACKER EN ADELANTE]', 'formato': 'sidpolpdf 44445555', 'estado': 'ACTIVO ✅', 'creditos': 15}
            ]
        }
    },
    
    # ========================================
    # FINANCIERO
    # ========================================
    'financiero': {
        'titulo': ' FINANCIERO',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': '📍 SBS | CENTRAL DE RIESGOS [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'sentinel 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8}
            ]
        }
    },
    
    # ========================================
    # SUNARP
    # ========================================
    'sunarp': {
        'titulo': '️ SUNARP',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': ' SUNARP TEXTO POR DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'sunarp 44445555', 'estado': 'ACTIVO ✅', 'creditos': 6},
                {'titulo': ' SUNARP PDF POR DNI', 'tag': '[VIP EN ADELANTE]', 'formato': 'sunarpdf 44445555', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': ' BIENES INMUEBLES PDFs', 'tag': '[VIP EN ADELANTE]', 'formato': 'bienespdf 44445555', 'estado': 'ACTIVO ✅', 'creditos': 12}
            ]
        }
    },
    
    # ========================================
    # JUSTICIA (2 páginas)
    # ========================================
    'justicia': {
        'titulo': '️ JUSTICIA',
        'total_paginas': 2,
        'paginas': {
            1: [
                {'titulo': '📍 FISCALÍA TEXTO [DNI] - DOXER', 'tag': '[DOXER EN ADELANTE]', 'formato': 'fiscalia 44445555', 'estado': 'ACTIVO ✅', 'creditos': 12},
                {'titulo': '📍 FISCALÍA PDF [DNI] - HACKER', 'tag': '[HACKER EN ADELANTE]', 'formato': 'fiscaliapdf 44445555', 'estado': 'ACTIVO ✅', 'creditos': 30},
                {'titulo': '📍 FISCALÍA PDF [RUC] - HACKER', 'tag': '[HACKER EN ADELANTE]', 'formato': 'fisruc 20536902385', 'estado': 'ACTIVO ✅', 'creditos': 30},
                {'titulo': ' FISCALÍA TEXTO [RUC] - DOXER', 'tag': '[DOXER EN ADELANTE]', 'formato': 'fisructext 20536902385', 'estado': 'ACTIVO ✅', 'creditos': 12}
            ],
            2: [
                {'titulo': ' FISCALÍA POR NOMBRES [TXT] - HACKER', 'tag': '[HACKER EN ADELANTE]', 'formato': 'fisnm URIEL|BERNAL|JUSCACHI', 'estado': 'ACTIVO ✅', 'creditos': 30},
                {'titulo': '📍 FISCALÍA POR NOMBRES [PDF] - HACKER', 'tag': '[HACKER EN ADELANTE]', 'formato': 'fisnmpdf URIEL|BERNAL|JUSCACHI', 'estado': 'ACTIVO ✅', 'creditos': 30},
                {'titulo': '📍 FISCALÍA CASO TEXTO - DOXER', 'tag': '[DOXER EN ADELANTE]', 'formato': 'fiscaso 01805114504-2023-000045-0000', 'estado': 'ACTIVO ✅', 'creditos': 12},
                {'titulo': ' FISCALÍA CASO PDF - HACKER', 'tag': '[HACKER EN ADELANTE]', 'formato': 'fiscasopdf 01805114504-2023-000045-0000', 'estado': 'ACTIVO ✅', 'creditos': 30}
            ]
        }
    },
    
    # ========================================
    # SUNAT
    # ========================================
    'sunat': {
        'titulo': ' SUNAT',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': ' RUC INFO COMPLETO', 'tag': '[VIP EN ADELANTE]', 'formato': 'ruc 20165465009', 'estado': 'ACTIVO ✅', 'creditos': 5}
            ]
        }
    },
    
    # ========================================
    # FAMILIA
    # ========================================
    'familia': {
        'titulo': '👩‍👧 FAMILIA',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': '📍 ARBOL GENEALOGICO TEXTO', 'tag': '[VIP EN ADELANTE]', 'formato': 'ag 44441111', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' ARBOL GENEALOGICO TEXTO v2', 'tag': '[VIP EN ADELANTE]', 'formato': 'ag2 44441111', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' ARBOL GENEALOGICO VISUAL [PNG]', 'tag': '[SOLO PARA RANGOS CON CRÉDITOS]', 'formato': 'agv 44441111', 'estado': 'ACTIVO ✅', 'creditos': 15},
                {'titulo': ' ÁRBOL FAMILIAR VISUAL MEJORADO', 'tag': '[VIP EN ADELANTE]', 'formato': 'famivi 44441111', 'estado': 'ACTIVO ✅', 'creditos': 12}
            ]
        }
    },
    
    # ========================================
    # MINEDU
    # ========================================
    'minedu': {
        'titulo': ' MINEDU',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': '⭐ NOTAS MINEDU [PDF] - VIP', 'tag': '[HACKER EN ADELANTE]', 'formato': 'minedu 44445555', 'estado': 'ACTIVO ✅', 'creditos': 10}
            ]
        }
    },
    
    # ========================================
    # MTC (2 páginas)
    # ========================================
    'mtc': {
        'titulo': ' MTC',
        'total_paginas': 2,
        'paginas': {
            1: [
                {'titulo': ' LICENCIA DE CONDUCIR', 'tag': '[VIP EN ADELANTE]', 'formato': 'licencia 45454545', 'estado': 'ACTIVO ✅', 'creditos': 6},
                {'titulo': '📍 LICENCIA DE CONDUCIR ELECTRÓNICA [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'licenciapdf 45454545', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': '📍 PAPELETAS POR DNI [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'record 45454545', 'estado': 'ACTIVO ✅', 'creditos': 10},
                {'titulo': ' TARJETA DE PROPIEDAD [IMAGEN]', 'tag': '[VIP EN ADELANTE]', 'formato': 'tarjeta ABS920', 'estado': 'ACTIVO ✅', 'creditos': 8}
            ],
            2: [
                {'titulo': ' REVISIÓN TÉCNICA VEHICULAR [TXT]', 'tag': '[VIP EN ADELANTE]', 'formato': 'citv ABC123', 'estado': 'ACTIVO ✅', 'creditos': 6},
                {'titulo': '📍 REVISIÓN TÉCNICA VEHICULAR [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'citvpdf ABC123', 'estado': 'ACTIVO ✅', 'creditos': 12},
                {'titulo': ' REQUISITORIA VEHICULAR [PDF]', 'tag': '[VIP EN ADELANTE]', 'formato': 'rqpla APM384', 'estado': 'ACTIVO ✅', 'creditos': 8}
            ]
        }
    },
    
    # ========================================
    # DESCANSOS
    # ========================================
    'descansos': {
        'titulo': '💤 DESCANSOS',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': '📍 DESCANSO + RECETA LA LUZ [PDF]', 'tag': '[NOOB EN ADELANTE]', 'formato': 'laluz 44445555|INFECCION GASTROINTESTINAL|3|AMOXICILINA 500MG', 'estado': 'ACTIVO ✅', 'creditos': 60},
                {'titulo': '📍 DESCANSO MÉDICO MINSA [PDF]', 'tag': '[NOOB EN ADELANTE]', 'formato': 'dminsa 60685138|INFECCIÓN ESTOMACAL|HOSPITAL NACIONAL CAYETANO HEREDIA|21-04-2026|2', 'estado': 'ACTIVO ✅', 'creditos': 50},
                {'titulo': ' DESCANSO MÉDICO ESSALUD [PDF]', 'tag': '[NOOB EN ADELANTE]', 'formato': 'dessalud DNI|NOMBRE|CONTINGENCIA|DIAS', 'estado': 'ACTIVO ✅', 'creditos': 50},
                {'titulo': ' DESCANSO + RECETA LA LUZ [PDF COMBINADO]', 'tag': '[NOOB EN ADELANTE]', 'formato': 'laluz DNI|DIAGNOSTICO|DIAS|MEDICAMENTOS', 'estado': 'ACTIVO ✅', 'creditos': 60}
            ]
        }
    },
    
    # ========================================
    # ARGENTINA
    # ========================================
    'argentina': {
        'titulo': '🇦 ARGENTINA',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': ' BUSQUEDA POR DNI ARGENTINA', 'tag': '[NOOB EN ADELANTE]', 'formato': 'dniarg 12345678', 'estado': 'ACTIVO ✅', 'creditos': 2},
                {'titulo': '📍 BUSQUEDA POR TELÉFONO ARGENTINA', 'tag': '[NOOB EN ADELANTE]', 'formato': 'telarg 2284524520', 'estado': 'ACTIVO ✅', 'creditos': 2},
                {'titulo': '📍 BUSQUEDA POR NOMBRE ARGENTINA', 'tag': '[NOOB EN ADELANTE]', 'formato': 'nmarg juan perez', 'estado': 'ACTIVO ✅', 'creditos': 2}
            ]
        }
    },
    
    # ========================================
    # GENERADOR (2 páginas)
    # ========================================
    'generador': {
        'titulo': '️ GENERADOR',
        'total_paginas': 2,
        'paginas': {
            1: [
                {'titulo': ' C4 AZUL [GENERADO]', 'tag': '[VIP EN ADELANTE]', 'formato': 'c4 44441111', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': '📍 C4 BLANCO [GENERADO]', 'tag': '[VIP EN ADELANTE]', 'formato': 'c4b 44441111', 'estado': 'ACTIVO ✅', 'creditos': 5},
                {'titulo': ' CERTIFICADO DE INSCRIPCION [GENERADO]', 'tag': '[VIP EN ADELANTE]', 'formato': 'c4i 44441111', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' DNI VIRTUAL AZUL', 'tag': '[VIP EN ADELANTE]', 'formato': 'dniv 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8}
            ],
            2: [
                {'titulo': '📍 DNI ELECTRÓNICO', 'tag': '[VIP EN ADELANTE]', 'formato': 'dnive 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' CERTIF. ANTECEDENTES PENALES [GENERADO]', 'tag': '[VIP EN ADELANTE]', 'formato': 'antpe 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': ' CERTIF. ANTECEDENTES JUDICIALES [GENERADO]', 'tag': '[VIP EN ADELANTE]', 'formato': 'antju 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8},
                {'titulo': '📍 ANTECEDENTES POLICIALES', 'tag': '[VIP EN ADELANTE]', 'formato': 'antpol 44445555', 'estado': 'ACTIVO ✅', 'creditos': 8}
            ]
        }
    },
    
    # ========================================
    # EXTRAS
    # ========================================
    'extras': {
        'titulo': '🧩 EXTRAS',
        'total_paginas': 1,
        'paginas': {
            1: [
                {'titulo': '📍 GEOCALIZACION - CON IP', 'tag': '[VIP EN ADELANTE]', 'formato': 'ip 192.199.248.75', 'estado': 'ACTIVO ✅', 'creditos': 1},
                {'titulo': '📍 DIPLOMA USC', 'tag': '[VIP EN ADELANTE]', 'formato': 'dpm Juan Perez|Ingeniería de Sistemas', 'estado': 'ACTIVO ✅', 'creditos': 3}
            ]
        }
    }
}

# ==============================================================================
# SECCIÓN 5: FUNCIONES AUXILIARES DEL MENÚ
# ==============================================================================
def generar_mensaje_pagina(categoria, pagina):
    """Genera el mensaje formateado para una página específica"""
    if categoria not in COMANDOS_CATEGORIAS:
        return "❌ Categoría no encontrada"
    
    datos_categoria = COMANDOS_CATEGORIAS[categoria]
    titulo_categoria = datos_categoria['titulo']
    
    if pagina not in datos_categoria['paginas']:
        return f"❌ Página {pagina} no existe en {titulo_categoria}"
    
    comandos = datos_categoria['paginas'][pagina]
    total_paginas = datos_categoria['total_paginas']
    
    mensaje = f"**{titulo_categoria}**\n\n"
    
    for cmd in comandos:
        mensaje += (
            f"{cmd['titulo']}\n"
            f"▶ {cmd['tag']}\n"
            f"- Formato: `/{cmd['formato']}`\n"
            f"- Estado: {cmd['estado']}\n"
            f"- Créditos: {cmd['creditos']}\n\n"
        )
    
    mensaje += f"📄 Página {pagina} de {total_paginas}"
    
    return mensaje

def generar_botones_navegacion(categoria, pagina_actual):
    """Genera los botones de navegación según la página"""
    if categoria not in COMANDOS_CATEGORIAS:
        return []
    
    total_paginas = COMANDOS_CATEGORIAS[categoria]['total_paginas']
    
    if total_paginas == 1:
        return [
            [Button.inline("🔙 Categorías", b'volver_menu')],
            [
                Button.inline("🏠 Inicio", b'volver_menu'),
                Button.inline("❌ Cerrar", b'cerrar_menu')
            ]
        ]
    
    botones_nav = []
    fila_nav = []
    
    if pagina_actual > 1:
        fila_nav.append(Button.inline("️ Anterior", f'nav_{categoria}_anterior_{pagina_actual}'))
    
    if pagina_actual < total_paginas:
        fila_nav.append(Button.inline("Siguiente ️", f'nav_{categoria}_siguiente_{pagina_actual}'))
    
    if fila_nav:
        botones_nav.append(fila_nav)
    
    botones_nav.append([
        Button.inline(" INICIO", b'volver_menu'),
        Button.inline(" CERRAR", b'cerrar_menu')
    ])
    
    return botones_nav

def generar_menu_principal_botones():
    """Genera los botones del menú principal"""
    return [
        [Button.inline("📄 RENIEC", b'categoria_reniec'), Button.inline(" METADATA", b'categoria_metadata')],
        [Button.inline("📞 TELEFONIA", b'categoria_telefonia'), Button.inline(" FACIAL", b'categoria_facial')],
        [Button.inline("🚗 VEHICULOS", b'categoria_vehiculos'), Button.inline(" PERSONAS", b'categoria_personas')],
        [Button.inline(" DELITOS", b'categoria_delitos'), Button.inline("⚖️ JUSTICIA", b'categoria_justicia')],
        [Button.inline("💰 FINANCIERO", b'categoria_financiero'), Button.inline("📑 SUNAT", b'categoria_sunat')],
        [Button.inline("️ SUNARP", b'categoria_sunarp'), Button.inline("👨‍ FAMILIA", b'categoria_familia')],
        [Button.inline("🎓 MINEDU", b'categoria_minedu'), Button.inline(" DESCANSOS", b'categoria_descansos')],
        [Button.inline(" MTC", b'categoria_mtc'), Button.inline("🇷 ARGENTINA", b'categoria_argentina')],
        [Button.inline(" EXTRAS", b'categoria_extras'), Button.inline("⚙️ GENERADOR", b'categoria_generador')],
        [Button.inline("❓ AYUDA", b'categoria_ayuda'), Button.inline("❌ CERRAR", b'cerrar_menu')]
    ]

# ==============================================================================
# SECCIÓN 6: HANDLERS DE COMANDOS DEL MENÚ
# ==============================================================================
@bot_client.on(events.NewMessage(incoming=True, pattern=r'(?i)^/cmds|^/menu|^/help'))
async def cmds_handler(event):
    """Handler para el comando /cmds"""
    try:
        sender_id = event.sender_id
        
        # 🛡️ VERIFICAR ACCESO PRIMERO
        tiene_acceso = verificar_acceso(sender_id)
        
        if not tiene_acceso:
            print(f"⚠️ ACCESO DENEGADO: User ID {sender_id} intentó usar menú")
            await event.reply(
                f"⚠️ <b>No tienes acceso activo.</b>\n\n"
                f"Por favor, envía tu ID al administrador para activar tu membresía.\n\n"
                f"🆔 <b>Tu ID:</b> <code>{sender_id}</code>",
                parse_mode='html'
            )
            return  # DETENER AQUÍ, NO MOSTRAR MENÚ
        
        print("   → Ejecutando comando /cmds - Mostrando menú principal")
        
        mensaje_menu = (
            " **[ MENU DE CONSULTAS ]**\n\n"
            "**PROVENET DOX BOT**\n\n"
            "Selecciona una categoría para ver los comandos disponibles.\n\n"
            "Secciones activas ⇒ 18\n"
            "Comandos activos ⇒ 78"
        )
        
        botones = generar_menu_principal_botones()
        
        await event.reply(mensaje_menu, parse_mode='md', buttons=botones)
        
    except Exception as e:
        print(f"❌ Error al mostrar menú: {e}")
        import traceback
        traceback.print_exc()

@bot_client.on(events.CallbackQuery(pattern=rb'categoria_(\w+)'))
async def mostrar_categoria_handler(event):
    """Handler para mostrar categorías"""
    try:
        sender_id = event.sender_id
        
        # 🛡️ VERIFICAR ACCESO
        tiene_acceso = verificar_acceso(sender_id)
        if not tiene_acceso:
            await event.answer("⚠️ No tienes acceso activo", alert=True)
            return
        
        categoria = event.pattern_match.group(1).decode('utf-8')
        print(f"   → Mostrando categoría: {categoria}")
        
        if categoria not in COMANDOS_CATEGORIAS:
            await event.answer(" Categoría no disponible aún", alert=True)
            return
        
        mensaje = generar_mensaje_pagina(categoria, 1)
        botones = generar_botones_navegacion(categoria, 1)
        
        await event.edit(mensaje, parse_mode='md', buttons=botones)
        await event.answer(f"Mostrando {categoria}", alert=False)
        
    except Exception as e:
        print(f"❌ Error al mostrar categoría: {e}")
        import traceback
        traceback.print_exc()

@bot_client.on(events.CallbackQuery(pattern=rb'nav_(\w+)_(\w+)_(\d+)'))
async def navegacion_paginas_handler(event):
    """Handler para navegación de páginas"""
    try:
        sender_id = event.sender_id
        
        # 🛡️ VERIFICAR ACCESO
        tiene_acceso = verificar_acceso(sender_id)
        if not tiene_acceso:
            await event.answer("⚠️ No tienes acceso activo", alert=True)
            return
        
        categoria = event.pattern_match.group(1).decode('utf-8')
        accion = event.pattern_match.group(2).decode('utf-8')
        pagina_actual = int(event.pattern_match.group(3).decode('utf-8'))
        
        print(f"   → Navegación: {categoria} - {accion} - página {pagina_actual}")
        
        if categoria not in COMANDOS_CATEGORIAS:
            await event.answer(" Categoría no encontrada", alert=True)
            return
        
        total_paginas = COMANDOS_CATEGORIAS[categoria]['total_paginas']
        
        if accion == 'anterior':
            nueva_pagina = pagina_actual - 1
        elif accion == 'siguiente':
            nueva_pagina = pagina_actual + 1
        else:
            await event.answer("️ Acción inválida", alert=True)
            return
        
        if nueva_pagina < 1 or nueva_pagina > total_paginas:
            await event.answer("❌ Página inválida", alert=True)
            return
        
        mensaje = generar_mensaje_pagina(categoria, nueva_pagina)
        botones = generar_botones_navegacion(categoria, nueva_pagina)
        
        await event.edit(mensaje, parse_mode='md', buttons=botones)
        await event.answer(f"Página {nueva_pagina} de {total_paginas}", alert=False)
        
    except Exception as e:
        print(f" Error en navegación: {e}")
        import traceback
        traceback.print_exc()

@bot_client.on(events.CallbackQuery(pattern=b'volver_menu'))
async def volver_menu_handler(event):
    """Handler para volver al menú principal"""
    try:
        sender_id = event.sender_id
        
        # 🛡️ VERIFICAR ACCESO
        tiene_acceso = verificar_acceso(sender_id)
        if not tiene_acceso:
            await event.answer("⚠️ No tienes acceso activo", alert=True)
            return
        
        print("   → Volviendo al menú principal")
        mensaje_menu = (
            "📋 **[ MENU DE CONSULTAS ]**\n\n"
            "**AXEL DOX BOT**\n\n"
            "Selecciona una categoría para ver los comandos disponibles.\n\n"
            "Secciones activas ⇒ 18\n"
            "Comandos activos ⇒ 78"
        )
        
        botones = generar_menu_principal_botones()
        
        await event.edit(mensaje_menu, parse_mode='md', buttons=botones)
        await event.answer("🔙 Menú principal", alert=False)
        
    except Exception as e:
        print(f" Error al volver al menú: {e}")
        import traceback
        traceback.print_exc()

@bot_client.on(events.CallbackQuery(pattern=b'cerrar_menu'))
async def cerrar_menu_handler(event):
    """Handler para cerrar menú"""
    try:
        print("   → Cerrando menú")
        await event.edit("❌ **Menú cerrado**\n\nEscribe /cmds o /menu para volver a abrirlo.")
        await event.answer("Menú cerrado", alert=False)
    except Exception as e:
        print(f"❌ Error al cerrar menú: {e}")
        import traceback
        traceback.print_exc()

# ==============================================================================
# SECCIÓN 7: HANDLER DEL BOT - PROCESAMIENTO DE MENSAJES
# ==============================================================================
@bot_client.on(events.NewMessage(incoming=True))
async def bot_message_handler(event):
    global bot_id, main_account_id
    
    try:
        texto = event.raw_text or event.text or ""
        texto_lower = texto.lower().strip()
        chat_id = event.chat_id
        sender_id = event.sender_id
        
        # 🛡️ CORRECCIÓN: Si es un comando de menú, IGNORAR COMPLETAMENTE
        # El cmds_handler ya se encarga de responder (con menú o con error de acceso)
        if texto_lower.startswith('/cmds') or texto_lower.startswith('/menu') or texto_lower.startswith('/help'):
            print(f"   → Comando de menú detectado ('{texto}'), ignorando en bot_message_handler")
            return
        
        print(f"\n{'='*50}")
        print(f"📩 [BOT] Mensaje recibido")
        print(f"   Chat ID: {chat_id}")
        print(f"   Sender ID: {sender_id}")
        print(f"   Texto: {texto[:80]}...")
        print(f"   Tiene media: {bool(event.media)}")
        
        
        # ==============================================================================
        # PROCESAMIENTO DE CUENTA PRINCIPAL
        # ==============================================================================
        if sender_id == main_account_id:
            print("   → Es de la CUENTA PRINCIPAL")
            
            # CASO 1: Mensaje de texto con "RESULTADO PARA:"
            if "RESULTADO PARA:" in texto and not event.media:
                print("   → Mensaje de texto de resultado")
                lineas = texto.split("\n\n")
                if len(lineas) >= 2:
                    try:
                        chat_destino = int(lineas[0].replace("RESULTADO PARA:", "").strip())
                        respuesta_texto = "\n\n".join(lineas[1:])
                        
                        print(f"   → Chat destino: {chat_destino}")
                        print(f"   → Texto completo ({len(respuesta_texto)} chars): {respuesta_texto[:200]}...")
                        
                        if len(respuesta_texto) > 4000:
                            print(f"   → Texto largo, dividiendo en partes...")
                            partes = [respuesta_texto[i:i+4000] for i in range(0, len(respuesta_texto), 4000)]
                            for idx, parte in enumerate(partes):
                                await bot_client.send_message(chat_destino, parte)
                                print(f"   ✅ Parte {idx+1}/{len(partes)} enviada")
                                await asyncio.sleep(0.3)
                        else:
                            await bot_client.send_message(chat_destino, respuesta_texto)
                            print(f"   ✅ Texto completo enviado")
                        
                        if chat_destino not in resultados_enviados:
                            resultados_enviados[chat_destino] = {
                                'texto': True,
                                'media': False,
                                'time': asyncio.get_event_loop().time()
                            }
                        else:
                            resultados_enviados[chat_destino]['texto'] = True
                        
                        if chat_destino in processing_messages:
                            msg_id = processing_messages[chat_destino]
                            try:
                                await bot_client.edit_message(
                                    chat_destino, 
                                    msg_id, 
                                    "✅ RESULTADO ENVIADO CORRECTAMENTE"
                                )
                                print(f"   ✅ Mensaje 'Procesando...' editado exitosamente")
                            except Exception as e:
                                print(f"   ️ Error al editar mensaje: {e}")
                                import traceback
                                traceback.print_exc()
                        
                        await asyncio.sleep(10)
                        if chat_destino in processing_messages:
                            del processing_messages[chat_destino]
                            print(f"   ✅ Limpiado processing_messages para {chat_destino}")
                        
                    except Exception as e:
                        print(f"   ❌ Error al procesar resultado: {e}")
                        import traceback
                        traceback.print_exc()
                return
            
            # CASO 2: Mensaje con IMAGEN/PDF
            elif event.media:
                print("   → Media recibido de cuenta principal")
                
                chats_pendientes = list(processing_messages.keys())
                
                if not chats_pendientes:
                    print("   ⚠️ No hay chats pendientes para recibir media")
                    return
                
                for chat_id_pendiente in chats_pendientes:
                    print(f"   → Reenviando media a {chat_id_pendiente}")
                    try:
                        await bot_client.send_file(chat_id_pendiente, event.media, caption=texto)
                        print(f"   ✅ Media + texto reenviados juntos")
                        
                        if chat_id_pendiente not in resultados_enviados:
                            resultados_enviados[chat_id_pendiente] = {
                                'texto': True,
                                'media': True,
                                'time': asyncio.get_event_loop().time()
                            }
                        else:
                            resultados_enviados[chat_id_pendiente]['media'] = True
                        
                        if chat_id_pendiente in processing_messages:
                            msg_id = processing_messages[chat_id_pendiente]
                            try:
                                await bot_client.edit_message(
                                    chat_id_pendiente, 
                                    msg_id, 
                                    "✅ RESULTADO ENVIADO CORRECTAMENTE"
                                )
                                print(f"   ✅ Mensaje editado para {chat_id_pendiente}")
                            except Exception as e:
                                print(f"   ️ Error al editar mensaje: {e}")
                        
                    except Exception as e:
                        print(f"   ⚠️ Error al reenviar media: {e}")
                
                await asyncio.sleep(10)
                for chat_id_pendiente in chats_pendientes:
                    if chat_id_pendiente in processing_messages:
                        del processing_messages[chat_id_pendiente]
                        print(f"   ✅ Limpiado processing_messages para {chat_id_pendiente}")
                
                return
        
        # ==============================================================================
        # PROCESAMIENTO DE CUENTA SECUNDARIA
        # ==============================================================================
        print("   → Es de CUENTA SECUNDARIA")
        
        # ️ VERIFICAR ACCESO EN CLOUDFLARE KV
        tiene_acceso = verificar_acceso(sender_id)
        
        if not tiene_acceso:
            print(f"⚠️ ACCESO DENEGADO: User ID {sender_id} no tiene acceso en KV")
            await event.reply(
                f"⚠️ <b>No tienes acceso activo.</b>\n\n"
                f"Por favor, envía tu ID al administrador para activar tu membresía.\n\n"
                f"🆔 <b>Tu ID:</b> <code>{sender_id}</code>",
                parse_mode='html'
            )
            return  # DETENER - No procesar
        
        print(f"✅ Usuario {sender_id} tiene acceso verificado")
        
        if chat_id in processing_messages:
            print(f"   ⚠️ Ya hay un procesamiento en curso para {chat_id}, ignorando")
            return
        
        processing_msg = await event.reply(" Procesando...")
        processing_messages[chat_id] = processing_msg.id
        print(f"   → Guardado chat {chat_id} con msg_id {processing_msg.id}")

        if event.media:
            print(f"   → Media detectado, enviando texto + media a cuenta principal")
            caption_principal = f"PROCESAR PARA: {chat_id}\n\n{texto}"
            await bot_client.send_file(MAIN_ACCOUNT, event.media, caption=caption_principal)
        else:
            await bot_client.send_message(MAIN_ACCOUNT, f"PROCESAR PARA: {chat_id}\n\n{texto}")
        print(f"   ✅ Enviado a cuenta principal")
        
    except Exception as e:
        print(f"❌ [BOT] ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

# ==============================================================================
# SECCIÓN 8: HANDLER DE CUENTA PRINCIPAL (CORREGIDO - ENVÍA TODOS LOS MENSAJES)
# ==============================================================================
@user_client.on(events.NewMessage(incoming=True))
async def user_receive_handler(event):
    global bot_id, main_account_id
    
    try:
        sender_id = event.sender_id
        texto = event.raw_text or event.text or ""
        
        print(f"\n{'='*50}")
        print(f"📩 [USER] Mensaje recibido")
        print(f"   Sender ID: {sender_id}")
        print(f"   Texto: {texto[:100]}...")
        
        if bot_id is None:
            print("   ⚠️ bot_id es None, ignorando")
            return
        
        if sender_id != bot_id:
            print(f"   ❌ Ignorado: sender_id ({sender_id}) != bot_id ({bot_id})")
            return
        
        print("   ✅ Paso 1: Viene del bot")
        
        if "PROCESAR PARA:" not in texto:
            print(f"   ⚠️ Ignorado: no contiene 'PROCESAR PARA:'")
            return
        
        print("   ✅ Paso 2: Es para procesar")
        
        try:
            primera_linea = texto.split("\n\n")[0]
            chat_destino = int(primera_linea.replace("PROCESAR PARA:", "").strip())
            print(f"   ✅ Paso 3: Chat destino = {chat_destino}")
        except Exception as e:
            print(f"   ❌ Paso 3 falló: {e}")
            return
        
        lineas = texto.split("\n\n")
        if len(lineas) < 2:
            print("   ❌ Formato incorrecto (menos de 2 líneas)")
            return
        
        texto_original = lineas[1].strip()
        print(f"   ✅ Texto original: {texto_original}")
        
        partes = texto_original.split()
        comando_guia = partes[0].replace('/', '').lower() if partes else ""
        
        numero_buscar = " ".join(partes[1:]) if len(partes) > 1 else ""
        print(f"   ✅ Comando guía: '{comando_guia}' | Número a buscar: '{numero_buscar}'")
        
        print(f"   → Enviando a Provenet...")
        try:
            if event.media:
                print(f"   → Media detectado, enviando texto + media a Provenet")
                msg_enviado = await user_client.send_file(CODE_BOT, event.media, caption=texto_original)
            else:
                msg_enviado = await user_client.send_message(CODE_BOT, texto_original)
            print("   ✅ Enviado a Provenet")
            
            msg_enviado_id = msg_enviado.id
            msg_enviado_time = msg_enviado.date
            print(f"   → Mensaje enviado ID: {msg_enviado_id}, Time: {msg_enviado_time}")
            
        except Exception as e:
            print(f"   ❌ Error al enviar a Provenet: {e}")
            await user_client.send_message(BOT_USERNAME, f"RESULTADO PARA: {chat_destino}\n\n❌ Error: {e}")
            return
        
        print("   ⏳ Iniciando espera (máx 45 segundos, verifica cada 3s)...")
        
        mensajes_validos = []
        palabras_basura = ['espera', 'consultando', 'cargando', 'procesando', 'generando', 'por favor']
        
        tiempo_maximo = 45
        intervalo_verificacion = 3
        tiempo_esperado = 0
        tiempo_sin_nuevos_mensajes = 0
        
        while tiempo_esperado < tiempo_maximo:
            espera = intervalo_verificacion
            
            print(f"    Esperando {espera} segundos... (total: {tiempo_esperado}s/{tiempo_maximo}s)")
            await asyncio.sleep(espera)
            tiempo_esperado += espera
            
            print(f"   🔍 Verificando respuestas después de {tiempo_esperado}s...")
            
            try:
                mensajes = await user_client.get_messages(CODE_BOT, limit=100)
                print(f"   → {len(mensajes)} mensajes encontrados")
                
                mensajes_validos_temp = []
                
                for i, msg in enumerate(mensajes):
                    msg_text = msg.text or msg.raw_text or ""
                    msg_has_media = msg.media is not None
                    msg_date = msg.date
                    
                    print(f"      Mensaje {i+1}: ID={msg.id}, text='{msg_text[:40]}...', media={msg_has_media}, date={msg_date}")
                    
                    if msg_date <= msg_enviado_time:
                        print(f"         → Ignorado (es anterior o igual al enviado)")
                        continue
                    
                    if msg.id == msg_enviado_id:
                        print(f"         → Ignorado (es el que enviamos)")
                        continue
                    
                    if msg_text and any(x in msg_text.lower() for x in palabras_basura):
                        print(f"         → Ignorado (es basura)")
                        continue
                    
                    comando_limpio = texto_original.strip().lower()
                    mensaje_limpio = msg_text.strip().lower()
                    
                    if mensaje_limpio == comando_limpio:
                        print(f"         → Ignorado (es el comando original - ECO)")
                        continue
                    
                    if len(mensaje_limpio) < len(comando_limpio) + 15 and comando_limpio in mensaje_limpio:
                        print(f"         → Ignorado (eco del comando)")
                        continue
                    
                    es_valido = False
                    
                    if msg_has_media:
                        es_valido = True
                        print(f"         ✅ VÁLIDO (media): Agregado")
                    
                    if not es_valido and len(msg_text) > 50:
                        es_valido = True
                        print(f"         ✅ VÁLIDO (texto largo): Agregado")
                    
                    if not es_valido and numero_buscar and numero_buscar.lower() in msg_text.lower():
                        es_valido = True
                        print(f"         ✅ VÁLIDO (nombre '{numero_buscar}' encontrado): Agregado")
                    
                    if not es_valido:
                        patrones_datos = ['dni:', 'apellidos:', 'nombres:', 'busqueda:', 'total:']
                        if any(patron in msg_text.lower() for patron in patrones_datos):
                            es_valido = True
                            print(f"         ✅ VÁLIDO (contiene datos): Agregado")
                    
                    if not es_valido and comando_guia and comando_guia in msg_text.lower():
                        es_valido = True
                        print(f"         ✅ VÁLIDO (comando '{comando_guia}' encontrado): Agregado")
                    
                    if es_valido:
                        mensajes_validos_temp.append(msg)
                
                mensajes_validos_temp.sort(key=lambda x: x.date)
                
                nuevos_ids = [msg.id for msg in mensajes_validos_temp if msg.id not in [m.id for m in mensajes_validos]]
                
                if nuevos_ids:
                    print(f"   ✅ Detectados {len(nuevos_ids)} NUEVOS mensajes válidos")
                    # ✅ CORRECCIÓN: AGREGAR nuevos mensajes sin perder los anteriores
                    mensajes_validos = list({msg.id: msg for msg in mensajes_validos + mensajes_validos_temp}.values())
                    tiempo_sin_nuevos_mensajes = 0
                else:
                    tiempo_sin_nuevos_mensajes += espera
                    print(f"   ⏱️ Sin nuevos mensajes por {tiempo_sin_nuevos_mensajes}s")
                
                if len(mensajes_validos) > 0 and tiempo_sin_nuevos_mensajes >= 15:
                    print(f"   ✅ Ya no llegan más mensajes después de {tiempo_sin_nuevos_mensajes}s")
                    break
                
                if tiempo_esperado >= tiempo_maximo:
                    print(f"   ⏰ Timeout de {tiempo_maximo}s alcanzado")
                    break
                
            except Exception as e:
                print(f"   ⚠️ Error al verificar: {e}")
                continue
        
        mensajes_validos = list({msg.id: msg for msg in mensajes_validos}.values())
        mensajes_validos.sort(key=lambda x: x.date)
        
        if not mensajes_validos:
            print(f"   ⚠️ No se encontró respuesta válida después de {tiempo_maximo}s")
            await user_client.send_message(BOT_USERNAME, f"RESULTADO PARA: {chat_destino}\n\n⚠️ ERROR: No se recibió respuesta en {tiempo_maximo} segundos.")
            print("   ✅ Mensaje de timeout enviado al bot")
            return
        
        print(f"   📊 Total de mensajes válidos capturados: {len(mensajes_validos)}")
        
        try:
            # ✅ ENVIAR TODOS LOS MENSAJES CAPTURADOS (NO SOLO UNO)
            for msg in mensajes_validos:
                header = f"RESULTADO PARA: {chat_destino}\n\n"
                
                if msg.media:
                    texto_completo = header + (msg.text or "")
                    await user_client.send_file(BOT_USERNAME, msg.media, caption=texto_completo)
                    print(f"   ✅ Enviado: media + texto")
                elif msg.text:
                    await user_client.send_message(BOT_USERNAME, header + msg.text)
                    print(f"   ✅ Enviado: solo texto")
                
                await asyncio.sleep(0.3)
            
            print(f"   ✅ TODOS los {len(mensajes_validos)} mensajes enviados al bot")
            
        except Exception as e:
            print(f"   ❌ Error al enviar al bot: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"❌ [USER] ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

# ==============================================================================
# SECCIÓN 9: FUNCIÓN MAIN
# ==============================================================================
async def main():
    global bot_id, main_account_id
    
    print("\n" + "="*60)
    print(" INICIANDO AXEL BOT")
    print("="*60)
    
    print(" Iniciando cuenta principal...")
    await user_client.start()
    me = await user_client.get_me()
    main_account_id = me.id
    print(f"✅ Cuenta: {me.first_name} (ID: {main_account_id})")

    print("\n Iniciando Bot...")
    await bot_client.start(bot_token=BOT_TOKEN)
    bot_me = await bot_client.get_me()
    bot_id = bot_me.id
    print(f"✅ Bot: @{bot_me.username} (ID: {bot_id})")

    print("\n" + "="*60)
    print("🚀 AXEL BOT INICIADO - Esperando mensajes...")
    print("="*60 + "\n")

    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

# ==============================================================================
# SECCIÓN 10: EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Bot detenido.")
