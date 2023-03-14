from converters import byte_piece_to_index_dict, color_bit_dict

directions_array = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]]


def get_attacking_squares(byte_board, i, j, color_bit):
    attacking_squares = [[0], []]
    for h in [-1, 0, 1]:  # this loop checks for king, queen, rooks,and bishops
        for w in [-1, 0, 1]:
            if w == 0 and h == 0:
                continue
            found_squares = get_attacking_squares_direction(byte_board, (h, w), (i, j), color_bit)
            if found_squares is not None:
                attacking_squares[0][0] += 1
                attacking_squares[1] += found_squares

    attacking_knight_squares = check_for_knight_squares(byte_board, i, j, color_bit)
    if attacking_knight_squares is not None:
        attacking_squares[0][0] += 1
        attacking_squares[1] += attacking_knight_squares

    attacking_pawn_squares = check_for_pawn_squares(byte_board, i, j, color_bit)
    if attacking_pawn_squares is not None:
        attacking_squares[0][0] += 1
        attacking_squares[1] += attacking_pawn_squares

    return None if attacking_squares[0][0] == 0 else attacking_squares


def get_attacking_squares_direction(byte_board, offset_tuple, location_tuple, color_bit):
    height_offset = offset_tuple[0]
    width_offset = offset_tuple[1]
    i = location_tuple[0] + height_offset
    j = location_tuple[1] + width_offset
    if abs(height_offset) == abs(width_offset):  # diagonals
        return check_for_attacking_squares(byte_board, color_bit, height_offset, width_offset, i, j, 3, 5)
    else:
        return check_for_attacking_squares(byte_board, color_bit, height_offset, width_offset, i, j, 4, 5)


def check_for_attacking_squares(byte_board, color_bit, height_offset, width_offset, i, j, *pieces):
    count = 1
    while 0 <= i <= 7 and 0 <= j <= 7:
        piece = byte_board.byte_array[i, j]
        piece_index = byte_piece_to_index_dict[piece]
        if piece_index != 0:
            if color_bit_dict[piece] != color_bit or piece_index not in pieces:
                break
            if piece_index in pieces and color_bit_dict[piece] == color_bit:
                found_squares = []
                for k in range(count):
                    found_squares.append(i - k * height_offset)
                    found_squares.append(j - k * width_offset)
                return found_squares
        i += height_offset
        j += width_offset
        count += 1
    return None


def check_for_knight_squares(byte_board, i, j, color_bit):
    possible_locations = [i + 1, j + 2,
                          i + 1, j - 2,
                          i + 2, j - 1,
                          i + 2, j + 1,
                          i - 1, j + 2,
                          i - 1, j - 2,
                          i - 2, j + 1,
                          i - 2, j - 1]
    actual_locations = []
    remove_if_out_of_range(possible_locations)
    for k in range(0, len(possible_locations), 2):
        piece = byte_board.byte_array[possible_locations[k], possible_locations[k + 1]]
        piece_index = byte_piece_to_index_dict[piece]
        if piece_index == 2 and color_bit_dict[piece] == color_bit:
            actual_locations += [possible_locations[k], possible_locations[k + 1]]

    return None if len(actual_locations) == 0 else actual_locations


def check_for_pawn_squares(byte_board, i, j, color_bit):
    direction = -1 if color_bit == 1 else 1
    possible_locations = [i - direction, j + 1, i - direction, j - 1]
    actual_locations = []
    remove_if_out_of_range(possible_locations)
    if len(possible_locations) == 0:
        return None
    for k in range(0, len(possible_locations), 2):
        piece = byte_board.byte_array[possible_locations[k], possible_locations[k + 1]]
        piece_index = byte_piece_to_index_dict[piece]
        if piece_index == 1 and color_bit_dict[piece] == color_bit:  # pawn
            actual_locations += [possible_locations[k], possible_locations[k + 1]]

    return None if len(actual_locations) == 0 else actual_locations


def remove_if_out_of_range(possible_locations_arr):
    k = 0
    while k <= len(possible_locations_arr) - 2:
        if possible_locations_arr[k] > 7 \
                or possible_locations_arr[k] < 0 \
                or possible_locations_arr[k + 1] > 7 \
                or possible_locations_arr[k + 1] < 0:
            del possible_locations_arr[k]
            del possible_locations_arr[k]
        else:
            k += 2
