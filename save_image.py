import pymysql
import os

print("save_image.py 실행됨!", flush=True)
image_path = os.path.abspath("static/images/banner2.jpg")
print("이미지 경로:", image_path)

def save_image_to_db(image_path, image_name):
    conn = None
    cursor = None
    try:
        # MySQL 연결
        print("DB 연결 시도...", flush=True)
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='ugahan582818',
            database='ugamedical'
        )
        cursor = conn.cursor()
        print("DB 연결 성공", flush=True)

        # 이미지 파일 확인
        abs_path = os.path.abspath(image_path)
        print(f"이미지 절대 경로: {abs_path}", flush=True)

        # 이미지 파일을 바이너리 모드로 읽음
        with open(abs_path, 'rb') as file:
            binary_data = file.read()
            print(f"이미지 읽음: {len(binary_data)} bytes", flush=True)

        # SQL 쿼리 실행
        query = "INSERT INTO banner_images (image_name, image_data) VALUES (%s, %s)"
        cursor.execute(query, (image_name, binary_data))

        # 변경 사항 커밋
        conn.commit()

        print("Image saved successfully!", flush=True)

    except pymysql.Error as err:
        print(f"Database Error: {err}", flush=True)
    except FileNotFoundError as err:
        print(f"File Error: {err}", flush=True)
    except Exception as err:
        print(f"Unexpected Error: {err}", flush=True)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    image_path = "c:\\UGAMEDICAL\\static\\images\\banner2.jpg"
    image_name = "banner2"
    save_image_to_db(image_path, image_name)