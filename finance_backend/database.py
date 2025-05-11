import os
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "https://finance-manager-snowy.vercel.app/login"], supports_credentials=True)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "message": "No JSON data provided"}), 400

        add = data.get("add")

        if add == "insert":

            
            dlist = data.get("backlist")

            try:
                # Convert to correct types
                def convert_value(value, index):
                    # First two values (Month and Year) are Month=str, Year=int
                    if index == 0:
                        return str(value)  # Month
                    elif index == 1:
                        return int(value)  # Year
                    else:
                        try:
                            return int(value) if value != "" else None
                        except ValueError:
                            return None

                # Apply conversion
                ldata = tuple(convert_value(item["value"], idx) for idx, item in enumerate(dlist))

                sql = """
                    INSERT INTO businessdata (Month, Year, Workers, Revenue, Target, Lodging, Drinks, Hall_Renting, Orders, Expenses, Staff, Drinks_purch, Entertainment, Power, Web_Presence)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                print("🔌 Attempting to connect to MySQL...")
                connection = pymysql.connect(
                    host=os.environ.get('DB_HOST'),
                    port=int(os.environ.get('DB_PORT', 3306)),
                    user=os.environ.get('DB_USER'),
                    password=os.environ.get('DB_PASSWORD'),
                    database=os.environ.get('DB_NAME')
                )

                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(sql, ldata)
                    connection.commit()

                return jsonify({"success": True, "message": "Data inserted successfully"})

            except Exception as e:
                print("❌ Error inserting data:", str(e))
                return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500
        


        elif add == "Check":

            backlist = data.get('backlist', {})
            username = backlist.get('username')
            password = backlist.get('password')

            try:

                print("🔌 Attempting to connect to MySQL...")
                connection = pymysql.connect(
                    host=os.environ.get('DB_HOST'),
                    port=int(os.environ.get('DB_PORT', 3306)),
                    user=os.environ.get('DB_USER'),
                    password=os.environ.get('DB_PASSWORD'),
                    database=os.environ.get('DB_NAME'),
                    cursorclass=pymysql.cursors.DictCursor  # <== This is GOOD and works!
                )


                sql = "SELECT * FROM datalogin WHERE username = %s"
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(sql, (username,))  # Use parameterized queries to avoid SQL injection
                        result = cursor.fetchone()  # Get the first row (if any)
                        
                        if result:
                            if check_password_hash(result['password'], password):
                                return jsonify({"success": True, "message": "Login successful"})
                            else:
                                return jsonify({"success": False, "message": "Invalid password"})
                        else:
                            return jsonify({"success": False, "message": "User not found"})
            except Exception as e:
                print("❌ Error inserting data:", str(e))
                return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500
        

        
        elif add == "Delete":
            record_id = data.get('backlist')  # Consider renaming 'backlist' to 'record_id'

            try:
                print("🔌 Attempting to connect to MySQL...")
                connection = pymysql.connect(
                    host=os.environ.get('DB_HOST'),
                    port=int(os.environ.get('DB_PORT', 3306)),
                    user=os.environ.get('DB_USER'),
                    password=os.environ.get('DB_PASSWORD'),
                    database=os.environ.get('DB_NAME')
                )

                sql = "DELETE FROM businessdata WHERE id = %s"
                with connection:
                    with connection.cursor() as cursor:
                        cursor.execute(sql, (record_id,))
                    connection.commit()  # Commit the deletion

                return jsonify({"success": True, "message": "Record deleted"}), 200

            except Exception as e:
                print("❌ Error deleting data:", str(e))
                return jsonify({"success": False, "message": "Database error", "error": str(e)}), 500

        else:
            return jsonify({"success": False, "message": "Invalid operation"}), 400

    return jsonify({"message": "Hello, send a POST request!"})




@app.route('/get_data', methods=["GET", "POST"])
def get_data():
    if request.method == "GET":
        sql = "SELECT * FROM Businessdata ORDER BY Year DESC, Month DESC LIMIT 12"


        try:
            print("🔌 Attempting to connect to MySQL...")
            connection = pymysql.connect(
                host=os.environ.get('DB_HOST'),
                port=int(os.environ.get('DB_PORT', 3306)),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                database=os.environ.get('DB_NAME'),
                cursorclass=pymysql.cursors.DictCursor  # <== This is GOOD and works!
            )


            with connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    result = cursor.fetchall()

            return jsonify({"success": True, "data": result})

        except Exception as e:
            return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

    else:
        return jsonify({"success": False, "message": "Invalid operation"}), 400


if __name__ == "__main__":
    app.run(debug=True)
