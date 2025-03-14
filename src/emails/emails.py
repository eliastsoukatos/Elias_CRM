import sqlite3
import os
import datetime


def main():
    # Ruta de la base de datos
    db_path = "/Users/anthonyhurtado/Jobs/personal/others/Elias_CRM/databases/database.db"

    # Conectar a la base de datos
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return

    # Solicitar al usuario el/los campaign_batch_tag (pueden ser varios separados por coma)
    tags_input = input("Ingrese campaign_batch_tag(s) separados por coma: ")
    tags_list = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

    # Consultar la tabla 'contacts_campaign' para obtener los contact_id que tienen el tag indicado y estado 'approved'
    # Se asume que la tabla se llama 'contacts_campaign'
    placeholders = ','.join('?' for _ in tags_list)
    query = f"""
        SELECT contact_id FROM contacts_campaign
        WHERE campaign_batch_tag IN ({placeholders})
          AND current_state = 'approved'
    """
    try:
        cursor.execute(query, tags_list)
        contact_ids_result = cursor.fetchall()
        contact_ids = [row[0] for row in contact_ids_result]
    except Exception as e:
        print("Error al consultar la tabla contacts_campaign:", e)
        conn.close()
        return

    if not contact_ids:
        print("No se encontraron contactos con los tags y estado 'approved'.")
        conn.close()
        return

    # Eliminar duplicados, en caso de existir
    contact_ids = list(set(contact_ids))

    # Consultar la tabla 'contacts' para obtener los datos de los contactos correspondientes
    placeholders = ','.join('?' for _ in contact_ids)
    query_contacts = f"""
        SELECT contact_id, Email, Timezone FROM contacts
        WHERE contact_id IN ({placeholders})
    """
    try:
        cursor.execute(query_contacts, contact_ids)
        contacts = cursor.fetchall()
    except Exception as e:
        print("Error al consultar la tabla contacts:", e)
        conn.close()
        return

    if not contacts:
        print("No se encontraron contactos en la tabla contacts para los contact_id obtenidos.")
        conn.close()
        return

    # Extraer los timezones únicos de los contactos obtenidos
    timezones_set = set()
    for contact in contacts:
        tz = contact[2]  # Se asume que la columna Timezone es la tercera
        if tz:
            timezones_set.add(tz)
    unique_timezones = sorted(list(timezones_set))

    print("\nTimezones disponibles:")
    for tz in unique_timezones:
        print(" -", tz)

    # Solicitar al usuario que seleccione los timezones (o escribir 'todos')
    tz_input = input(
        "\nSeleccione timezones separados por coma o escriba 'todos' para seleccionar todos: ")
    if tz_input.lower() == 'todos':
        selected_timezones = unique_timezones
    else:
        selected_timezones = [tz.strip()
                              for tz in tz_input.split(",") if tz.strip()]

    # Filtrar los contactos según los timezones seleccionados
    filtered_contacts = [
        contact for contact in contacts if contact[2] in selected_timezones]

    if not filtered_contacts:
        print("No se encontraron contactos con los timezones seleccionados.")
        conn.close()
        return

    # Extraer los emails de los contactos filtrados (se eliminan duplicados)
    emails = list({contact[1] for contact in filtered_contacts if contact[1]})

    # Formatear los emails para que queden separados por "; "
    emails_str = "; ".join(emails) + ";"

    # Crear el archivo .txt en la ruta indicada
    output_dir = r"C:\Users\EliasTsoukatos\Documents\leads\Data_CRM_Elias\email_lists"
    os.makedirs(output_dir, exist_ok=True)
    # Usar timestamp en el nombre para evitar sobreescritura
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"email_list_{timestamp}.txt")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(emails_str)
        print("\nArchivo creado exitosamente en:", output_file)
    except Exception as e:
        print("Error al escribir el archivo:", e)

    conn.close()


if __name__ == "__main__":
    main()
