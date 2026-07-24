import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button
import requests
import time
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
processing_messages = {}
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
        print(f" Error al verificar acceso: {e}")
        return False

# ==============================================================================
# SECCIÓN 4: LISTA DE COMANDOS (TEXTO SIMPLE)
# ==============================================================================
def generar_lista_comandos():
    """Genera la lista completa de comandos en texto simple"""
    
    comandos = """📄 **RENIEC:**
/dni <dni> - Foto y datos de una persona (2 créditos)
/nm <nombres y apellidos> - Búsqueda por nombres (1 crédito)

📱 **METADATA:**
/metadata <dni> - Metadata completa DNI + PDF (20 créditos)
/metanum <numero> - Seeker módulo 1 PDF (10 créditos)
/seekerdni <dni> - Seeker módulo 2 DNI (10 créditos)
/seekernum <numero> - Seeker módulo 2 número (30 créditos)

📞 **TELEFONIA:**
/fonos <dni> - Teléfonos por DNI (5 créditos)
/fono <numero> - Titular por número (5 créditos)
/lineas <dni> - Líneas por DNI (5 créditos)
/titular <numero> - Titular detallado (5 créditos)
/movistar <numero> - Consulta Movistar (5 créditos)
/bitel <numero> - Consulta Bitel (5 créditos)
/claro <numero> - Consulta Claro (7 créditos)
/valnum <numero> - Consulta operador (3 créditos)
/cel <numero> - Telefonía por número (5 créditos)
/tel <dni> - Telefonía por DNI (5 créditos)
/clardni <dni> - Líneas Claro por DNI (5 créditos)
/telp <numero> - Búsqueda titular (5 créditos)
/telx <dni o numero> - Telefonía general (5 créditos)

 **FACIAL:**
/facial [foto] - Reconocimiento facial masivo (45 créditos)

👤 **PERSONAS:**
/seekerdni <dni> - Seeker completo por DNI (10 créditos)
/metadni <dni> - Seeker completo PDF (25 créditos)
/seeker <dni> - Seeker completo v2.0 (15 créditos)
/co <dni> - Correos de una persona (5 créditos)

🚗 **VEHICULOS:**
/insve <placa> - Inscripción vehicular PDF (10 créditos)
/pla <placa> - Datos de vehículo (5 créditos)
/placapdf <placa> - Sunarp asientos PDF (10 créditos)
/tiv <placa> - Tive online Sunarp PDF (15 créditos)
/tive <placa> - Tive original Sunarp PDF (15 créditos)
/tiveg <placa> - Tive generado Sunarp PDF (15 créditos)
/tarjeta <placa> - Tarjeta de propiedad (10 créditos)
/pla2 <placa> - Datos placa imagen (2 créditos)
/citv <placa> - Revisión técnica TXT (8 créditos)
/soat <placa> - SOAT vehicular texto (7 créditos)
/soatpdf <placa> - SOAT vehicular PDF (7 créditos)
/boleta <placa> - Boleta informativa PDF (10 créditos)

 **DELITOS:**
/anteper <dni> - Antecedentes personales PDF (8 créditos)
/rqper <dni> - Requisitoria persona PDF (8 créditos)
/denuncias <dni> - Denuncias policiales (20 créditos)
/sidpolpdf <dni> - Sidpol PDF (15 créditos)

💰 **FINANCIERO:**
/sentinel <dni> - SBS Central de riesgos PDF (8 créditos)

📑 **SUNARP:**
/sunarp <dni> - Sunarp texto (6 créditos)
/sunarpdf <dni> - Sunarp PDF (10 créditos)
/bienespdf <dni> - Bienes inmuebles PDFs (12 créditos)

️ **JUSTICIA:**
/fiscalia <dni> - Fiscalía texto (12 créditos)
/fiscaliapdf <dni> - Fiscalía PDF DNI (30 créditos)
/fisruc <ruc> - Fiscalía PDF RUC (30 créditos)
/fisructext <ruc> - Fiscalía texto RUC (12 créditos)
/fisnm <nombres> - Fiscalía por nombres TXT (30 créditos)
/fisnmpdf <nombres> - Fiscalía por nombres PDF (30 créditos)
/fiscaso <caso> - Fiscalía caso texto (12 créditos)
/fiscasopdf <caso> - Fiscalía caso PDF (30 créditos)

💵 **SUNAT:**
/ruc <ruc> - RUC info completo (5 créditos)

👨‍👩‍👧 **FAMILIA:**
/ag <dni> - Árbol genealógico texto (8 créditos)
/ag2 <dni> - Árbol genealógico texto v2 (8 créditos)
/agv <dni> - Árbol genealógico visual PNG (15 créditos)
/famivi <dni> - Árbol familiar visual (12 créditos)

🎓 **MINEDU:**
/minedu <dni> - Notas Minedu PDF (10 créditos)

🚦 **MTC:**
/licencia <dni> - Licencia de conducir (6 créditos)
/licenciapdf <dni> - Licencia electrónica PDF (10 créditos)
/record <dni> - Papeletas por DNI PDF (10 créditos)
/tarjeta <placa> - Tarjeta de propiedad imagen (8 créditos)
/citv <placa> - Revisión técnica TXT (6 créditos)
/citvpdf <placa> - Revisión técnica PDF (12 créditos)
/rqpla <placa> - Requisitoria vehicular PDF (8 créditos)

💤 **DESCANSOS:**
/laluz <dni>|<diagnostico>|<dias>|<medicamentos> - Descanso La Luz PDF (60 créditos)
/dminsa <dni>|<diagnostico>|<hospital>|<fecha>|<dias> - Descanso Minsa PDF (50 créditos)
/dessalud <dni>|<nombre>|<contingencia>|<dias> - Descanso Essalud PDF (50 créditos)

🇦🇷 **ARGENTINA:**
/dniarg <dni> - Búsqueda por DNI Argentina (2 créditos)
/telarg <numero> - Búsqueda por teléfono Argentina (2 créditos)
/nmarg <nombre> - Búsqueda por nombre Argentina (2 créditos)

⚙️ **GENERADOR:**
/c4 <dni> - C4 azul generado (5 créditos)
/c4b <dni> - C4 blanco generado (5 créditos)
/c4i <dni> - Certificado de inscripción (8 créditos)
/dniv <dni> - DNI virtual azul (8 créditos)
/dnive <dni> - DNI electrónico (8 créditos)
/antpe <dni> - Certificado antecedentes penales (8 créditos)
/antju <dni> - Certificado antecedentes judiciales (8 créditos)
/antpol <dni> - Antecedentes policiales (8 créditos)

 **EXTRAS:**
/ip <ip> - Geocalización por IP (1 crédito)
/dpm <nombre>|<carrera> - Diploma USC (3 créditos)

━━━━━━━━━━━━━━━━━━━━
📊 Total: 78 comandos disponibles
💳 Créditos requeridos según comando"""
    
    return comandos

