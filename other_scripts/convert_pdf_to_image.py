from pdf2image import convert_from_path
import os

def convert_pdf_to_image(pdf_path, output_folder):
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'page_{i+1}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths

# Example usage
pdf_path = '/home/jmiguel-rai-control/Documents/slap127.pdf'
output_folder = '/home/jmiguel-rai-control/Documents'
image_paths = convert_pdf_to_image(pdf_path, output_folder)
print(f'Converted images: {image_paths}')
