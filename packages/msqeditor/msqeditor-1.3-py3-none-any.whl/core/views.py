import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
import mysql.connector
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        db_user = request.POST.get('dbuser')
        db_password = request.POST.get('dbpassword')

        if not db_user or not db_password:
            error = "Please provide both username and password."
            return render(request, 'login.html', {'error': error})

        # Save credentials in session
        request.session['db_user'] = db_user
        request.session['db_password'] = db_password

        print(f"Login attempt with user: {db_user}")  # or use logging module

        return redirect('das')

    return render(request, 'login.html')


def list_databases(request):
    db_user = request.session.get('db_user')
    db_password = request.session.get('db_password')

    if not db_user or not db_password:
        return JsonResponse({'error': 'Not authenticated'}, status=403)

    try:
        cnx = mysql.connector.connect(
            host='localhost',
            user=db_user,
            password=db_password
        )
        cursor = cnx.cursor()

        cursor.execute("SHOW DATABASES")
        all_dbs = [db[0] for db in cursor.fetchall()]

        db_sizes = {}
        for db in all_dbs:
            if db in ['information_schema', 'mysql', 'performance_schema', 'sys']:
                continue  # skip system databases
            cursor.execute(f"""
                SELECT 
                    table_schema AS db_name,
                    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb
                FROM information_schema.tables
                WHERE table_schema = %s
                GROUP BY table_schema
            """, (db,))
            result = cursor.fetchone()
            db_sizes[db] = result[1] if result else 0.0

        return render(request, "das.html", {
            'databases': db_sizes
        })

    except mysql.connector.Error as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


def get_tables(request, db_name):
    db_user = request.session.get('db_user')
    db_password = request.session.get('db_password')

    if not db_user or not db_password:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        cnx = mysql.connector.connect(
            host='localhost',
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = cnx.cursor()

        # Get table names
        cursor.execute("SHOW TABLES")
        table_names = [table[0] for table in cursor.fetchall()]

        tables_info = []
        for name in table_names:
            cursor.execute("""
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2)
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            """, (db_name, name))
            size_result = cursor.fetchone()
            size_mb = size_result[0] if size_result and size_result[0] else 0.0
            tables_info.append({'name': name, 'size_mb': size_mb})

        cursor.close()
        cnx.close()
        return JsonResponse({'tables': tables_info})

    except mysql.connector.Error as e:
        return JsonResponse({'error': str(e)}, status=400)



def get_table_data(request, db_name, table_name):
    db_user = request.session.get('db_user')
    db_password = request.session.get('db_password')

    if not db_user or not db_password:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        cnx = mysql.connector.connect(
            host='localhost',
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = cnx.cursor()
        cursor.execute(f"SELECT * FROM `{table_name}`")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()

        data = [dict(zip(columns, row)) for row in rows]

        return JsonResponse({'columns': columns, 'rows': data})
    except mysql.connector.Error as e:
        return JsonResponse({'error': str(e)}, status=400)
    
def update_table_row(request, db_name, table_name, pk):
    logger.info(f"Update request: db={db_name}, table={table_name}, pk={pk}, method={request.method}")

    if request.method != 'POST':
        logger.warning("Rejected: method not POST")
        return JsonResponse({'error': 'POST method required'}, status=405)

    db_user = request.session.get('db_user')
    db_password = request.session.get('db_password')
    if not db_user or not db_password:
        logger.warning("Rejected: not authenticated - missing db_user or db_password in session")
        return JsonResponse({'error': 'Not authenticated'}, status=403)

    try:
        data = json.loads(request.body)
        logger.debug(f"Received update data: {data}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not data:
        logger.warning("Rejected: no data provided")
        return JsonResponse({'error': 'No data provided'}, status=400)

    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(
            host='localhost',
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = cnx.cursor()

        set_clause = ", ".join(f"`{k}` = %s" for k in data.keys())
        values = list(data.values())
        values.append(pk)

        query = f"UPDATE `{table_name}` SET {set_clause} WHERE id = %s"
        logger.debug(f"Executing query: {query} with values {values}")

        cursor.execute(query, values)
        cnx.commit()
        logger.info("Update successful")
    except mysql.connector.Error as e:
        logger.error(f"MySQL error: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

    return JsonResponse({'success': True})


def create_table_row(request, db_name, table_name):
    logger.info(f"Create request: db={db_name}, table={table_name}, method={request.method}")

    if request.method != 'POST':
        logger.warning("Rejected: method not POST")
        return JsonResponse({'error': 'POST method required'}, status=405)

    db_user = request.session.get('db_user')
    db_password = request.session.get('db_password')
    if not db_user or not db_password:
        logger.warning("Rejected: not authenticated - missing db_user or db_password in session")
        return JsonResponse({'error': 'Not authenticated'}, status=403)

    try:
        data = json.loads(request.body)
        logger.debug(f"Received create data: {data}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not data:
        logger.warning("Rejected: no data provided")
        return JsonResponse({'error': 'No data provided'}, status=400)

    cnx = None
    cursor = None
    try:
        cnx = mysql.connector.connect(
            host='localhost',
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = cnx.cursor()

        columns = ", ".join(f"`{k}`" for k in data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        values = list(data.values())

        query = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
        logger.debug(f"Executing query: {query} with values {values}")

        cursor.execute(query, values)
        cnx.commit()
        last_id = cursor.lastrowid
        logger.info(f"Insert successful, new ID: {last_id}")

    except mysql.connector.Error as e:
        logger.error(f"MySQL error: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

    return JsonResponse({'success': True, 'last_insert_id': last_id})

def delete_table_row(request, db_name, table_name, row_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    db_user = request.session.get('db_user')
    db_password = request.session.get('db_password')

    if not db_user or not db_password:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        cnx = mysql.connector.connect(
            host='localhost',
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = cnx.cursor()
        
        # Use parameterized query to prevent SQL injection
        query = f"DELETE FROM `{table_name}` WHERE `id` = %s"
        cursor.execute(query, (row_id,))
        cnx.commit()
        
        cursor.close()
        cnx.close()

        return JsonResponse({'status': 'success', 'deleted_id': row_id})
    except mysql.connector.Error as e:
        return JsonResponse({'error': str(e)}, status=400)