# ==============================================================================
# SECCIÓN 5: HANDLERS DE COMANDOS
# ==============================================================================
@bot_client.on(events.NewMessage(incoming=True, pattern=r'(?i)^/cmds|^/menu|^/help|^/comandos'))
async def cmds_handler(event):
    """Handler para el comando /cmds - Muestra lista simple de comandos"""
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
            return
        
        print("   → Ejecutando comando /cmds - Mostrando lista de comandos")
        
        # Obtener lista de comandos
        lista_comandos = generar_lista_comandos()
        
        mensaje = (
            f"**[ LISTA DE COMANDOS ]**\n\n"
            f"**AXEL DOX BOT**\n\n"
            f"{lista_comandos}\n\n"
            f"💡 Usa los comandos directamente con el formato mostrado."
        )
        
        await event.reply(mensaje, parse_mode='md')
        
    except Exception as e:
        print(f"❌ Error al mostrar comandos: {e}")
        import traceback
        traceback.print_exc()

# ==============================================================================
# SECCIÓN 6: HANDLER DEL BOT - PROCESAMIENTO DE MENSAJES
# ==============================================================================
@bot_client.on(events.NewMessage(incoming=True))
async def bot_message_handler(event):
    global bot_id, main_account_id
    
    try:
        texto = event.raw_text or event.text or ""
        texto_lower = texto.lower().strip()
        chat_id = event.chat_id
        sender_id = event.sender_id
        
        # 🛡️ Si es un comando de menú, ignorar
        if texto_lower.startswith('/cmds') or texto_lower.startswith('/menu') or texto_lower.startswith('/help') or texto_lower.startswith('/comandos'):
            return
        
        print(f"\n{'='*50}")
        print(f"📩 [BOT] Mensaje recibido")
        print(f"   Chat ID: {chat_id}")
        print(f"   Sender ID: {sender_id}")
        print(f"   Texto: {texto[:80]}...")
        
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
                        
                        if len(respuesta_texto) > 4000:
                            print(f"   → Texto largo, dividiendo en partes...")
                            partes = [respuesta_texto[i:i+4000] for i in range(0, len(respuesta_texto), 4000)]
                            for idx, parte in enumerate(partes):
                                await bot_client.send_message(chat_destino, parte)
                                await asyncio.sleep(0.3)
                        else:
                            await bot_client.send_message(chat_destino, respuesta_texto)
                        
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
                            except Exception as e:
                                print(f"   ⚠️ Error al editar mensaje: {e}")
                        
                        await asyncio.sleep(10)
                        if chat_destino in processing_messages:
                            del processing_messages[chat_destino]
                        
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
                            except Exception as e:
                                print(f"   ⚠️ Error al editar mensaje: {e}")
                        
                    except Exception as e:
                        print(f"   ⚠️ Error al reenviar media: {e}")
                
                await asyncio.sleep(10)
                for chat_id_pendiente in chats_pendientes:
                    if chat_id_pendiente in processing_messages:
                        del processing_messages[chat_id_pendiente]
                
                return
        
        # ==============================================================================
        # PROCESAMIENTO DE CUENTA SECUNDARIA
        # ==============================================================================
        print("   → Es de CUENTA SECUNDARIA")
        
        # 🛡️ VERIFICAR ACCESO EN CLOUDFLARE KV
        tiene_acceso = verificar_acceso(sender_id)
        
        if not tiene_acceso:
            print(f"⚠️ ACCESO DENEGADO: User ID {sender_id} no tiene acceso en KV")
            await event.reply(
                f"⚠️ <b>No tienes acceso activo.</b>\n\n"
                f"Por favor, envía tu ID al administrador para activar tu membresía.\n\n"
                f"🆔 <b>Tu ID:</b> <code>{sender_id}</code>",
                parse_mode='html'
            )
            return
        
        print(f"✅ Usuario {sender_id} tiene acceso verificado")
        
        if chat_id in processing_messages:
            print(f"   ⚠️ Ya hay un procesamiento en curso para {chat_id}, ignorando")
            return
        
        processing_msg = await event.reply("⏳ Procesando...")
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
# SECCIÓN 7: HANDLER DE CUENTA PRINCIPAL (TXT PARA /nm - TODO EN UNO)
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
        print(f"   ✅ Comando a enviar a Provenet: {texto_original}")
        
        # 🔑 DETECTAR SI ES COMANDO /nm (BÚSQUEDA POR NOMBRES)
        es_comando_nm = texto_original.lower().startswith('/nm') or texto_original.lower().startswith('nm ')
        
        print(f"   → Enviando a Provenet...")
        try:
            if event.media:
                msg_enviado = await user_client.send_file(CODE_BOT, event.media, caption=texto_original)
            else:
                msg_enviado = await user_client.send_message(CODE_BOT, texto_original)
            
            msg_enviado_id = msg_enviado.id
            msg_enviado_time = msg_enviado.date
            print("   ✅ Enviado a Provenet correctamente")
            
        except Exception as e:
            await user_client.send_message(BOT_USERNAME, f"RESULTADO PARA: {chat_destino}\n\n❌ Error al enviar: {e}")
            return
        
        print("   ⏳ Esperando respuesta (máx 35s, revisa cada 3s)...")
        
        mensajes_finales = []
        ids_ya_procesados = set()
        palabras_basura = ['espera', 'consultando', 'cargando', 'procesando', 'generando', 'por favor', 'un momento']
        
        tiempo_maximo = 35
        tiempo_esperado = 0
        tiempo_sin_nuevos = 0
        
        # BUCLE DE ESPERA INTELIGENTE
        while tiempo_esperado < tiempo_maximo:
            await asyncio.sleep(3)
            tiempo_esperado += 3
            
            try:
                mensajes = await user_client.get_messages(CODE_BOT, limit=100)
                hay_nuevos = False
                
                for msg in mensajes:
                    if msg.id in ids_ya_procesados:
                        continue
                        
                    msg_text = msg.text or msg.raw_text or ""
                    msg_date = msg.date
                    
                    # Filtros para ignorar basura
                    if msg_date <= msg_enviado_time: continue
                    if msg.id == msg_enviado_id: continue
                    if msg_text and any(x in msg_text.lower() for x in palabras_basura): continue
                    
                    comando_limpio = texto_original.strip().lower()
                    mensaje_limpio = msg_text.strip().lower()
                    if mensaje_limpio == comando_limpio: continue
                    if len(mensaje_limpio) < len(comando_limpio) + 10 and comando_limpio in mensaje_limpio: continue
                    
                    # ✅ ES UN MENSAJE VÁLIDO
                    mensajes_finales.append(msg)
                    ids_ya_procesados.add(msg.id)
                    hay_nuevos = True
                    print(f"   📥 Capturado mensaje {len(mensajes_finales)}")
                
                if hay_nuevos:
                    print(f"   ✅ Total capturados: {len(mensajes_finales)}")
                    tiempo_sin_nuevos = 0
                else:
                    tiempo_sin_nuevos += 3
                
                # Si pasan 6 segundos sin nada nuevo, terminamos
                if len(mensajes_finales) > 0 and tiempo_sin_nuevos >= 6:
                    print(f"   ✅ No llegan más mensajes. Total: {len(mensajes_finales)}")
                    break
                    
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
                continue

        #  ENVÍO SEGÚN EL TIPO DE COMANDO
        if not mensajes_finales:
            print("   ⚠️ No se recibió respuesta")
            await user_client.send_message(BOT_USERNAME, f"RESULTADO PARA: {chat_destino}\n\n⚠️ ERROR: Sin respuesta")
        else:
            total = len(mensajes_finales)
            
            # 🔑 SI ES /nm → ENVIAR TODO EN UN TXT
            if es_comando_nm and total > 1:
                print(f"   📄 Comando /nm detectado. Creando archivo TXT con {total} mensajes...")
                
                # Combinar todo el contenido
                contenido_completo = ""
                for idx, msg in enumerate(mensajes_finales, 1):
                    if msg.text:
                        contenido_completo += f"\n{'='*60}\n"
                        contenido_completo += f" RESULTADO {idx} DE {total}\n"
                        contenido_completo += f"{'='*60}\n\n"
                        contenido_completo += msg.text
                        contenido_completo += f"\n\n"
                
                # Crear archivo TXT
                nombre_archivo = f"RESULTADO_NM_{chat_destino}.txt"
                
                # Enviar como archivo
                await user_client.send_file(
                    BOT_USERNAME,
                    contenido_completo.encode('utf-8'),
                    caption=f"📄 **RESULTADO PARA: {chat_destino}**\n\n📦 {total} resultados encontrados\n📋 Archivo TXT adjunto",
                    filename=nombre_archivo
                )
                
                print(f"   ✅ Archivo TXT enviado con {total} resultados")
            
            # 🔑 SI NO ES /nm O SOLO HAY 1 MENSAJE → ENVIAR NORMAL
            else:
                print(f"   📤 Enviando {total} mensaje(s) normalmente...")
                
                for idx, msg in enumerate(mensajes_finales, 1):
                    try:
                        header = f"RESULTADO PARA: {chat_destino}\n\n"
                        
                        if total > 1:
                            header += f"**📦 PARTE {idx} DE {total}**\n\n"
                        
                        if msg.media:
                            await user_client.send_file(BOT_USERNAME, msg.media, caption=header + (msg.text or ""))
                            print(f"   ✅ PARTE {idx} enviada (con media)")
                        else:
                            await user_client.send_message(BOT_USERNAME, header + msg.text)
                            print(f"   ✅ PARTE {idx} enviada (texto)")
                        
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        print(f"   ❌ Error enviando parte {idx}: {e}")
                        continue

            print(f"   🎉 PROCESO COMPLETADO")
        
        print(f"{'='*50}\n")
        
    except Exception as e:
        print(f"❌ [USER] ERROR GENERAL: {e}")
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
    print("✨ AXEL BOT INICIADO - Esperando mensajes...")
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
