import uuid
import os

from werkzeug.utils import secure_filename
from cloudinary.utils import cloudinary_url
from cloudinary.uploader import upload


def upload_images(files, foldername):
    uploaded_images = []

    if os.environ.get("FLASK_ENV") == "development":
        for file in files:
            code = str(uuid.uuid4()).replace("-", "")
            if not os.path.exists(f"../uploads/{foldername}"):
                os.makedirs(f"../uploads/{foldername}")

            image_filename = f"{code}{secure_filename(file.filename)}"
            upload_path = os.path.join(
                f"../uploads/{foldername}", image_filename)
            file.save(upload_path)

            uploaded_images.append({
                "image_url": os.path.abspath(upload_path),
                "image_id": image_filename
            })
    else:
        for file in files:
            code = str(uuid.uuid4()).replace("-", "")
            upload_result = upload(file, public_id=f"{code}{secure_filename(file.filename)}",
                                   overwrite=True,
                                   folder=foldername)

            public_id = upload_result['public_id']
            image_url, _ = cloudinary_url(public_id,
                                          format=upload_result['format'])

            uploaded_images.append({
                "image_url": image_url,
                "image_id": public_id
            })

    return uploaded_images
