import os
import pickle


def encode_image(image_pixels, width, height, image_type, scanning="C"):
    converted_image_pixels = _convert_encode_scanning(list(image_pixels), width, height, scanning)
    if image_type == '1':
        return _encode_image_bw(converted_image_pixels)
    elif image_type == 'P':
        return _encode_image_4bit(converted_image_pixels)
    else:
        return _encode_image_8bit(converted_image_pixels)


def _encode_image_8bit(image_pixels):
    encoded_image = bytearray()

    count = 0

    prev = image_pixels[0]
    temp_map = ""

    for pixel in image_pixels:
        if count >= 255:
            encoded_image.append(255)
            encoded_image.append(prev)
            temp_map += "1"
            temp_map += "0"
            count = 0
            prev = pixel

        if pixel == prev:
            count += 1
        else:
            if count > 1:
                encoded_image.append(count)
                temp_map += "1"
            encoded_image.append(prev)
            temp_map += "0"
            count = 1
            prev = pixel

    if count > 1:
        encoded_image.append(count)
        temp_map += "1"

    encoded_image.append(prev)
    temp_map += "0"

    encoded_image.extend([0] * _remaining(len(encoded_image)))
    temp_map += "1" * _remaining(len(temp_map))

    encoded_image = _set_8bit_map(temp_map, encoded_image)

    return encoded_image


def decode_image(encoded_image, width, height, image_type, scanning="C"):
    if image_type == '1':
        new_encoded_image = _decode_image_black_white(list(encoded_image))
    elif image_type == 'P':
        new_encoded_image = _decode_image_4bit(list(encoded_image))
    else:
        new_encoded_image = _decode_image_8bit(list(encoded_image))

    return _convert_decode_scanning(new_encoded_image, width, height, scanning)


def _decode_image_8bit(encoded_image):
    decoded_image = []

    image_map, encrypted_image = _get_8bit_map(encoded_image)

    for index, i in enumerate(image_map):
        if i == '1' and encrypted_image[index] == 0:
            break

        if i == '1':
            decoded_image.extend([encrypted_image[index + 1]] * encrypted_image[index])
        elif image_map[index - 1] != '1' or index == 0:
            decoded_image.append(encrypted_image[index])

    return decoded_image


def _encode_image_bw(image_pixels):
    encoded_image = bytearray()

    count = 0

    prev = 255

    for pixel in image_pixels:
        if count >= 255:
            encoded_image.append(255)
            encoded_image.append(0)
            count = 0

        if pixel == prev:
            count += 1
        else:
            encoded_image.append(count)
            count = 1
            prev = pixel

    encoded_image.append(count)

    return encoded_image


def _decode_image_black_white(encoded_image):
    decoded_image = []

    for index, count in enumerate(encoded_image):
        pixel = 0
        if index % 2 == 0:
            pixel = 255
        decoded_image += [pixel] * count

    return decoded_image


def _get_8bit_map(encoded_image):
    image_map = ""
    new_encoded_image = list(encoded_image)

    temp = range(0, len(new_encoded_image), 9)

    for i in temp:
        image_map += '{0:08b}'.format(new_encoded_image[i])

    for i in sorted(list(temp), reverse=True):
        del new_encoded_image[i]

    return image_map, new_encoded_image


def _set_8bit_map(image_map, encoded_image):
    new_image_map = _divide_by_row(image_map, 8)
    temp_image = _divide_by_row(list(encoded_image), 8)
    return bytearray(_flatten_list_of_list(_merge_map(temp_image, new_image_map)))


def _divide_by_row(flat, size):
    return [flat[i:i + size] for i in range(0, len(flat), size)]


def _divide_by_column(flat, size):
    return [[row[i] for row in flat] for i in range(size)]


def _flatten_list_of_list(flat):
    return [item for sublist in flat for item in sublist]


def _single_row_to_continuous_row(flat):
    return [i if index % 2 == 0 else list(reversed(i)) for index, i in enumerate(flat)]


def _remaining(x, y=8):
    return 0 if x % y == 0 else y - (x % y)


def _merge_map(z, x):
    return [[int(x[index], 2)] + i for index, i in enumerate(z)]


def _divide_zig_zag(flat, width, height):
    return [flat[i] for i in _get_zig_zag_index(width, height)]


def _get_parts(a, b):
    return _flatten_list_of_list([[int(a / b)] * (b - 1), [int(a / b) + a % b]])


def _get_index(a, b):
    return [(int(x / a), x % a) for x in list(range(0, a * b))]


def _get_zig_zag_index(coord_x, coord_y):
    zig_zag_index = []
    for a in sorted(
            (p % coord_x + int(p / coord_x), (p % coord_x, int(p / coord_x))[(p % coord_x - int(p / coord_x)) % 2], p)
            for p in range(coord_x * coord_y)):
        zig_zag_index.append(a[2])

    return zig_zag_index


