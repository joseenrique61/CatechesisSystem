import os
from uuid import uuid4
from flask import current_app
from werkzeug.datastructures import FileStorage

def upload_image(image: FileStorage) -> str:
    """
    Uploads an image file to the server and returns the file path.
    """

    # Generate a unique filename using UUID
    filename = f"{uuid4()}.{image.filename.split('.')[-1]}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
        os.makedirs(current_app.config['UPLOAD_FOLDER'])

    image.save(file_path)

    return filename

def delete_image(filename: str) -> bool:
    """
    Deletes an image file from the server.
    """
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        print(f"The file {file_path} does not exist.")
        return False
    except:
        print(f"Error deleting the file {file_path}.")
        return False