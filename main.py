import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import requests
import time
from datetime import datetime
import uuid

# ==============================================================================
# SECCIÓN 1: CONFIGURACIÓN
# ==============================================================================
API_ID = 35552520
API_HASH = "5eda0ce7ccc5228d007dd3bb00e69572"
BOT_TOKEN = "8937193409:AAEyc628t2h416UFTC7veY7Gnr2Y4vvt4y4"
CODE_BOT = "@ProvenetDoxBot"
MAIN_ACCOUNT = "@gartuoe733"
BOT_USERNAME = "@axel_vipBOT"

# 🔑 CREDENCIALES DE CLOUDFLARE
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
processing_messages = {}  # {chat_id: {'request_id': 'xxx', 'termino': 'yyy', 'msg_id': 'zzz'}}
pending_media = {}
resultados_enviados = {}

# ==============================================================================
# FUNCIÓN PARA VERIFICAR ACCESO EN CLOUDFLARE KV
# ==============================================================================
def verificar_acceso(user_id):
    """Verifica si el usuario tiene acceso en Cloudflare KV"""
    try:
        timestamp = int(time.time())
        url = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/storage/kv/namespaces/{KV_NAMESPACE_ID}/values/user:{user_id}?t={timestamp}"
        
        headers = {
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            try:
                data = response.json()
                
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
                        return True
                    else:
                        return False
                else:
                    return False
            except Exception:
                return False
        else:
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar acceso: {e}")
        return False

# ==============================================================================
# SECCIÓN 4: LISTA DE COMANDOS
# ==============================================================================
def generar_lista_comandos():
    """Genera la lista completa de comandos"""
    
    comandos = """📄 **RENIEC:**
/dni 44441111 - Foto y datos de una persona
/nm JUAN CARLOS RAMIREZ ESPINOZA - Búsqueda por nombres

📱 **METADATA:**
/metadata 44445555 - Metadata completa DNI + PDF
/metanum 987654321 - Seeker módulo 1 PDF
/seekerdni 44445555 - Seeker módulo 2 DNI
/seekernum 987654321 - Seeker módulo 2 número

📞 **TELEFONIA:**
/fonos 44445555 - Teléfonos por DNI
/fono 986699757 - Titular por número
/lineas 44445555 - Líneas por DNI
/titular 951568168 - Titular detallado
/movistar 967245095 - Consulta Movistar
/bitel 910884863 - Consulta Bitel
/claro 923990901 - Consulta Claro
/valnum 987654321 - Consulta operador
/cel 987654321 - Telefonía por número
/tel 44445555 - Telefonía por DNI
/clardni 44445555 - Líneas Claro por DNI
/telp 987654321 - Búsqueda titular
/telx 44445555 - Telefonía general

👤 **FACIAL:**
/facial [foto] - Reconocimiento facial masivo

👤 **PERSONAS:**
/seekerdni 44445555 - Seeker completo por DNI
/metadni 44445555 - Seeker completo PDF
/seeker 45454545 - Seeker completo v2.0
/co 44445555 - Correos de una persona

🚗 **VEHICULOS:**
/insve ABC123 - Inscripción vehicular PDF
/pla ABC123 - Datos de vehículo
/placapdf ABC123 - Sunarp asientos PDF
/tiv BFA908 - Tive online Sunarp PDF
/tive BFA908 - Tive original Sunarp PDF
/tiveg ABC123 - Tive generado Sunarp PDF
/tarjeta ABC-123 - Tarjeta de propiedad
/pla2 ABC123 - Datos placa imagen
/citv ABC123 - Revisión técnica TXT
/soat ABC123 - SOAT vehicular texto
/soatpdf ABC123 - SOAT vehicular PDF
/boleta ABC123 - Boleta informativa PDF

⚖️ **DELITOS:**
/anteper 44445555 - Antecedentes personales PDF
/rqper 44445555 - Requisitoria persona PDF
/denuncias 44445555 - Denuncias policiales
/sidpolpdf 44445555 - Sidpol PDF

💰 **FINANCIERO:**
/sentinel 44445555 - SBS Central de riesgos PDF

📑 **SUNARP:**
/sunarp 44445555 - Sunarp texto
/sunarpdf 44445555 - Sunarp PDF
/bienespdf 44445555 - Bienes inmuebles PDFs

⚖️ **JUSTICIA:**
/fiscalia 44445555 - Fiscalía texto
/fiscaliapdf 44445555 - Fiscalía PDF DNI
/fisruc 20536902385 - Fiscalía PDF RUC
/fisructext 20536902385 - Fiscalía texto RUC
/fisnm URIEL|BERNAL|JUSCACHI - Fiscalía por nombres TXT
/fisnmpdf URIEL|BERNAL|JUSCACHI - Fiscalía por nombres PDF
/fiscaso 01805114504-2023-000045-0000 - Fiscalía caso texto
/fiscasopdf 01805114504-2023-000045-0000 - Fiscalía caso PDF

💵 **SUNAT:**
/ruc 20165465009 - RUC info completo

👨‍👩‍👧 **FAMILIA:**
/ag 44441111 - Árbol genealógico texto
/ag2 44441111 - Árbol genealógico texto v2
/agv 44441111 - Árbol genealógico visual PNG
/famivi 44441111 - Árbol familiar visual

🎓 **MINEDU:**
/minedu 44445555 - Notas Minedu PDF

🚦 **MTC:**
/licencia 45454545 - Licencia de conducir
/licenciapdf 45454545 - Licencia electrónica PDF
/record 45454545 - Papeletas por DNI PDF
/tarjeta ABS920 - Tarjeta de propiedad imagen
/citv ABC123 - Revisión técnica TXT
/citvpdf ABC123 - Revisión técnica PDF
/rqpla APM384 - Requisitoria vehicular PDF

💤 **DESCANSOS:**
/laluz 44445555|INFECCION GASTROINTESTINAL|3|AMOXICILINA 500MG - Descanso La Luz PDF
/dminsa 60685138|INFECCIÓN ESTOMACAL|HOSPITAL NACIONAL CAYETANO HEREDIA|21-04-2026|2 - Descanso Minsa PDF
/dessalud DNI|NOMBRE|CONTINGENCIA|DIAS - Descanso Essalud PDF

🇦🇷 **ARGENTINA:**
/dniarg 12345678 - Búsqueda por DNI Argentina
/telarg 2284524520 - Búsqueda por teléfono Argentina
/nmarg juan perez - Búsqueda por nombre Argentina

⚙️ **GENERADOR:**
/c4 44441111 - C4 azul generado
/c4b 44441111 - C4 blanco generado
/c4i 44441111 - Certificado de inscripción
/dniv 44445555 - DNI virtual azul
/dnive 44445555 - DNI electrónico
/antpe 44445555 - Certificado antecedentes penales
/antju 44445555 - Certificado antecedentes judiciales
/antpol 44445555 - Antecedentes policiales

🌐 **EXTRAS:**
/ip 192.199.248.75 - Geocalización por IP
/dpm Juan Perez|Ingeniería de Sistemas - Diploma USC

━━━━━━━━━━━━━━━━━━━━
📊 Total: 78 comandos disponibles
💡 Usa los ejemplos mostrados como referencia"""
    
    return comandos

# ==============================================================================
# SECCIÓN 5: HANDLERS DE COMANDOS
# ==============================================================================
@bot_client.on(events.NewMessage(incoming=True, pattern=r'(?i)^/cmds|^/menu|^/help|^/comandos'))
async def cmds_handler(event):
    """Handler para el comando /cmds"""
    try:
        sender_id = event.sender_id
        
        tiene_acceso = verificar_acceso(sender_id)
        
        if not tiene_acceso:
            print(f"⚠️ ACCESO DENEGADO: User ID {sender_id}")
            await event.reply(
                f"⚠️ <b>No tienes acceso activo.</b>\n\n"
                f"🆔 <b>Tu ID:</b> <code>{sender_id}</code>",
                parse_mode='html'
            )
            raise events.StopPropagation
        
        print("   → Ejecutando /cmds")
        
        lista_comandos = generar_lista_comandos()
        
        mensaje = (
            f"**[ LISTA DE COMANDOS ]**\n\n"
            f"**AXEL DOX BOT**\n\n"
            f"{lista_comandos}"
        )
        
        await event.reply(mensaje, parse_mode='md')
        
        raise events.StopPropagation
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# ==============================================================================
# SECCIÓN 6: HANDLER DEL BOT - PROCESAMIENTO
# ==============================================================================
@bot_client.on(events.NewMessage(incoming=True))
async def bot_message_handler(event):
    global bot_id, main_account_id
    
    try:
        texto = event.raw_text or event.text or ""
        texto_lower = texto.lower().strip()
        chat_id = event.chat_id
        sender_id = event.sender_id
        
        if texto_lower.startswith('/cmds') or texto_lower.startswith('/menu') or texto_lower.startswith('/help'):
            return
        
        print(f"\n{'='*50}")
        print(f"📩 [BOT] Mensaje recibido")
        print(f"   Chat ID: {chat_id}")
        print(f"   Sender ID: {sender_id}")
        
        # ==============================================================================
        # PROCESAMIENTO DE CUENTA PRINCIPAL
        # ==============================================================================
        if sender_id == main_account_id:
            print("   → Es de la CUENTA PRINCIPAL")
            
            if "RESULTADO PARA:" in texto and not event.media:
                print("   → Mensaje de texto de resultado")
                lineas = texto.split("\n\n")
                if len(lineas) >= 2:
                    try:
                        chat_destino = int(lineas[0].replace("RESULTADO PARA:", "").strip())
                        respuesta_texto = "\n\n".join(lineas[1:])
                        
                        if len(respuesta_texto) > 4000:
                            partes = [respuesta_texto[i:i+4000] for i in range(0, len(respuesta_texto), 4000)]
                            for idx, parte in enumerate(partes):
                                await bot_client.send_message(chat_destino, parte)
                                await asyncio.sleep(0.3)
                        else:
                            await bot_client.send_message(chat_destino, respuesta_texto)
                        
                        if chat_destino in processing_messages:
                            msg_id = processing_messages[chat_destino].get('msg_id')
                            if msg_id:
                                try:
                                    await bot_client.edit_message(
                                        chat_destino, msg_id, 
                                        "✅ RESULTADO ENVIADO CORRECTAMENTE"
                                    )
                                except Exception as e:
                                    print(f"   ⚠️ Error al editar: {e}")
                        
                        await asyncio.sleep(10)
                        if chat_destino in processing_messages:
                            del processing_messages[chat_destino]
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        import traceback
                        traceback.print_exc()
                return
            
            elif event.media:
                print("   → Media recibido")
                
                chats_pendientes = list(processing_messages.keys())
                
                if not chats_pendientes:
                    return
                
                for chat_id_pendiente in chats_pendientes:
                    try:
                        await bot_client.send_file(chat_id_pendiente, event.media, caption=texto)
                        
                        if chat_id_pendiente in processing_messages:
                            msg_id = processing_messages[chat_id_pendiente].get('msg_id')
                            if msg_id:
                                await bot_client.edit_message(
                                    chat_id_pendiente, msg_id,
                                    "✅ RESULTADO ENVIADO CORRECTAMENTE"
                                )
                        
                    except Exception as e:
                        print(f"   ⚠️ Error: {e}")
                
                await asyncio.sleep(10)
                for chat_id_pendiente in chats_pendientes:
                    if chat_id_pendiente in processing_messages:
                        del processing_messages[chat_id_pendiente]
                
                return
        
        # ==============================================================================
        # PROCESAMIENTO DE CUENTA SECUNDARIA
        # ==============================================================================
        print("   → Es de CUENTA SECUNDARIA")
        
        tiene_acceso = verificar_acceso(sender_id)
        
        if not tiene_acceso:
            await event.reply(
                f"⚠️ <b>No tienes acceso activo.</b>\n\n"
                f"🆔 <b>Tu ID:</b> <code>{sender_id}</code>",
                parse_mode='html'
            )
            return
        
        if chat_id in processing_messages:
            print(f"   ⚠️ Ya hay procesamiento en curso")
            return
        
        processing_msg = await event.reply(" Procesando...")
        
        # 🔑 GENERAR ID ÚNICO PARA ESTA CONSULTA
        request_id = str(uuid.uuid4())[:8]  # ID único de 8 caracteres
        
        processing_messages[chat_id] = {
            'msg_id': processing_msg.id,
            'request_id': request_id,
            'timestamp': time.time()
        }
        
        print(f"   → ID de solicitud: {request_id}")

        if event.media:
            caption_principal = f"PROCESAR PARA: {chat_id}\nREQUEST_ID: {request_id}\n\n{texto}"
            await bot_client.send_file(MAIN_ACCOUNT, event.media, caption=caption_principal)
        else:
            await bot_client.send_message(MAIN_ACCOUNT, f"PROCESAR PARA: {chat_id}\nREQUEST_ID: {request_id}\n\n{texto}")
        print(f"   ✅ Enviado a cuenta principal")
        
    except Exception as e:
        print(f"❌ [BOT] ERROR: {e}")
        import traceback
        traceback.print_exc()


# ==============================================================================
# SECCIÓN 7: HANDLER DE CUENTA PRINCIPAL (CON ID ÚNICO POR CONSULTA)
# ==============================================================================
@user_client.on(events.NewMessage(incoming=True))
async def user_receive_handler(event):
    global bot_id, main_account_id
    
    try:
        sender_id = event.sender_id
        texto = event.raw_text or event.text or ""
        
        print(f"\n{'='*50}")
        print(f"📩 [USER] Mensaje recibido del Bot")
        
        if bot_id is None or sender_id != bot_id:
            return
        
        if "PROCESAR PARA:" not in texto:
            return
        
        try:
            primera_linea = texto.split("\n\n")[0]
            chat_destino = int(primera_linea.replace("PROCESAR PARA:", "").strip())
        except Exception:
            return
        
        lineas = texto.split("\n\n")
        if len(lineas) < 2:
            return
        
        texto_original = lineas[1].strip()
        
        # 🔑 EXTRAER REQUEST_ID SI EXISTE
        request_id_enviado = None
        if "REQUEST_ID:" in texto:
            request_id_enviado = texto.split("REQUEST_ID:")[1].split("\n")[0].strip()
            print(f"   ✅ Request ID recibido: {request_id_enviado}")
        
        # 🔑 EXTRAER TÉRMINO DE BÚSQUEDA
        partes_comando = texto_original.split(' ', 1)
        comando = partes_comando[0].lower() if len(partes_comando) > 0 else ""
        termino_busqueda = partes_comando[1].strip() if len(partes_comando) > 1 else ""
        
        print(f"   🔍 Comando: {comando}")
        print(f"   🔍 Término: '{termino_busqueda}'")
        
        es_comando_nm = comando.startswith('/nm') or comando.startswith('nm')
        
        print(f"   → Enviando a Provenet...")
        try:
            if event.media:
                msg_enviado = await user_client.send_file(CODE_BOT, event.media, caption=texto_original)
            else:
                msg_enviado = await user_client.send_message(CODE_BOT, texto_original)
            
            msg_enviado_id = msg_enviado.id
            msg_enviado_time = msg_enviado.date
            print(f"   ✅ Enviado (Msg ID: {msg_enviado_id})")
            
        except Exception as e:
            await user_client.send_message(BOT_USERNAME, f"RESULTADO PARA: {chat_destino}\n\n❌ Error: {e}")
            return
        
        print(f"   ⏳ Esperando respuesta que contenga: '{termino_busqueda}'...")
        
        mensajes_finales = []
        ids_ya_procesados = set()
        palabras_basura = ['espera', 'consultando', 'cargando', 'procesando', 'generando']
        respuesta_completa = False
        
        tiempo_maximo = 45
        tiempo_esperado = 0
        
        while tiempo_esperado < tiempo_maximo and not respuesta_completa:
            await asyncio.sleep(3)
            tiempo_esperado += 3
            
            try:
                mensajes = await user_client.get_messages(CODE_BOT, limit=50)
                
                for msg in mensajes:
                    if msg.id in ids_ya_procesados:
                        continue
                    
                    if msg.date <= msg_enviado_time:
                        continue
                    
                    # Verificar si es respuesta a nuestro mensaje
                    es_nuestra_respuesta = False
                    if hasattr(msg, 'reply_to_msg_id') and msg.reply_to_msg_id == msg_enviado_id:
                        es_nuestra_respuesta = True
                    elif not msg.text or msg.text.strip().lower() != texto_original.strip().lower():
                        es_nuestra_respuesta = True
                    
                    if not es_nuestra_respuesta:
                        continue

                    msg_text = msg.text or msg.raw_text or ""
                    
                    # 🔑 DETECTAR MENSAJE DE ÉXITO
                    if "consulta se hizo de manera exitosa" in msg_text.lower() or "consulta exitosa" in msg_text.lower():
                        print(f"   ✅ Detectado mensaje de éxito")
                        mensajes_finales.append(msg)
                        ids_ya_procesados.add(msg.id)
                        respuesta_completa = True
                        break
                    
                    # Ignorar mensajes de espera
                    if msg_text and any(x in msg_text.lower() for x in palabras_basura):
                        continue
                    
                    # Ignorar eco del comando
                    comando_limpio = texto_original.strip().lower()
                    mensaje_limpio = msg_text.strip().lower()
                    if mensaje_limpio == comando_limpio:
                        continue
                    if len(mensaje_limpio) < len(comando_limpio) + 10 and comando_limpio in mensaje_limpio:
                        continue
                    
                    # 🔑 VERIFICACIÓN 100%: El mensaje DEBE contener el término COMPLETO
                    mensaje_en_mayusculas = msg_text.upper()
                    termino_en_mayusculas = termino_busqueda.upper()
                    
                    if termino_en_mayusculas not in mensaje_en_mayusculas:
                        print(f"   ⚠️ NO contiene '{termino_busqueda}' - Ignorando")
                        continue
                    
                    # ✅ CAPTURAR MENSAJE
                    mensajes_finales.append(msg)
                    ids_ya_procesados.add(msg.id)
                    print(f"   ✅ CAPTADO - Contiene '{termino_busqueda}'")
                    print(f"   📥 Total: {len(mensajes_finales)}")
                
                if respuesta_completa:
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
                continue

        # ENVÍO DE RESULTADOS
        if not mensajes_finales:
            print("   ⚠️ Sin respuesta")
            await user_client.send_message(BOT_USERNAME, f"RESULTADO PARA: {chat_destino}\n\n⚠️ ERROR: Sin respuesta")
        else:
            total = len(mensajes_finales)
            total_resultados = total - 1
            print(f"   📊 Total: {total_resultados} resultados")
            
            if es_comando_nm and total_resultados > 1:
                print(f"   📄 Creando TXT...")
                
                contenido_completo = ""
                contador = 0
                for idx, msg in enumerate(mensajes_finales, 1):
                    if msg.text and "consulta se hizo de manera exitosa" not in msg.text.lower():
                        contador += 1
                        contenido_completo += f"\n{'='*60}\n"
                        contenido_completo += f" RESULTADO {contador} DE {total_resultados}\n"
                        contenido_completo += f"{'='*60}\n\n"
                        contenido_completo += msg.text
                        contenido_completo += f"\n\n"
                
                nombre_archivo = f"RESULTADO_NM_{chat_destino}.txt"
                
                await user_client.send_file(
                    BOT_USERNAME,
                    contenido_completo.encode('utf-8'),
                    caption=f" **RESULTADO PARA: {chat_destino}**\n\n📦 {total_resultados} resultados",
                    filename=nombre_archivo
                )
                
                print(f"   ✅ TXT enviado")
            
            else:
                print(f"   📤 Enviando {total_resultados} mensaje(s)...")
                
                for idx, msg in enumerate(mensajes_finales, 1):
                    try:
                        msg_text = msg.text or ""
                        
                        if "consulta se hizo de manera exitosa" in msg_text.lower():
                            continue
                        
                        header = f"RESULTADO PARA: {chat_destino}\n\n"
                        
                        if total_resultados > 1:
                            header += f"**📦 PARTE {idx} DE {total_resultados}**\n\n"
                        
                        if msg.media:
                            await user_client.send_file(BOT_USERNAME, msg.media, caption=header + msg_text)
                        else:
                            await user_client.send_message(BOT_USERNAME, header + msg_text)
                        
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                        continue

            print(f"   🎉 PROCESO COMPLETADO")
        
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"❌ [USER] ERROR: {e}")
        import traceback
        traceback.print_exc()


# ==============================================================================
# SECCIÓN 8: FUNCIÓN MAIN
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

    print("\n🤖 Iniciando Bot...")
    await bot_client.start(bot_token=BOT_TOKEN)
    bot_me = await bot_client.get_me()
    bot_id = bot_me.id
    print(f"✅ Bot: @{bot_me.username} (ID: {bot_id})")

    print("\n" + "="*60)
    print("✨ AXEL BOT INICIADO")
    print("="*60 + "\n")

    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )

# ==============================================================================
# SECCIÓN 9: EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot detenido.")
