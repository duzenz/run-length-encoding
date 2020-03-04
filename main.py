import argparse
import RLE
from PIL import Image
from Detail import Detail


def encode_image(path, scan_type):
    image = Image.open(path)
    original_image = list(image.getdata(0))
    encoded_image = RLE.encode_image(original_image, image.size[0], image.size[1], image.mode, scan_type)
    temp_image = Detail(encoded_image, 1, image.size[0], image.size[1], image.mode, scan_type, image.getpalette())
    compression_size, file_path = RLE.save_compressed_to_a_file(temp_image, path, scan_type)
    print("Encoded file saved to: " + file_path)


def decode_image(path):
    compressed_image = RLE.open_file_to_compressed(path)
    decoded_image = RLE.decode_image(compressed_image.compressed, compressed_image.width, compressed_image.height,
                                     compressed_image.mode, compressed_image.scanning)
    new_image = Image.new(compressed_image.mode, (compressed_image.width, compressed_image.height))
    new_image.putdata(decoded_image)
    if compressed_image.mode == 'P':
        new_image.putpalette(compressed_image.palette)
    new_file_path = path[:len(path) - 9] + "-copy." + path.partition(".")[2].partition(".")[0]
    new_image.save(new_file_path)
    print("Decoded file saved to: " + new_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RLE Encoder.')
    parser.add_argument('-e', '--encode', help='Image to encode.')
    parser.add_argument('-d', '--decode', help='Compressed file to decode.')
    parser.add_argument('-s', '--scanning', help='Works if encoding is set. Can be R, RR, ZZ, C, CR.')

    args = parser.parse_args()

    if not (args.encode or args.decode):
        parser.error('No action requested, add -e or -d')

    args = vars(args)

    if args['encode'] is not None and args['scanning'] is not None:
        scan = args['scanning']

        if scan not in ['R', 'RR', 'ZZ', 'C', 'CR']:
            scan = 'R'
        encode_image(args['encode'], scan)
    elif args['decode'] is not None:
        decode_image(args['decode'])
    else:
        print('Enter arguments correctly')
