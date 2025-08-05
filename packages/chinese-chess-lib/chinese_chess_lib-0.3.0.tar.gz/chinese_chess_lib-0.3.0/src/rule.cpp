#include "rule.h"

#include <set>
#include <algorithm>
#include "board.h"
#include "move.h"

std::vector<std::string> warn(Board& chesses, const std::string& color) {
    std::set<std::string> attackers;

    for (int y = 0; y < 10; ++y) {
        for (int x = 0; x < 9; ++x) {
            Chess* chess = chesses[y][x];
            if (!chess) continue;
            if (chess->color != color) continue;

            std::vector<Move> steps = get_legal_moves(chesses, chess);
            for (const auto& step : steps) {
                bool isCapture = std::get<0>(step);
                int dx = std::get<1>(step);
                int dy = std::get<2>(step);
                int tx = chess->x + dx;
                int ty = chess->y + dy;

                if (tx < 0 || tx >= 9 || ty < 0 || ty >= 10) continue;

                Chess* target = chesses[ty][tx];
                if (isCapture && target && (target->name == "j" || target->name == "J")) {
                    attackers.insert(chess->color);
                    break;
                }
            }
        }
    }

    // 转为vector返回
    return std::vector<std::string>(attackers.begin(), attackers.end());
}

std::optional<std::string> dead(Board& chesses, const std::string& color) {
    bool opponent_king_found = false;

    for (int y = 0; y < 10; ++y) {
        for (int x = 0; x < 9; ++x) {
            Chess* chess = chesses[y][x];
            if (!chess) continue;
            if (chess->color == color) continue;

            if (chess->name == "j" || chess->name == "J") {
                opponent_king_found = true;
            }

            auto steps = get_legal_moves(chesses, chess);
            for (const auto& step : steps) {
                if (virtual_move(chesses, chess, step, color).empty()) {
                    return std::nullopt;
                }
            }
        }
    }

    if (!opponent_king_found) {
        return color;
    }

    return color;
}
