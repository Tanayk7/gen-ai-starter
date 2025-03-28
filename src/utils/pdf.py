import os
import pathlib
import urllib.request
import pypdfium2 as pdfium
import uuid

# Downloads a PDF from a url and saves pdf along with images of each page.
def download_and_save_pdf(url): 
    file_id = str(uuid.uuid4())
    print("file id; ", file_id)

    # extracting artwork_example.pdf from the above url. 
    pdf_dir = './pdfs'
    images_path = f"{pdf_dir}/images/{file_id}"

    # creating pdf saving dir. <-- refactor this. 
    pathlib.Path(pdf_dir).mkdir(parents=True, exist_ok=True)
    pdf_returned = urllib.request.urlretrieve(url, f'{pdf_dir}/{file_id}.pdf')

    # file is being downloaded here and stored in the defined dir. 
    if pdf_returned:
        print(f'Pdf file is downloaded in {pdf_dir}!')
        # save pdf to file 
        pdf = pdfium.PdfDocument(f"{pdf_dir}/{file_id}.pdf")
        # creating image saving dir. <-- refactor this. 
        pathlib.Path(images_path).mkdir(parents=True, exist_ok=True)

        # looping over pdf pages and saving jpgs.
        for i in range(len(pdf)):
            page = pdf[i]
            image = page.render(scale=4).to_pil()
            image.save(f"{images_path}/{file_id}_{i}.jpg")

    return [f"{images_path}/{item}" for item in os.listdir(images_path)], file_id
