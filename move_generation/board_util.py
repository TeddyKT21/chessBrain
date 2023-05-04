from move_generation.short_board import board_size


def set_en_passant_state(short_board, colum):
    en_passant_flag = pow(2, 6 + colum)
    if short_board.state % (2 * en_passant_flag) < en_passant_flag:
        short_board.state = short_board.state + en_passant_flag


def remove_if_out_of_range(possible_locations_arr):
    k = 0
    while k <= len(possible_locations_arr) - 2:
        if possible_locations_arr[k] > board_size - 1 \
                or possible_locations_arr[k] < 0 \
                or possible_locations_arr[k + 1] > board_size - 1 \
                or possible_locations_arr[k + 1] < 0:
            del possible_locations_arr[k]
            del possible_locations_arr[k]
        else:
            k += 2


def update_castle_state(short_board, castle_scale):
    if short_board.state % (2 * castle_scale) >= castle_scale:
        short_board.state = short_board.state - castle_scale