def save_compressed_to_a_file(img, filename):
    compressed_file = open(filename + ".comp", "wb")
    pickle.dump(img, compressed_file)
    compressed_path = os.path.abspath(filename + ".comp")
    stat_info = os.stat(filename + ".comp")
    return stat_info.st_size, compressed_path


def open_file_to_compressed(path):
    compressed_file = open(path, "rb")
    return pickle.load(compressed_file)


def _convert_encode_scanning(img, width, height, scanning="C"):
    if scanning == "RR":
        return _flatten_list_of_list(_single_row_to_continuous_row(_divide_by_row(img, width)))
    elif scanning == "R":
        return _flatten_list_of_list(_divide_by_row(img, width))
    elif scanning == "C":
        return _flatten_list_of_list(_divide_by_column(_divide_by_row(img, width), width))
    elif scanning == "CR":
        return _flatten_list_of_list(
            _single_row_to_continuous_row(_divide_by_column(_divide_by_row(img, width), width)))
    else:
        return [img[i] for i in _get_zig_zag_index(width, height)]


def _convert_decode_scanning(img, width, height, scanning="C"):
    if scanning == "ZZ":
        lst = [0] * width * height

        new_index = _get_zig_zag_index(width, height)

        for index in range(0, width * height):
            lst[new_index[index]] = img[index]

        return lst
    elif scanning == "CR":
        return _flatten_list_of_list(
            _divide_by_column(_single_row_to_continuous_row(_divide_by_row(img, height)), height))
    elif scanning == "C":
        return _flatten_list_of_list(_divide_by_column(_divide_by_row(img, height), height))
    else:
        return _convert_encode_scanning(img, width, height, scanning)


def _generate_zig_zag_index(x, y):
    list_x = x[:]
    list_y = y[:]
    list_x.insert(0, 0)
    list_y.insert(0, 0)

    result_list = []

    for i in range(1, len(list_y)):
        for k in range(1, len(list_x)):
            result_list.append([sum(list_x[:k]), sum(list_x[:k + 1]), sum(list_y[:i]), sum(list_y[:i + 1])])

    return result_list


def _split_8bit_to_4bit(eight_bit):
    left_mask = 240
    right_mask = 15
    left = (eight_bit & left_mask) >> 4
    right = eight_bit & right_mask

    return left, right


def _merge_4bit_to_8bit(left, right):
    return (left << 4) | right


def _encode_image_4bit(image_pixels):
    encoded_image = bytearray()

    count = 0

    prev = image_pixels[0]
    temp_map = ""

    for pixel in image_pixels:
        if count >= 15:
            encoded_image.append(15)
            encoded_image.append(prev)
            temp_map += "1"
            temp_map += "0"
            count = 0
            prev = pixel

        if pixel == prev:
            count += 1
        else:
            if count > 1:
                encoded_image.append(count)
                temp_map += "1"
            encoded_image.append(prev)
            temp_map += "0"
            count = 1
            prev = pixel

    if count > 1:
        encoded_image.append(count)
        temp_map += "1"

    encoded_image.append(prev)
    temp_map += "0"

    encoded_image.extend([0] * _remaining(len(encoded_image)))
    temp_map += "1" * _remaining(len(temp_map))

    encoded_image = _set_4bit_map(temp_map, encoded_image)

    return encoded_image


def _set_4bit_map(image_map, encoded_image):
    new_image_map = _divide_by_row(image_map, 8)

    temp_image = [_merge_4bit_to_8bit(encoded_image[i], encoded_image[i + 1]) for i in range(0, len(encoded_image), 2)]
    temp_image = _divide_by_row(list(temp_image), 4)

    return bytearray(_flatten_list_of_list(_merge_map(temp_image, new_image_map)))


def _decode_image_4bit(encoded_image):
    decoded_image = []

    image_map, encrypted_image = _get_4bit_map(encoded_image)

    for index, i in enumerate(image_map):
        if i == '1' and encrypted_image[index] == 0:
            break

        if i == '1':
            decoded_image.extend([encrypted_image[index + 1]] * encrypted_image[index])
        elif image_map[index - 1] != '1' or index == 0:
            decoded_image.append(encrypted_image[index])

    return decoded_image


def _get_4bit_map(encoded_image):
    image_map = ""

    new_encoded_image = list(encoded_image)

    temp = range(0, len(new_encoded_image), 5)

    for i in temp:
        image_map += '{0:08b}'.format(new_encoded_image[i])

    for i in sorted(list(temp), reverse=True):
        del new_encoded_image[i]

    new_encoded_image = _flatten_list_of_list([_split_8bit_to_4bit(i) for i in new_encoded_image])

    return image_map, new_encoded_image
