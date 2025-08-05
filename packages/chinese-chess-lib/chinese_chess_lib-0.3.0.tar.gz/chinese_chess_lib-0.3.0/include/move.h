#pragma once

#include <vector>

#include "board.h"

std::vector<std::string> virtual_move(Board& chesses, Chess* chess, const Move& step, const std::string color);

std::vector<Move> get_legal_moves(Board& board, Chess* chess, bool flag_ = false);
